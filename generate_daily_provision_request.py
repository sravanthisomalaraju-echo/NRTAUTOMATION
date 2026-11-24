import os
import re
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from gspread.cell import Cell

# Load local .env variables
load_dotenv()

# Imports specifically structured for NRTAUTOMATION (GitHub Actions / Utilities)
try:
    from utilities.gsheet_manager import GSheetManager
except ImportError:
    from gsheet_manager import GSheetManager

try:
    from utilities.gchat_notifier import GChatNotifier
except ImportError:
    from gchat_notifier import GChatNotifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_CREDENTIALS = os.path.join(BASE_DIR, "credentials.json")
WORKBOOK_NAME = "Number Range Testing_MasterSheet"

# -----------------------------------------------------------------------------
# CLAIM-THEN-CONFIRM (patent Claim 1 / FIG. 9 steps 908-916, FIG. 15)
# Before the Chat request is posted, each Priority row in the request gets a claim
#   IN_PROGRESS|<run_id>|<YYYY-MM-DD HH:MM:SS>   in Column G (SIM Provisioning status).
# The run reads the rows back and keeps only rows carrying its own run_id.
#   post succeeded -> PROVISION_REQUESTED   post failed -> claim removed (blank)
# A claim older than STALE_CLAIM_MINUTES is left by an interrupted run: reported for
# review, never re-requested. A fresher claim belongs to a run still working: skipped.
# -----------------------------------------------------------------------------
import time as _time
import uuid as _uuid
CLAIM_PREFIX = "IN_PROGRESS"
CLAIM_SETTLE_SECONDS = int(os.getenv("CLAIM_SETTLE_SECONDS", "5"))
STALE_CLAIM_MINUTES = int(os.getenv("STALE_CLAIM_MINUTES", "60"))
RUN_ID = f"{datetime.now():%Y%m%d%H%M%S}-{_uuid.uuid4().hex[:6]}"


def _claim_value():
    return f"{CLAIM_PREFIX}|{RUN_ID}|{datetime.now():%Y-%m-%d %H:%M:%S}"


def _parse_claim(value):
    v = str(value or "").strip()
    if not v.upper().startswith(CLAIM_PREFIX):
        return None, None
    parts = v.split("|")
    run_id = parts[1] if len(parts) > 1 else ""
    try:
        at = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S") if len(parts) > 2 else None
    except ValueError:
        at = None
    return run_id, at


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_blocked_or_tested(val_str):
    """Helper to check if a text string indicates a tested/blocked entry."""
    if not val_str:
        return False
    return "block is already tested" in str(val_str).lower()

def archive_completed_queue_rows(wb, q_sheet, q_prov_idx):
    """Appends CEASED rows to 'Test_Queue_Archive' and deletes them from 'Test_Queue_Master'."""
    logger.info("🧹 Checking Test_Queue_Master for completed/ceased rows to archive...")
    
    # 1. Get or create the Test_Queue_Archive worksheet
    try:
        archive_sheet = wb.worksheet("Test_Queue_Archive")
    except Exception:
        logger.info("➕ Creating 'Test_Queue_Archive' tab in workbook...")
        archive_sheet = wb.add_worksheet(title="Test_Queue_Archive", rows=1000, cols=20)
        # Copy headers from active queue sheet
        header_row = q_sheet.row_values(1)
        if header_row:
            archive_sheet.append_row(header_row)

    # 2. Fetch fresh rows after cell updates
    q_rows = q_sheet.get_all_values()
    rows_to_archive = []
    indices_to_delete = []

    for idx, row in enumerate(q_rows[1:], start=2):
        if len(row) > q_prov_idx:
            prov_status = row[q_prov_idx].strip().upper()
            if prov_status == "CEASED":
                rows_to_archive.append(row)
                indices_to_delete.append(idx)

    # 3. Append to Archive and Delete from Active Queue (in REVERSE order)
    if rows_to_archive:
        logger.info(f"📦 Moving {len(rows_to_archive)} CEASED row(s) to 'Test_Queue_Archive'...")
        archive_sheet.append_rows(rows_to_archive)

        logger.info("🗑️ Purging archived rows from 'Test_Queue_Master'...")
        for r_idx in sorted(indices_to_delete, reverse=True):
            q_sheet.delete_rows(r_idx)
        logger.info("✅ Queue cleanup complete!")
    else:
        logger.info("ℹ️ No CEASED rows ready for archiving in this run.")


# =============================================================================
# RESULTS SYNC: Priority tab test results -> Test_Queue_Master
# Testing is now manual, so nothing else writes PASSED/FAILED to the queue.
# This step reads the carrier result columns on the Priority tab and updates
# Test_Execution_Status so passed numbers are picked up for the cease request.
# =============================================================================
PASS_MARKS = {"X", "P", "PASS", "PASSED", "OK", "\u2713", "\u2714"}
FAIL_MARKS = {"F", "FAIL", "FAILED"}
IGNORE_MARKS = {"", "NO W2", "N/A", "NA", "-", "SKIP", "SKIPPED"}
# Result columns whose header starts with one of these are optional (W2 is decommissioned).
OPTIONAL_REGION_PREFIXES = ("w2",)
RESULT_HEADER_RE = re.compile(r"(dish\s*dish|att mvno|tmo mvno|verizon mvno)", re.I)
INC_RE = re.compile(r"\bINC[A-Z]*\d{5,}\b", re.I)
# Queue statuses this step is allowed to change. Ceased / cease-requested rows are never touched.
SYNCABLE_EXEC = {"", "WAITING_PROVISIONING", "PROVISIONING_REQUESTED", "PROVISION_REQUESTED",
                 "PENDING", "QUEUED", "IN_PROGRESS", "IN_TESTING", "PASSED", "FAILED"}


def _find_header_row(rows, must_contain="iccid", max_scan=10):
    """The Priority tab's real header is on row 3 (rows 1-2 are box notes)."""
    for i, row in enumerate(rows[:max_scan]):
        if any(must_contain in str(c).strip().lower() for c in row):
            return i
    return None


def evaluate_priority_results(row, result_cols):
    """Returns (verdict, detail). verdict is PASSED, FAILED, or None while results are incomplete."""
    failed, missing = [], []
    for idx, header in result_cols:
        val = row[idx].strip().upper() if idx < len(row) else ""
        optional = header.lower().startswith(OPTIONAL_REGION_PREFIXES)
        if val in FAIL_MARKS:
            failed.append(header)
        elif val in PASS_MARKS:
            continue
        elif not optional:
            # Blank or unrecognised mark on a required column: not finished yet.
            # Never treat a guess as a pass, because a pass leads to a cease request.
            missing.append(header)
    if failed:
        return "FAILED", failed
    if missing:
        return None, missing
    return "PASSED", []


def sync_test_results_from_priority(p_rows, q_sheet, preview=False):
    hdr_i = _find_header_row(p_rows)
    if hdr_i is None:
        logger.warning("Results sync skipped: no header row containing 'ICCID' on the Priority tab.")
        return 0
    headers = [h.strip() for h in p_rows[hdr_i]]
    low = [h.lower() for h in headers]

    def col(*keys):
        return next((i for i, h in enumerate(low) if any(k in h for k in keys)), None)

    tn_i, iccid_i, remarks_i = col("arnold", "internal test", "phone"), col("iccid"), col("remarks")
    result_cols = [(i, h) for i, h in enumerate(headers) if RESULT_HEADER_RE.search(h)]
    if tn_i is None or iccid_i is None or not result_cols:
        logger.warning(f"Results sync skipped: required Priority columns not found in {headers}")
        return 0

    # Latest Priority result per phone number (later rows win, like the rest of this script)
    results_by_tn = {}
    for row_num, row in enumerate(p_rows[hdr_i + 1:], start=hdr_i + 2):
        iccid = row[iccid_i].strip() if iccid_i < len(row) else ""
        if not iccid.startswith("89"):
            continue  # skips 'Block is already tested' rows and blanks
        tn = re.sub(r"[^\d]", "", row[tn_i] if tn_i < len(row) else "")[-10:]
        if not tn:
            continue
        verdict, detail = evaluate_priority_results(row, result_cols)
        remarks = row[remarks_i].strip() if remarks_i is not None and remarks_i < len(row) else ""
        inc = INC_RE.search(remarks)
        results_by_tn[tn] = {"row": row_num, "iccid": iccid, "verdict": verdict,
                             "detail": detail, "incident": inc.group(0) if inc else ""}

    q_rows = q_sheet.get_all_values()
    if not q_rows:
        return 0
    qh = [h.strip().lower() for h in q_rows[0]]

    def qcol(name):
        return next((i for i, h in enumerate(qh) if h == name), None)

    q_tn, q_iccid = qcol("phone_number"), qcol("assigned_iccid")
    q_prov, q_exec = qcol("provisioning_status"), qcol("test_execution_status")
    q_inc, q_reason, q_ts = qcol("snow_incident_inc"), qcol("failure_reason"), qcol("last_sync_timestamp")
    if None in (q_tn, q_iccid, q_prov, q_exec):
        logger.warning(f"Results sync skipped: required Test_Queue_Master columns not found in {q_rows[0]}")
        return 0

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cells, changes = [], []
    for r_idx, row in enumerate(q_rows[1:], start=2):
        def get(i):
            return row[i].strip() if i is not None and i < len(row) else ""

        tn = re.sub(r"[^\d]", "", get(q_tn))[-10:]
        res = results_by_tn.get(tn)
        if not res or not res["verdict"]:
            continue  # not in Priority, or results not complete yet
        if get(q_iccid) and get(q_iccid) != res["iccid"]:
            logger.warning(f"Row {r_idx} ({get(q_tn)}): queue ICCID {get(q_iccid)} differs from "
                           f"Priority row {res['row']} ICCID {res['iccid']} - not synced, check by hand")
            continue
        prov, exec_s = get(q_prov).upper(), get(q_exec).upper()
        if prov in ("CEASED", "CEASE_REQUESTED") or exec_s not in SYNCABLE_EXEC:
            continue

        new_inc = res["incident"] if res["verdict"] == "FAILED" and q_inc is not None and not get(q_inc) else ""
        if exec_s == res["verdict"] and not new_inc:
            continue
        if exec_s != res["verdict"]:
            cells.append(Cell(row=r_idx, col=q_exec + 1, value=res["verdict"]))
        if res["verdict"] == "FAILED":
            if new_inc:
                cells.append(Cell(row=r_idx, col=q_inc + 1, value=new_inc))
            if q_reason is not None and not get(q_reason):
                cells.append(Cell(row=r_idx, col=q_reason + 1, value="Failed: " + ", ".join(res["detail"])))
        if q_ts is not None:
            cells.append(Cell(row=r_idx, col=q_ts + 1, value=now_str))
        note = ""
        if res["verdict"] == "FAILED":
            note = f" ({', '.join(res['detail'])}; incident {res['incident'] or 'not recorded'})"
        changes.append(f"Row {r_idx} {get(q_tn)}: {exec_s or '(blank)'} -> {res['verdict']}{note}")

    for c in changes:
        logger.info(("[PREVIEW] " if preview else "Results sync: ") + c)
    if not changes:
        logger.info("Results sync: Test_Queue_Master already matches the Priority tab.")
    elif not preview:
        q_sheet.update_cells(cells)  # one API call
        logger.info(f"Results sync: updated {len(changes)} Test_Queue_Master row(s) from the Priority tab.")
    return len(changes)



# =============================================================================
# RE-TEST ON TICKET CLOSE (patent answer 6 / FIG. 3 "Incident resolved" edge)
# A FAILED number keeps its SIM provisioned. When every failure ticket recorded for
# it is closed, it goes back to testing:
#   Test_Queue_Master  Test_Execution_Status FAILED -> QUEUED  (shield box runner picks it up)
#   Priority tab       F marks cleared (x marks kept), Remarks gets a re-test note
# "Closed" = every ticket in SNOW_Incident_INC is Resolved/Closed in SNOW_Ticket_Tracker.
# Manual override: set Test_Execution_Status to RETEST to re-queue without a ticket check.
# Set RETEST_PREVIEW=1 to log what would change without writing.
# =============================================================================
CLOSED_TICKET_STATES = {"RESOLVED", "CLOSED", "CLOSED COMPLETE", "CLOSED_COMPLETE", "COMPLETE", "COMPLETED"}
MANUAL_RETEST_VALUES = {"RETEST", "READY_FOR_RETEST", "RE-TEST"}
TICKET_RE = re.compile(r"\b(?:INC[A-Z]*\d{5,}|MOCK_[A-Z]+_\d+|MANUAL_[A-Z]+_\d+|REQ\d{5,}|RITM\d{5,})\b", re.I)


def requeue_resolved_failures(wb, p_sheet, p_rows, q_sheet, reserved_iccids=(), preview=None):
    preview = (os.getenv("RETEST_PREVIEW", "") in ("1", "true", "yes")) if preview is None else preview

    # ticket states from SNOW_Ticket_Tracker
    states = {}
    try:
        t_rows = wb.worksheet("SNOW_Ticket_Tracker").get_all_values()
        th = [h.strip().lower() for h in t_rows[0]] if t_rows else []
        ti, si = th.index("ticket_number"), th.index("snow_state")
        for r in t_rows[1:]:
            if len(r) > max(ti, si) and r[ti].strip():
                states[r[ti].strip().upper()] = r[si].strip().upper()
    except Exception as e:
        logger.warning(f"Re-test check: SNOW_Ticket_Tracker not readable ({e}); only manual RETEST rows are handled.")

    q_rows = q_sheet.get_all_values()
    if not q_rows:
        return 0
    qh = [h.strip().lower() for h in q_rows[0]]
    qc = lambda n: next((i for i, h in enumerate(qh) if h == n), None)
    q_tn, q_iccid, q_exec = qc("phone_number"), qc("assigned_iccid"), qc("test_execution_status")
    q_inc, q_reason, q_ts = qc("snow_incident_inc"), qc("failure_reason"), qc("last_sync_timestamp")
    if None in (q_tn, q_iccid, q_exec):
        logger.warning("Re-test check skipped: Test_Queue_Master columns not found.")
        return 0

    # latest Priority row per TN (for clearing F marks)
    hdr_i = _find_header_row(p_rows)
    headers = [h.strip() for h in p_rows[hdr_i]] if hdr_i is not None else []
    low = [h.lower() for h in headers]
    pc = lambda *k: next((i for i, h in enumerate(low) if any(x in h for x in k)), None)
    p_tn, p_iccid, p_rem = pc("arnold", "internal test", "phone"), pc("iccid"), pc("remarks")
    result_cols = [i for i, h in enumerate(headers) if RESULT_HEADER_RE.search(h)]
    p_by_tn = {}
    if hdr_i is not None and p_tn is not None:
        for n, row in enumerate(p_rows[hdr_i + 1:], start=hdr_i + 2):
            tn = re.sub(r"[^\d]", "", row[p_tn] if p_tn < len(row) else "")[-10:]
            if tn:
                p_by_tn[tn] = (n, row)

    today = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    q_cells, p_cells, done = [], [], []
    for r_idx, row in enumerate(q_rows[1:], start=2):
        g = lambda i: row[i].strip() if i is not None and i < len(row) else ""
        exec_s, iccid = g(q_exec).upper(), g(q_iccid)
        manual = exec_s in MANUAL_RETEST_VALUES
        if exec_s != "FAILED" and not manual:
            continue
        if iccid in reserved_iccids:
            continue
        tickets = [t.upper() for t in TICKET_RE.findall(g(q_inc))]
        if not manual:
            if not tickets:
                continue  # no failure ticket recorded: wait for a person (set RETEST)
            open_t = [t for t in tickets if states.get(t) not in CLOSED_TICKET_STATES]
            if open_t:
                continue  # at least one failure ticket still open (or not tracked yet)
        why = "set to RETEST by hand" if manual else f"{', '.join(tickets)} closed"
        q_cells.append(Cell(row=r_idx, col=q_exec + 1, value="QUEUED"))
        if q_reason is not None:
            q_cells.append(Cell(row=r_idx, col=q_reason + 1, value=f"Re-test queued {today} ({why}). Previous: {g(q_reason)}"[:500]))
        if q_ts is not None:
            q_cells.append(Cell(row=r_idx, col=q_ts + 1, value=now_str))
        tn = re.sub(r"[^\d]", "", g(q_tn))[-10:]
        pr = p_by_tn.get(tn)
        if pr and (p_iccid is None or not iccid or (p_iccid < len(pr[1]) and pr[1][p_iccid].strip() == iccid)):
            n, prow = pr
            for c in result_cols:
                if c < len(prow) and prow[c].strip().upper() in FAIL_MARKS:
                    p_cells.append(Cell(row=n, col=c + 1, value=""))
            if p_rem is not None:
                old = prow[p_rem].strip() if p_rem < len(prow) else ""
                p_cells.append(Cell(row=n, col=p_rem + 1, value=(old + " | " if old else "") + f"Re-test queued {today} ({why})"))
        done.append(f"Row {r_idx} {g(q_tn)}: FAILED -> QUEUED ({why})")

    for d in done:
        logger.info(("[PREVIEW] " if preview else "Re-test: ") + d)
    if not done:
        logger.info("Re-test: no failed numbers with closed tickets.")
    elif not preview:
        q_sheet.update_cells(q_cells)
        if p_cells:
            p_sheet.update_cells(p_cells)
    return len(done)

# SIM states held outside NRT (e.g. lent for other testing). These SIMs are never
# reset to AVAILABLE, assigned, provisioned or ceased by this script.
RESERVED_SIM_STATES = {"RESERVED", "ON_HOLD", "HOLD", "DO_NOT_USE"}


def generate_and_post_daily_requests():
    logger.info("🚀 Starting Targeted Daily Provisioning & Cease Request Generator...")

    # STEP 0: pull PSIM cease confirmations from Google Chat -> Priority Column H = Done.
    # Non-fatal: if Chat is unreachable, the run continues with whatever Column H already says.
    if os.getenv("SKIP_GCHAT_CEASE_SYNC", "").lower() not in ("1", "true", "yes"):
        try:
            try:
                from sync_cease_from_gchat import run_cease_sync
            except ImportError:
                from utilities.sync_cease_from_gchat import run_cease_sync
            marked = run_cease_sync(days=int(os.getenv("GCHAT_CEASE_LOOKBACK_DAYS", "5")))
            logger.info(f"Step 0: Chat cease sync marked {marked} Priority row(s) Done.")
        except Exception as e:
            logger.warning(f"⚠️ Step 0: Chat cease sync skipped ({e}). Continuing with current Column H values.")

    cred_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", JSON_CREDENTIALS)
    gsheet = GSheetManager(cred_file, sheet_name=WORKBOOK_NAME)
    wb = gsheet.gc.open(WORKBOOK_NAME)

    notifier = GChatNotifier()

    p_sheet = wb.worksheet("Priority Test numbers with effective dates")
    sim_sheet = wb.worksheet("SIM_Cards_Inventory")
    q_sheet = wb.worksheet("Test_Queue_Master")

    # -------------------------------------------------------------------------
    # STEP 1: PARSE PRIORITY TAB & MAP LATEST OCCURRENCE PER ICCID / TN
    # -------------------------------------------------------------------------
    logger.info("🔍 Mapping latest occurrences per ICCID & TN from Priority tab...")
    p_rows = p_sheet.get_all_values()
    # Real header is on row 3 (rows 1-2 are box notes) - detect it instead of assuming row 1.
    p_hdr_i = _find_header_row(p_rows)
    if p_hdr_i is None:
        logger.error("❌ No header row containing 'ICCID' found in the first 10 rows of the Priority tab. Aborting.")
        sys.exit(1)
    p_headers = [h.strip().lower() for h in p_rows[p_hdr_i]]

    def _p_col(*keys):
        return next((i for i, h in enumerate(p_headers) if any(k in h for k in keys)), None)

    p_phone_idx = _p_col("arnold", "internal test", "phone")
    p_iccid_idx = _p_col("iccid")
    p_prov_idx = _p_col("provisioning status")
    p_cease_idx = _p_col("cease status")
    if None in (p_phone_idx, p_iccid_idx, p_prov_idx, p_cease_idx):
        logger.error(f"❌ Required Priority columns not found in header row {p_hdr_i + 1}: {p_rows[p_hdr_i]}. Aborting.")
        sys.exit(1)
    logger.info(f"Priority header on row {p_hdr_i + 1}: phone={p_phone_idx}, iccid={p_iccid_idx}, "
                f"prov={p_prov_idx}, cease={p_cease_idx}")

    latest_p_by_iccid = {}
    latest_p_by_tn = {}

    for idx, row in enumerate(p_rows[p_hdr_i + 1:], start=p_hdr_i + 2):
        if len(row) > max(p_prov_idx, p_cease_idx, p_phone_idx):
            raw_phone = row[p_phone_idx].strip()
            clean_phone = re.sub(r'[^\d]', '', raw_phone)[-10:]
            iccid = row[p_iccid_idx].strip() if len(row) > p_iccid_idx else ""
            
            prov_val = row[p_prov_idx].strip().upper()
            cease_val = row[p_cease_idx].strip().upper()

            if is_blocked_or_tested(iccid) or is_blocked_or_tested(raw_phone):
                continue

            row_info = {
                'prov_raw': row[p_prov_idx].strip(),
                'row_idx': idx,
                'raw_phone': raw_phone,
                'clean_phone': clean_phone,
                'iccid': iccid,
                'prov_status': prov_val,
                'cease_status': cease_val
            }

            if clean_phone:
                latest_p_by_tn[clean_phone] = row_info
            if iccid.startswith("89"):
                latest_p_by_iccid[iccid] = row_info

    # -------------------------------------------------------------------------
    # STEP 2: SYNC SIM INVENTORY BASED ON LATEST PRIORITY STATE
    # -------------------------------------------------------------------------
    sim_rows = sim_sheet.get_all_values()
    sim_headers = [h.strip().lower() for h in sim_rows[0]]

    sim_iccid_idx = next((i for i, h in enumerate(sim_headers) if "iccid" in h), 0)
    sim_state_idx = next((i for i, h in enumerate(sim_headers) if "state" in h), 2)
    sim_tn_idx = next((i for i, h in enumerate(sim_headers) if "tn" in h or "phone" in h), 3)
    sim_env_idx = next((i for i, h in enumerate(sim_headers) if "env" in h), 4)

    sim_sync_cells = []
    assigned_sim_tn_map = {}
    iccid_to_sim_row_map = {}
    cease_sim_items = []
    reserved_iccids = set()

    for row_idx, row in enumerate(sim_rows[1:], start=2):
        if len(row) > max(sim_iccid_idx, sim_tn_idx, sim_state_idx):
            iccid = row[sim_iccid_idx].strip()
            raw_tn = row[sim_tn_idx].strip()
            state = row[sim_state_idx].strip().upper()
            clean_tn = re.sub(r'[^\d]', '', raw_tn)[-10:]

            if is_blocked_or_tested(iccid) or is_blocked_or_tested(raw_tn):
                continue

            if iccid and iccid.startswith("89"):
                iccid_to_sim_row_map[iccid] = row_idx
                if state in RESERVED_SIM_STATES:
                    reserved_iccids.add(iccid)
                    logger.info(f"🔒 ICCID {iccid} is {state} - left unchanged and excluded from NRT requests")
                    continue
                latest_p = latest_p_by_iccid.get(iccid) or latest_p_by_tn.get(clean_tn)

                if latest_p:
                    p_cease_done = latest_p['cease_status'] in ["DONE", "CEASED", "COMPLETED"]

                    if p_cease_done and state != "AVAILABLE":
                        sim_sync_cells.append(Cell(row=row_idx, col=sim_state_idx + 1, value="AVAILABLE"))
                        sim_sync_cells.append(Cell(row=row_idx, col=sim_tn_idx + 1, value=""))
                        if len(row) > sim_env_idx:
                            sim_sync_cells.append(Cell(row=row_idx, col=sim_env_idx + 1, value=""))
                        logger.info(f"🔄 Resetting SIM to AVAILABLE (Priority Cease Done): ICCID {iccid}")
                        continue

                if state in ["ASSIGNED", "WAITING_PROVISIONING"]:
                    if clean_tn:
                        assigned_sim_tn_map[clean_tn] = iccid
                elif state in ["CEASE_PENDING", "CEASE_NEEDED"]:
                    cease_sim_items.append((raw_tn, iccid))

    if sim_sync_cells:
        sim_sheet.update_cells(sim_sync_cells)

    # STEP 2b: copy Priority tab pass/fail results into Test_Queue_Master
    # so passed numbers are picked up for the cease request below.
    sync_test_results_from_priority(p_rows, q_sheet)

    # STEP 2c: failed numbers whose failure tickets are all closed go back to testing
    if requeue_resolved_failures(wb, p_sheet, p_rows, q_sheet, reserved_iccids=reserved_iccids):
        p_rows = p_sheet.get_all_values()  # F marks were cleared; re-read before later steps

    # -------------------------------------------------------------------------
    # STEP 3: READ QUEUE MASTER FOR PASSED CEASE TRIGGERS & SYNC CEASED STATUS
    # -------------------------------------------------------------------------
    q_rows = q_sheet.get_all_values()
    q_headers = [h.strip().lower() for h in q_rows[0]]

    q_phone_idx = next((i for i, h in enumerate(q_headers) if "phone" in h), 2)
    q_iccid_idx = next((i for i, h in enumerate(q_headers) if "iccid" in h), 3)
    q_prov_idx = next((i for i, h in enumerate(q_headers) if "provisioning_status" in h), 5)
    q_exec_idx = next((i for i, h in enumerate(q_headers) if "test_execution_status" in h), 6)
    q_snow_cease_idx = next((i for i, h in enumerate(q_headers) if "snow_cease_req" in h), 10)

    queue_waiting_tns = set()
    cease_items = list(cease_sim_items)
    q_cease_row_map = {}
    q_sync_cells = []

    for row_idx, row in enumerate(q_rows[1:], start=2):
        if len(row) > max(q_phone_idx, q_iccid_idx):
            raw_phone = row[q_phone_idx].strip()
            iccid = row[q_iccid_idx].strip()
            clean_phone = re.sub(r'[^\d]', '', raw_phone)[-10:]

            prov_status = row[q_prov_idx].strip().upper() if len(row) > q_prov_idx else ""
            exec_status = row[q_exec_idx].strip().upper() if len(row) > q_exec_idx else ""
            snow_cease = row[q_snow_cease_idx].strip() if len(row) > q_snow_cease_idx else ""

            if is_blocked_or_tested(iccid) or exec_status in ["SKIPPED_ALREADY_TESTED", "SKIPPED"]:
                continue

            latest_p = latest_p_by_iccid.get(iccid) or latest_p_by_tn.get(clean_phone)
            p_cease_done = latest_p['cease_status'] in ["DONE", "CEASED", "COMPLETED"] if latest_p else False

            # Flipped to CEASED in Test Queue Master when Priority Tab Cease is marked Done
            if p_cease_done and prov_status != "CEASED":
                q_sync_cells.append(Cell(row=row_idx, col=q_prov_idx + 1, value="CEASED"))
                logger.info(f"🔄 Syncing Test Queue Master to CEASED: ICCID {iccid}")

            if clean_phone and prov_status not in ["PROVISIONING_COMPLETED", "PROVISION_COMPLETED", "DONE", "CEASED"]:
                if exec_status not in ["PASSED", "FAILED"]:
                    queue_waiting_tns.add(clean_phone)
                    if iccid and iccid.startswith("89"):
                        assigned_sim_tn_map[clean_phone] = iccid

            if exec_status == "PASSED" and exec_status != "FAILED" and not p_cease_done:
                if prov_status not in ["CEASED", "CEASE_REQUESTED"] and snow_cease not in ["CEASED_DONE", "DONE"]:
                    if iccid and iccid.startswith("89"):
                        if (raw_phone, iccid) not in cease_items:
                            cease_items.append((raw_phone, iccid))
                        q_cease_row_map[iccid] = row_idx

    if q_sync_cells:
        q_sheet.update_cells(q_sync_cells)

    if reserved_iccids:
        cease_items = [(tn, ic) for tn, ic in cease_items if ic not in reserved_iccids]

    # -------------------------------------------------------------------------
    # STEP 4: FILTER PROVISION ITEMS & MAP ALL ROW INDICES
    # -------------------------------------------------------------------------
    provision_items = []
    provision_rows_indices = []
    cease_rows_indices = []
    stale_claims = []

    for clean_tn, info in latest_p_by_tn.items():
        prov_status = info['prov_status']
        cease_status = info['cease_status']
        raw_phone = info['raw_phone']
        iccid = info['iccid'] or assigned_sim_tn_map.get(clean_tn)

        if cease_status in ["DONE", "CEASED", "COMPLETED"]:
            continue

        claim_run, claimed_at = _parse_claim(info.get('prov_raw', ''))
        if claim_run is not None:
            age = (datetime.now() - claimed_at).total_seconds() / 60 if claimed_at else None
            if age is None or age >= STALE_CLAIM_MINUTES:
                stale_claims.append((info['row_idx'], raw_phone, claim_run or "unknown run",
                                     f"{age:.0f} min ago" if age is not None else "no timestamp"))
            continue  # claimed by another run (fresh) or interrupted (stale): never re-requested here

        if clean_tn in queue_waiting_tns or clean_tn in assigned_sim_tn_map:
            if prov_status not in ["DONE", "PROVISIONING_COMPLETED", "PROVISION_REQUESTED"]:
                if iccid and iccid.startswith("89") and iccid not in reserved_iccids:
                    provision_items.append((raw_phone, iccid))
                    provision_rows_indices.append(info['row_idx'])

    for raw_phone, iccid in cease_items:
        clean_phone = re.sub(r'[^\d]', '', raw_phone)[-10:]
        latest_p = latest_p_by_iccid.get(iccid) or latest_p_by_tn.get(clean_phone)
        if latest_p:
            cease_rows_indices.append(latest_p['row_idx'])

    # -------------------------------------------------------------------------
    # STEP 5: DISPATCH GCHAT NOTIFICATION & UPDATE SHEET STATUSES
    # -------------------------------------------------------------------------
    all_row_indices = list(set(provision_rows_indices + cease_rows_indices))

    if not provision_items and not cease_items:
        logger.info("ℹ️ No active pending provisioning or cease items found. Running archive check before exit...")
        archive_completed_queue_rows(wb, q_sheet, q_prov_idx)
        sys.exit(0)

    start_row = min(all_row_indices) if all_row_indices else 2
    end_row = max(all_row_indices) if all_row_indices else start_row

    logger.info(f"🎯 Filtered Request Summary: {len(provision_items)} Provision item(s) and {len(cease_items)} PASSED Cease item(s) (Priority Rows {start_row}-{end_row}).")

    if stale_claims:
        for r_idx, tn, run, age in stale_claims:
            logger.warning(f"⚠️ Priority row {r_idx} ({tn}) still claimed by run {run} ({age}) with no request "
                           "recorded - left for review, not re-requested. Check the Chat space, then set "
                           "Column G to PROVISION_REQUESTED or clear it.")

    # --- CLAIM FIRST: mark each provision row before the request is posted ---
    if provision_rows_indices:
        claim = _claim_value()
        p_sheet.update_cells([Cell(row=r, col=p_prov_idx + 1, value=claim) for r in provision_rows_indices])
        _time.sleep(CLAIM_SETTLE_SECONDS)
        fresh = p_sheet.get_all_values()
        kept_rows, kept_items, lost = [], [], []
        for r_idx, item in zip(provision_rows_indices, provision_items):
            v = fresh[r_idx - 1][p_prov_idx] if r_idx - 1 < len(fresh) and p_prov_idx < len(fresh[r_idx - 1]) else ""
            if _parse_claim(v)[0] == RUN_ID:
                kept_rows.append(r_idx); kept_items.append(item)
            else:
                lost.append(r_idx)
        if lost:
            logger.warning(f"⚠️ Run {RUN_ID} backed off {len(lost)} row(s) claimed by another run: {lost}")
        provision_rows_indices, provision_items = kept_rows, kept_items
        logger.info(f"🔒 Run {RUN_ID} claimed {len(provision_rows_indices)} provision row(s): {provision_rows_indices}")
        if not provision_items and not cease_items:
            logger.info("ℹ️ Nothing left to request after read-back. Exiting.")
            sys.exit(0)

    posted = notifier.send_batch_provision_cease_request(
        cease_items=cease_items,
        provision_items=provision_items,
        start_row=start_row,
        end_row=end_row,
        tab_name="Priority Test numbers with effective dates",
        workbook_name=WORKBOOK_NAME
    )

    if posted:
        logger.info("✅ GChat request posted! Updating Google Sheet statuses...")

        if provision_rows_indices:
            prov_cells = [
                Cell(row=r_idx, col=p_prov_idx + 1, value="PROVISION_REQUESTED")
                for r_idx in provision_rows_indices
            ]
            p_sheet.update_cells(prov_cells)

        if cease_items:
            sim_cells = []
            for tn, iccid in cease_items:
                sim_row_idx = iccid_to_sim_row_map.get(iccid)
                if sim_row_idx:
                    sim_cells.append(Cell(row=sim_row_idx, col=sim_state_idx + 1, value="CEASE_REQUESTED"))
            if sim_cells:
                sim_sheet.update_cells(sim_cells)

            q_cease_cells = []
            for tn, iccid in cease_items:
                q_row_idx = q_cease_row_map.get(iccid)
                if q_row_idx:
                    q_cease_cells.append(Cell(row=q_row_idx, col=q_prov_idx + 1, value="CEASE_REQUESTED"))
            if q_cease_cells:
                q_sheet.update_cells(q_cease_cells)

        # -------------------------------------------------------------------------
        # STEP 6: ARCHIVE & PURGE COMPLETED ROWS FROM TEST QUEUE MASTER
        # -------------------------------------------------------------------------
        archive_completed_queue_rows(wb, q_sheet, q_prov_idx)

        logger.info("🎉 Execution completed successfully!")

        sys.exit(0)
    else:
        logger.error("❌ Failed to post message to GChat webhook.")
        if provision_rows_indices:
            # Post failed: release the claims so the next run requests these rows again.
            p_sheet.update_cells([Cell(row=r, col=p_prov_idx + 1, value="") for r in provision_rows_indices])
            logger.error(f"🔓 Released claims on rows {provision_rows_indices} for the next run.")
        sys.exit(1)

if __name__ == "__main__":
    generate_and_post_daily_requests()