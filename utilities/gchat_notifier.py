import os
import json
import requests
import urllib3
from dotenv import load_dotenv

# Suppress SSL verification warnings caused by corporate proxy inspection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env file automatically
load_dotenv()

class GChatNotifier:
    """Handles posting batch cease and provisioning requests to the Google Chat team space."""
    
    def __init__(self, webhook_url=None):
        self.webhook_url = (
            webhook_url 
            or os.getenv("PROVISIONING_WEBHOOK_URL") 
            or os.getenv("GCHAT_WEBHOOK_URL")
        )

    def send_batch_provision_cease_request(
        self, 
        cease_items, 
        provision_items, 
        start_row, 
        end_row, 
        tab_name="Priority Test numbers with effective dates", 
        workbook_name="Number Range Testing_MasterSheet",
        sheet_url=None,
        mentions="@Manuel Barraza [Contractor] @Daniel Limón [Contractor]"
    ):
        """Formats and posts dynamic SIM Cease & Provisioning requests with user action notes."""
        if not self.webhook_url or "YOUR_" in str(self.webhook_url):
            print("⚠️ GChat Webhook URL not configured. Skipping post.")
            return False

        # Fallback to .env sheet URL if not passed explicitly
        if not sheet_url:
            sheet_url = os.getenv("GSHEET_SPREADSHEET_URL") or "https://docs.google.com/spreadsheets/d/1aTK5U16BNNlm41djfyqrcjlHkeutTQot3EJfQ0_upqI/edit?gid=0#gid=0"

        has_cease = len(cease_items) > 0
        has_provision = len(provision_items) > 0

        if not has_cease and not has_provision:
            print("ℹ️ Neither cease nor provision items found to post.")
            return False

        # Format item blocks
        cease_block = "\n".join([f"{tn:<15} ICCID:{iccid}" for tn, iccid in cease_items]) if has_cease else ""
        prov_block = "\n".join([f"{tn:<15} ICCID:{iccid}" for tn, iccid in provision_items]) if has_provision else ""

        # Format row description string
        row_str = f"row {start_row}" if start_row == end_row else f"rows {start_row} to {end_row}"

        # Create Hyperlink for Google Chat
        sheet_link_text = f"<{sheet_url}|📊 {workbook_name}>" if sheet_url else f"📊 {workbook_name}"

        # ------------------------------------------------------------------
        # SCENARIO 1: BOTH CEASE & PROVISION
        # ------------------------------------------------------------------
        if has_cease and has_provision:
            message_text = (
                f"Hi, {mentions} please cease the following ICCIDs,\n\n"
                f"{cease_block}\n\n"
                f"and provision to the following numbers for number range testing. Prod env, Prov, OTA, ACC15.\n\n"
                f"{prov_block}\n\n"
                f"These are in {row_str} on {tab_name} Tab of\n"
                f"{sheet_link_text}\n\n"
                f"📌 *Note: Please mark Column G (SIM Provisioning status) & Column H (Cease status) as 'Done' in the sheet once completed.*"
            )

        # ------------------------------------------------------------------
        # SCENARIO 2: CEASE ONLY
        # ------------------------------------------------------------------
        elif has_cease and not has_provision:
            message_text = (
                f"Hi, {mentions} please cease the following ICCIDs,\n\n"
                f"{cease_block}\n\n"
                f"These are in {row_str} on {tab_name} Tab of\n"
                f"{sheet_link_text}\n\n"
                f"📌 *Note: Please mark Column H (Cease status) as 'Done' in the sheet once completed.*"
            )

        # ------------------------------------------------------------------
        # SCENARIO 3: PROVISION ONLY
        # ------------------------------------------------------------------
        else:
            message_text = (
                f"Hi {mentions} Please provision the following numbers for number range testing. Prov, OTA, ACC15.\n\n"
                f"{prov_block}\n\n"
                f"These are in {row_str} on {tab_name} Tab of\n"
                f"{sheet_link_text}\n\n"
                f"📌 *Note: Please mark Column G (SIM Provisioning status) as 'Done' in the sheet once completed.*"
            )

        payload = {"text": message_text}

        try:
            res = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json; charset=UTF-8"},
                timeout=10,
                verify=False  # Bypass corporate SSL interception
            )
            if res.status_code == 200:
                print("✅ GChat provisioning & cease request posted successfully!")
                return True
            else:
                print(f"❌ Webhook returned HTTP {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"⚠️ GChat Webhook Exception: {e}")
            return False