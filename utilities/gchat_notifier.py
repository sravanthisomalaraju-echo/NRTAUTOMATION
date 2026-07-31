import json
import requests

class GChatNotifier:
    """Handles posting batch cease and provisioning requests to the Google Chat team space."""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_batch_provision_cease_request(
        self, 
        cease_items, 
        provision_items, 
        start_row, 
        end_row, 
        tab_name="Priority Test numbers with effective dates", 
        workbook_name="Number Range Testing_MasterSheet",
        mentions="Manuel Barraza [Contractor] Daniel Limón [Contractor]"
    ):
        """Formats and posts the exact team template for SIM Cease & Provisioning requests."""
        if not self.webhook_url or "YOUR_" in self.webhook_url:
            print("⚠️ GChat Webhook URL not configured. Skipping post.")
            return False

        # Format Cease Section
        cease_block = "\n".join([f"{tn:<15} ICCID:{iccid}" for tn, iccid in cease_items]) if cease_items else "None"

        # Format Provision Section
        prov_block = "\n".join([f"{tn:<15} ICCID:{iccid}" for tn, iccid in provision_items]) if provision_items else "None"

        # Assemble Exact Team Template
        message_text = (
            f"Hi, {mentions} please cease the following ICCIDs,\n\n\n"
            f"{cease_block}\n\n"
            f"and provision to the following numbers for number range testing. Prod env, Prov, OTA, ACC15.\n\n\n"
            f"{prov_block}\n\n\n"
            f"These are in rows {start_row} to {end_row} on {tab_name} Tab of\n"
            f"📊 {workbook_name}"
        )

        payload = {"text": message_text}

        try:
            res = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json; charset=UTF-8"}
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