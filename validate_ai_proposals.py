"""
validate_ai_proposals.py  -  "AI proposes, code validates" + SLA drift check

The AI Chat reader (AWS Quick schedule) never writes the Priority tab. It writes a
PROPOSAL on the matching Test_Queue_Master row:
    AI_Proposal       ACK_PROVISION | DONE_PROVISION | ACK_CEASE | DONE_CEASE | NEEDS_REVIEW: <why>
    AI_Matched_ICCID  ICCID mentioned in the reply (blank if none)
    AI_Confidence     0.0 - 1.0
    AI_Source         "YYYY-MM-DD HH:MM | <short reply text>"

This script checks every new proposal before anything changes:
    1. permitted action, and a valid transition from the row's recorded state
    2. ICCID in the reply matches the ICCID assigned to the row
    3. the SIM is not RESERVED / ON_HOLD / DO_NOT_USE
    4. confidence >= AI_CONFIDENCE_THRESHOLD
    5. the target Priority cell (G provisioning / H cease) is empty - never overwrite
Accepted DONE -> writes "Done" to Priority G/H (the nightly run then promotes the row).
Accepted ACK  -> records Ack_Time.  Anything else -> Validation_Result explains why, nothing applied.

SLA drift check (recomputed from the sheet every run, no timers):
    LATE_ACK   no acknowledgement SLA_ACK_HOURS after the request      (default 2)
    LATE_DONE  not completed SLA_DONE_HOURS after the request          (default 24)
    LATE_TEST  not tested SLA_TEST_HOURS after the effective date ends  (default 24)
Late rows get ONE grouped reminder per day in the NRT Chat space.

Usage:
    python validate_ai_proposals.py                 # dry run: prints what would change
    python validate_ai_proposals.py --apply         # writes to the sheet, posts reminders
    python validate_ai_proposals.py --sheet-id <id> # e.g. test on the mockup sheet
Env: NRT_SHEET_ID, AI_CONFIDENCE_THRESHOLD, SLA_ACK_HOURS, SLA_DONE_HOURS, SLA_TEST_HOURS,
     PROVISIONING_WEBHOOK_URL (reminders), REVIEW_WEBHOOK_URL (optional), NO_CHAT=1 (log only)
"""
import os, re, sys, argparse, logging, hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import gspread
from gspread.cell import Cell
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("validator")

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo(os.getenv("NRT_TZ", "America/Denver"))
SHEET_ID = os.getenv("NRT_SHEET_ID", "1aTK5U16BNNlm41djfyqrcjlHkeutTQot3EJfQ0_upqI")
CONF_MIN = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.8"))
ACK_H = float(os.getenv("SLA_ACK_HOURS", "2"))
DONE_H = float(os.getenv("SLA_DONE_HOURS", "24"))
TEST_H = float(os.getenv("SLA_TEST_HOURS", "24"))

QUEUE_TAB = "Test_Queue_Master"
PRIORITY_TAB_CANDIDATES = ["Priority Test numbers with effective dates", "Priority Test Numbers"]
SIM_TAB = "SIM_Cards_Inventory"
NEW_COLS = ["Requested_At", "Ack_Time", "Done_Time", "AI_Proposal", "AI_Matched_ICCID",
            "AI_Confidence", "AI_Source", "Validation_Result", "SLA_Status"]

ACTIONS = {"ACK_PROVISION", "DONE_PROVISION", "ACK_CEASE", "DONE_CEASE", "NEEDS_REVIEW"}
RESERVED = {"RESERVED", "ON_HOLD", "HOLD", "DO_NOT_USE"}
PROV_PENDING = {"WAITING_PROVISIONING", "PROVISION_REQUESTED", "PROVISIONING_REQUESTED", "PENDING", "WAITING"}
CEASE_PENDING = {"CEASE_REQUESTED", "CEASE_PENDING"}
TESTED = {"PASSED", "FAILED", "CEASED", "CEASE_REQUESTED", "CEASE_PENDING"}
SKIP_ROWS = {"SKIPPED", "SKIPPED_ALREADY_TESTED"}


def now():
    return datetime.now(TZ)


def digits(s):
    return re.sub(r"\D", "", str(s or ""))


def parse_dt(s):
    s = str(s or "").strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2}))?", s) or re.match(r"(\d{1,2}/\d{1,2}/\d{2,4})(?:\s+(\d{1,2}:\d{2}))?", s)
    if not m:
        return None
    d, tm = m.group(1), m.group(2) or "00:00"
    for fmt in ("%Y-%m-%d %H:%M", "%m/%d/%Y %H:%M", "%m/%d/%y %H:%M"):
        try:
            return datetime.strptime(f"{d} {tm}", fmt).replace(tzinfo=TZ)
        except ValueError:
            continue
    return None


def stamp(dt=None):
    return (dt or now()).strftime("%Y-%m-%d %H:%M")


def client():
    tok = os.path.join(BASE, "token.json")
    cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", os.path.join(BASE, "credentials.json"))
    if os.path.exists(tok):
        return gspread.oauth(credentials_filename=cred, authorized_user_filename=tok)
    return gspread.service_account(filename=cred)


def post_chat(text, url_env, apply):
    url = os.getenv(url_env, "")
    if not apply or os.getenv("NO_CHAT") == "1" or not url:
        log.info(f"[chat:{url_env}] (not posted) {text}")
        return
    import requests
    try:
        requests.post(url, json={"text": text}, timeout=20).raise_for_status()
    except Exception as e:
        log.warning(f"Chat post failed: {e}")


def header_index(rows, must="iccid", scan=10):
    for i, r in enumerate(rows[:scan]):
        if any(must in str(c).lower() for c in r):
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sheet-id", default=SHEET_ID)
    a = ap.parse_args()
    mode = "APPLY" if a.apply else "DRY RUN"
    log.info(f"Validator start ({mode}) sheet={a.sheet_id} conf>={CONF_MIN} ack={ACK_H}h done={DONE_H}h test={TEST_H}h")

    wb = client().open_by_key(a.sheet_id)
    qws = wb.worksheet(QUEUE_TAB)
    pws = None
    for t in PRIORITY_TAB_CANDIDATES:
        try:
            pws = wb.worksheet(t); break
        except Exception:
            continue
    if pws is None:
        sys.exit("Priority tab not found")
    sws = wb.worksheet(SIM_TAB)

    # ---------- queue headers (add the new columns once) ----------
    q = qws.get_all_values()
    hdr = q[0] if q else []
    missing = [c for c in NEW_COLS if c not in hdr]
    if missing:
        log.info(f"Adding columns to {QUEUE_TAB}: {missing}")
        if a.apply:
            need = len(hdr) + len(missing)
            if qws.col_count < need:
                qws.add_cols(need - qws.col_count)
            qws.update_cells([Cell(1, len(hdr) + i + 1, c) for i, c in enumerate(missing)])
        hdr = hdr + missing
    H = {h.strip().lower(): i for i, h in enumerate(hdr)}

    def qi(*names):
        for n in names:
            for h, i in H.items():
                if n in h:
                    return i
        return None
    c_date, c_phone, c_iccid = qi("date"), qi("phone"), qi("iccid")
    c_prov, c_exec = qi("provisioning_status"), qi("test_execution_status")
    C = {n: H[n.lower()] for n in NEW_COLS}

    # ---------- Priority index ----------
    p = pws.get_all_values()
    ph = header_index(p)
    phd = [x.strip().lower() for x in p[ph]]
    def pcol(*keys):
        return next((i for i, h in enumerate(phd) if any(k in h for k in keys)), None)
    p_phone, p_iccid = pcol("arnold", "internal test", "test number", "phone"), pcol("iccid")
    p_prov, p_cease = pcol("provisioning status"), pcol("cease status")
    pmap = {}
    for r_i, r in enumerate(p[ph + 1:], start=ph + 2):
        k = digits(r[p_phone] if p_phone is not None and p_phone < len(r) else "")[-10:]
        if k:
            pmap.setdefault(k, []).append((r_i, r))

    def prow(phone, iccid):
        cands = pmap.get(digits(phone)[-10:], [])
        for r_i, r in reversed(cands):
            if digits(iccid) and p_iccid is not None and p_iccid < len(r) and digits(r[p_iccid]) == digits(iccid):
                return r_i, r
        return cands[-1] if cands else (None, None)

    # ---------- SIM states ----------
    sims = sws.get_all_values()
    sh = [x.strip().lower() for x in sims[0]] if sims else []
    si, ss = sh.index("iccid") if "iccid" in sh else 0, sh.index("state") if "state" in sh else 2
    sim_state = {digits(r[si]): str(r[ss]).strip().upper() for r in sims[1:] if len(r) > max(si, ss)}

    q_updates, p_updates, review, late, late_test = [], [], [], [], []
    t = now(); today = t.strftime("%Y-%m-%d")

    for r_i, row in enumerate(q[1:], start=2):
        row = row + [""] * (len(hdr) - len(row))
        g = lambda c: str(row[c]).strip() if c is not None else ""
        phone, iccid = g(c_phone), g(c_iccid)
        prov, exe = g(c_prov).upper(), g(c_exec).upper()
        if not phone or exe in SKIP_ROWS or prov in SKIP_ROWS:
            continue
        pr_i, pr = prow(phone, iccid)
        pv = lambda c: (str(pr[c]).strip() if pr is not None and c is not None and c < len(pr) else "")
        prov_done = pv(p_prov).lower() == "done"
        cease_done = pv(p_cease).lower() == "done"
        prov_pending = (prov in PROV_PENDING or exe in PROV_PENDING) and not prov_done
        cease_pending = (prov in CEASE_PENDING or exe in CEASE_PENDING) and not cease_done
        pending = prov_pending or cease_pending
        setq = lambda name, val: q_updates.append(Cell(r_i, C[name] + 1, val))

        # stamp the request time the first time a row is seen waiting
        req_at = parse_dt(g(C["Requested_At"]))
        if pending and not req_at:
            req_at = t; setq("Requested_At", stamp(t))
        ack_at = parse_dt(g(C["Ack_Time"]))

        # ---------- validate a new AI proposal ----------
        prop = g(C["AI_Proposal"]); src = g(C["AI_Source"])
        if prop:
            key = hashlib.md5(f"{prop}|{src}".encode()).hexdigest()[:8]
            if f"[{key}]" not in g(C["Validation_Result"]):
                action = prop.split(":")[0].strip().upper()
                m_iccid = g(C["AI_Matched_ICCID"])
                try:
                    conf = float(g(C["AI_Confidence"]) or 0)
                except ValueError:
                    conf = 0.0
                src_dt = parse_dt(src) or t
                reason = None
                if action not in ACTIONS:
                    reason = f"unknown action '{action}'"
                elif action == "NEEDS_REVIEW":
                    reason = "AI flagged: " + prop.split(":", 1)[-1].strip()
                elif action.endswith("PROVISION") and not prov_pending:
                    reason = f"not a valid transition: no provisioning request pending (status {prov or exe or 'blank'})"
                elif action.endswith("CEASE") and not cease_pending:
                    reason = f"not a valid transition: no release request pending (status {prov or exe or 'blank'})"
                elif sim_state.get(digits(iccid), "") in RESERVED:
                    reason = f"SIM {iccid} is {sim_state.get(digits(iccid))} - excluded from every transition"
                elif digits(m_iccid) and digits(m_iccid) != digits(iccid):
                    reason = f"ICCID in reply ({m_iccid}) does not match assigned ICCID ({iccid})"
                elif conf < CONF_MIN:
                    reason = f"confidence {conf:.2f} below threshold {CONF_MIN:.2f}"
                elif action.startswith("DONE") and pr_i is None:
                    reason = "no matching row on the Priority tab"

                if reason is None and action.startswith("DONE"):
                    col = p_prov if action == "DONE_PROVISION" else p_cease
                    cur = pv(col)
                    if cur and cur.lower() != "done":
                        reason = f"Priority cell already holds '{cur}' - not overwritten"
                    elif not cur:
                        p_updates.append(Cell(pr_i, col + 1, "Done"))
                    setq("Done_Time", stamp(src_dt))
                    if not ack_at:
                        setq("Ack_Time", stamp(src_dt))
                    result = f"APPLIED {action}"
                    if action == "DONE_PROVISION":   # reset the clock for the later release request
                        setq("Requested_At", "")
                        pending = False
                elif reason is None:  # ACK
                    if not ack_at:
                        setq("Ack_Time", stamp(src_dt)); ack_at = src_dt
                    result = f"ACK recorded ({action})"
                if reason:
                    result = ("NEEDS_REVIEW: " if action == "NEEDS_REVIEW" else "REJECTED: ") + reason
                    review.append(f"• {phone} ({iccid}): {result}  | reply: {src[:120]}")
                setq("Validation_Result", f"{stamp(t)} [{key}] {result}")
                log.info(f"Row {r_i} {phone}: {action} -> {result}")

        # ---------- SLA drift check ----------
        parts = []
        if pending and req_at:
            age = (t - req_at).total_seconds() / 3600
            if not ack_at and age > ACK_H:
                parts.append(f"LATE_ACK {age:.0f}h")
            if age > DONE_H:
                parts.append(f"LATE_DONE {age:.0f}h")
        eff = parse_dt(g(c_date))
        if eff and exe not in TESTED and prov not in TESTED:
            deadline = eff.replace(hour=0, minute=0) + timedelta(days=1, hours=TEST_H)
            if t > deadline:
                parts.append(f"LATE_TEST {(t - deadline).total_seconds() / 3600:.0f}h past")
        prev = g(C["SLA_Status"])
        m = re.search(r"reminded (\d{4}-\d{2}-\d{2})", prev)
        reminded = m.group(1) if m else ""
        status = ", ".join(parts) if parts else ("ON_TRACK" if pending else "")
        if parts and reminded != today:
            team_parts = [x for x in parts if not x.startswith("LATE_TEST")]
            lab_parts = [x for x in parts if x.startswith("LATE_TEST")]
            if team_parts:   # request not acknowledged / not completed -> provisioning team
                late.append(f"• {phone} ({'cease' if cease_pending else 'provision'}): {', '.join(team_parts)}")
            if lab_parts:    # testing overdue -> lab / review channel, not the provisioning team
                late_test.append(f"• {phone}: {', '.join(lab_parts)} (status {prov or exe or 'blank'})")
            reminded = today
        if parts and reminded:
            status += f" (reminded {reminded})"
        if status != prev:
            setq("SLA_Status", status)

    log.info(f"{len(q_updates)} queue cell(s), {len(p_updates)} Priority cell(s), {len(review)} for review, {len(late)} late request(s), {len(late_test)} late test(s)")
    for c in p_updates:
        log.info(f"  Priority R{c.row}C{c.col} -> {c.value}")
    if a.apply:
        if q_updates:
            qws.update_cells(q_updates)
        if p_updates:
            pws.update_cells(p_updates)
    if late:
        post_chat("⏰ NRT SLA reminder – these requests are past their target:\n" + "\n".join(late)
                  + "\nPlease reply in this space when complete. Thank you!", "PROVISIONING_WEBHOOK_URL", a.apply)
    if late_test:
        post_chat("🧪 NRT – testing is past its target for these numbers:\n" + "\n".join(late_test),
                  "REVIEW_WEBHOOK_URL", a.apply)
    if review:
        post_chat("🔎 NRT – AI replies that need a human check:\n" + "\n".join(review), "REVIEW_WEBHOOK_URL", a.apply)
    log.info("Validator done.")


if __name__ == "__main__":
    main()
