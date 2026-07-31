import os
import gspread

class GSheetManager:
    """Handles authentication and reading rows from the Master Tracker Google Sheet."""
    
    def __init__(self, json_cred_path, sheet_name="Number Range Testing_MasterSheet"):
        token_path = os.path.join(os.path.dirname(json_cred_path), "token.json")
        
        # Authenticate via OAuth if token exists, otherwise fall back to Service Account
        if os.path.exists(token_path):
            self.gc = gspread.oauth(
                credentials_filename=json_cred_path,
                authorized_user_filename=token_path
            )
        else:
            self.gc = gspread.service_account(filename=json_cred_path)
            
        self.sh = self.gc.open(sheet_name)

    def get_priority_test_numbers(self, tab_name="Priority Test numbers with effective dates"):
        """
        Scans the tab for active rows requiring provisioning/ceasing.
        Returns (start_row, end_row, cease_items, provision_items).
        """
        ws = self.sh.worksheet(tab_name)
        all_rows = ws.get_all_values()
        
        cease_items = []
        provision_items = []
        matched_indices = []

        # Row 1 is header, data starts at Row 2
        for idx, row in enumerate(all_rows[1:], start=2):
            if not row or len(row) < 4:
                continue
            
            tn = str(row[2]).strip()       # Col C: Phone_Number
            iccid = str(row[3]).strip()    # Col D: ICCID
            status = str(row[4]).strip() if len(row) > 4 else ""

            # Skip rows marked 'Block is already tested'
            if "block is already tested" in status.lower() or "block is already tested" in iccid.lower():
                continue

            if tn:
                matched_indices.append(idx)
                
                # If ICCID exists and is valid, queue for Cease
                if len(iccid) >= 15 and "null" not in iccid.lower():
                    cease_items.append((tn, iccid))
                
                # Queue for Provision
                provision_items.append((tn, iccid if len(iccid) >= 15 else "PENDING_ASSIGNMENT"))

        if not matched_indices:
            return None, None, [], []

        start_row = min(matched_indices)
        end_row = max(matched_indices)

        return start_row, end_row, cease_items, provision_items