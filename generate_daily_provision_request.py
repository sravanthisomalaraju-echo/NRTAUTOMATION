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


def generate_and_post_daily_requests():
    logger.info("🚀 Starting Targeted Daily Provisioning & Cease Request Generator...")

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
    p_headers = [h.strip().lower() for h in p_rows[0]]

    p_phone_idx = next((i for i, h in enumerate(p_headers) if "arnold" in h or "phone" in h or "number" in h), 2)
    p_iccid_idx = next((i for i, h in enumerate(p_headers) if "iccid" in h), 3)
    p_prov_idx = next((i for i, h in enumerate(p_headers) if "provisioning status" in h), 6)
    p_cease_idx = next((i for i, h in enumerate(p_headers) if "cease status" in h), 7)

    latest_p_by_iccid = {}
    latest_p_by_tn = {}

    for idx, row in enumerate(p_rows[1:], start=2):
        if len(row) > max(p_prov_idx, p_cease_idx, p_phone_idx):
            raw_phone = row[p_phone_idx].strip()
            clean_phone = re.sub(r'[^\d]', '', raw_phone)[-10:]
            iccid = row[p_iccid_idx].strip() if len(row) > p_iccid_idx else ""
            
            prov_val = row[p_prov_idx].strip().upper()
            cease_val = row[p_cease_idx].strip().upper()

            if is_blocked_or_tested(iccid) or is_blocked_or_tested(raw_phone):
                continue

            row_info = {
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

    # -------------------------------------------------------------------------
    # STEP 4: FILTER PROVISION ITEMS & MAP ALL ROW INDICES
    # -------------------------------------------------------------------------
    provision_items = []
    provision_rows_indices = []
    cease_rows_indices = []

    for clean_tn, info in latest_p_by_tn.items():
        prov_status = info['prov_status']
        cease_status = info['cease_status']
        raw_phone = info['raw_phone']
        iccid = info['iccid'] or assigned_sim_tn_map.get(clean_tn)

        if cease_status in ["DONE", "CEASED", "COMPLETED"]:
            continue

        if clean_tn in queue_waiting_tns or clean_tn in assigned_sim_tn_map:
            if prov_status not in ["DONE", "PROVISIONING_COMPLETED", "PROVISION_REQUESTED"]:
                if iccid and iccid.startswith("89"):
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
        sys.exit(1)

if __name__ == "__main__":
    generate_and_post_daily_requests()