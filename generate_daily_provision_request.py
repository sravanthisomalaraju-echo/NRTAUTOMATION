import os
import sys
from utilities.gsheet_manager import GSheetManager
from utilities.gchat_notifier import GChatNotifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_CREDENTIALS = os.path.join(BASE_DIR, "credentials.json")

# Environment variable read (for GitHub Actions) with local fallback
PROVISIONING_WEBHOOK_URL = os.environ.get(
    "PROVISIONING_WEBHOOK_URL",
    "https://chat.googleapis.com/v1/spaces/AAQAc2bhlGg/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Ga-r-XrNzwAxm8GU_jlFfRzRdBChAqiMUntm_gd74-Q"
)

WORKBOOK_NAME = "Number Range Testing_MasterSheet"
TAB_NAME = "Priority Test numbers with effective dates"

def main():
    print("🚀 Starting Daily Provisioning Request Generator...")
    
    # 1. Initialize Sheet Reader
    gsheet = GSheetManager(JSON_CREDENTIALS, sheet_name=WORKBOOK_NAME)
    
    # 2. Extract Active Row Data
    start_row, end_row, cease_list, provision_list = gsheet.get_priority_test_numbers(TAB_NAME)
    
    if not start_row:
        print("😴 No pending effective rows found to process. Exiting.")
        return

    print(f"📊 Found active rows from Row {start_row} to Row {end_row}.")
    print(f"   • Cease Items: {len(cease_list)}")
    print(f"   • Provision Items: {len(provision_list)}")

    # 3. Post to Google Chat
    notifier = GChatNotifier(PROVISIONING_WEBHOOK_URL)
    notifier.send_batch_provision_cease_request(
        cease_items=cease_list,
        provision_items=provision_list,
        start_row=start_row,
        end_row=end_row,
        tab_name=TAB_NAME,
        workbook_name=WORKBOOK_NAME
    )

if __name__ == "__main__":
    main()