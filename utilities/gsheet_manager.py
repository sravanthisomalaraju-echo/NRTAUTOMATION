import os
import gspread

class GSheetManager:
    """Handles authentication, state tracking, and reading active queued items."""
    
    def __init__(self, json_cred_path, sheet_name="Number Range Testing_MasterSheet"):
        token_path = os.path.join(os.path.dirname(json_cred_path), "token.json")
        
        if os.path.exists(token_path):
            self.gc = gspread.oauth(
                credentials_filename=json_cred_path,
                authorized_user_filename=token_path
            )
        else:
            self.gc = gspread.service_account(filename=json_cred_path)
            
        self.sh = self.gc.open(sheet_name)
        self.queue_ws = self.sh.worksheet("Test_Queue_Master")

    def get_priority_test_numbers(self):
        """
        Reads active items needing provisioning where Provisioning_Status is NOT already requested.
        Returns 5 values: (start_row, end_row, cease_items, provision_items, queue_row_indices)
        """
        all_rows = self.queue_ws.get_all_values()
        
        provision_items = []
        cease_items = []
        queue_row_indices = []

        # Iterate through Test_Queue_Master (Header is Row 1)
        for idx, row in enumerate(all_rows[1:], start=2):
            if not row or len(row) < 7:
                continue
            
            tn = str(row[2]).strip()                  # Col C: Phone_Number
            iccid = str(row[3]).strip()               # Col D: Assigned_ICCID
            prov_status = str(row[5]).strip().upper() # Col F: Provisioning_Status
            exec_status = str(row[6]).strip().upper() # Col G: Test_Execution_Status

            # ==============================================================================
            # RULE 1: SKIP IF PROVISIONING REQUEST WAS ALREADY SENT TO GCHAT
            # ==============================================================================
            if "REQUESTED" in prov_status:
                continue

            # ==============================================================================
            # RULE 2: PICK UP NEW UNPROVISIONED ITEMS (WAITING_PROVISIONING / QUEUED / EMPTY)
            # ==============================================================================
            if exec_status in ["WAITING_PROVISIONING", "QUEUED", ""] and tn and len(iccid) >= 15:
                queue_row_indices.append(idx)
                provision_items.append((tn, iccid))

        if not queue_row_indices:
            return None, None, [], [], []

        # Map row range for context display in GChat message
        priority_ws = self.sh.worksheet("Priority Test numbers with effective dates")
        priority_rows = priority_ws.get_all_values()
        
        priority_indices = []
        queued_tns = {tn for tn, iccid in provision_items}

        for idx, row in enumerate(priority_rows[1:], start=2):
            if len(row) >= 3 and str(row[2]).strip() in queued_tns:
                priority_indices.append(idx)

        start_row = min(priority_indices) if priority_indices else min(queue_row_indices)
        end_row = max(priority_indices) if priority_indices else max(queue_row_indices)

        return start_row, end_row, cease_items, provision_items, queue_row_indices

    def mark_provisioning_as_requested(self, queue_row_indices):
        """Updates Column F (Provisioning_Status) to 'PROVISION_REQUESTED' for processed rows."""
        print(f"📝 Updating Google Sheets: Marking {len(queue_row_indices)} row(s) as PROVISION_REQUESTED...")
        
        for r_idx in queue_row_indices:
            # Col F (Column 6) is Provisioning_Status
            self.queue_ws.update_cell(r_idx, 6, "PROVISION_REQUESTED")
            
        print("✅ Sheet status updated successfully.")