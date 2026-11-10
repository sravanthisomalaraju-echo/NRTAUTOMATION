import os
import gspread
from datetime import datetime

def normalize_date(date_str):
    """Normalizes date strings so '08/01/2026' matches '8/1/2026'."""
    if not date_str:
        return ""
    parts = str(date_str).strip().split('/')
    if len(parts) == 3:
        try:
            return f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
        except ValueError:
            pass
    return str(date_str).strip()

class AutoQueueBuilder:
    def __init__(self, json_cred_path, sheet_name="Number Range Testing_MasterSheet"):
        token_path = os.path.join(os.path.dirname(json_cred_path), "token.json")
        if os.path.exists(token_path):
            self.gc = gspread.oauth(credentials_filename=json_cred_path, authorized_user_filename=token_path)
        else:
            self.gc = gspread.service_account(filename=json_cred_path)
            
        self.sh = self.gc.open(sheet_name)
        self.priority_ws = self.sh.worksheet("Priority Test numbers with effective dates")
        self.sim_ws = self.sh.worksheet("SIM_Cards_Inventory")
        self.queue_ws = self.sh.worksheet("Test_Queue_Master")

    def get_available_sims(self):
        """Returns a list of tuples: (row_index, iccid) for all AVAILABLE SIMs."""
        available_sims = []
        rows = self.sim_ws.get_all_values()
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) >= 3 and str(row[2]).strip().upper() == "AVAILABLE":
                available_sims.append((idx, str(row[0]).strip()))
        return available_sims

    def process_and_assign_new_blocks(self, target_date_str):
        """
        1. Scans Priority tab ONLY for rows matching target_date_str.
        2. Skips rows marked 'Block is already tested'.
        3. Assigns available ICCIDs from SIM_Cards_Inventory to genuine NEW blocks.
        4. Appends assigned rows directly to Test_Queue_Master as QUEUED.
        """
        print(f"\n⚡ Running Intelligent ICCID Assignment for {target_date_str}...")
        
        target_date_norm = normalize_date(target_date_str)
        priority_rows = self.priority_ws.get_all_values()
        available_sims = self.get_available_sims()
        
        assigned_count = 0
        skipped_count = 0

        for p_idx, row in enumerate(priority_rows[1:], start=2): # Row 1 is header
            if not row or len(row) < 3:
                continue

            eff_date_norm = normalize_date(row[0])
            block = str(row[1]).strip()
            tn = str(row[2]).strip()
            iccid_col = str(row[3]).strip() if len(row) > 3 else ""

            # ==============================================================================
            # RULE 1: ONLY PROCESS ROWS MATCHING TARGET EXTRACTION DATE
            # ==============================================================================
            if eff_date_norm != target_date_norm:
                continue

            # ==============================================================================
            # RULE 2: SKIP IF ALREADY TESTED OR ICCID ALREADY ASSIGNED
            # ==============================================================================
            if "block is already tested" in iccid_col.lower():
                print(f"   ℹ️ Row {p_idx} ({tn}): Block is already tested. Skipping SIM assignment.")
                skipped_count += 1
                continue

            if len(iccid_col) >= 15 and "null" not in iccid_col.lower():
                print(f"   ℹ️ Row {p_idx} ({tn}): Already has ICCID assigned ({iccid_col}). Skipping.")
                continue

            # ==============================================================================
            # RULE 3: ASSIGN NEXT AVAILABLE SIM TO UNTESTED NEW BLOCK
            # ==============================================================================
            if tn:
                if not available_sims:
                    print("   ⚠️ Ran out of AVAILABLE SIM cards in SIM_Cards_Inventory!")
                    break

                # Pop next available SIM
                sim_row_idx, assigned_iccid = available_sims.pop(0)

                # 1. Update Priority Sheet Column D with assigned ICCID
                self.priority_ws.update_cell(p_idx, 4, assigned_iccid)
                
                # 2. Update SIM_Cards_Inventory state to ASSIGNED
                self.sim_ws.update_cell(sim_row_idx, 3, "ASSIGNED")
                self.sim_ws.update_cell(sim_row_idx, 4, tn)

                # Append to Test_Queue_Master with All 3 PCIs and WAITING_PROVISIONING status
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.queue_ws.append_row([
                    row[0],                  # Col A: Date
                    block,                   # Col B: Block
                    tn,                      # Col C: Phone_Number
                    assigned_iccid,          # Col D: Assigned_ICCID
                    "80/81, 84, 86",         # Col E: Target_Env (Covers all 3 PCIs)
                    "",                      # Col F: Provisioning_Status
                    "WAITING_PROVISIONING",  # Col G: Test_Execution_Status
                    "", "", "", "", "", "", "", # Col H-N empty
                    now_str                  # Col O: Last_Sync_Timestamp
                ])

                assigned_count += 1
                print(f"   ✅ Assigned ICCID {assigned_iccid} ➔ TN {tn} (Appended to Test_Queue_Master as QUEUED)")

        print(f"🎉 Auto-Assignment Complete for {target_date_str}: Assigned {assigned_count} new line(s), Skipped {skipped_count} tested block(s).\n")