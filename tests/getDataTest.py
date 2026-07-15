from datetime import datetime, timedelta
import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gspread
from google.oauth2.credentials import Credentials
from pages.home.navigation_basepage_menu_map import NavigationBasePageMenuMap
from utilities.teststatus import TsStatus
import time
from utilities.util import Util
from utilities.generic_utils import GenericFileUtils
from base.webdriverfactory import WebDriverFactory
from configfiles.common_variable import *
from pages.home.login_page import LoginPage
from tabulate import tabulate
from pathlib import Path


def valid_date(date_str):
    """Validate date in m/d/yyyy format."""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date: '{date_str}'. Expected format: m/d/yyyy (e.g., 10/08/2025)"
        )

def get_dates_to_run():
    """Parses command line arguments and returns a list of dates to process."""
    parser = argparse.ArgumentParser(description="Run NRT Automation for a date range")
    parser.add_argument('--start-date', type=valid_date, help='Start date (e.g., m/d/yyyy)')
    parser.add_argument('--end-date', type=valid_date, help='End date (e.g., m/d/yyyy)')
    parser.add_argument(
        "--date",
        type=valid_date,
        default=datetime.today().date(),  # default = today's date
        help="Date in m/d/yyyy format (e.g., 10/08/2025)."
    )

    args = parser.parse_args()
    dates_to_run = []

    # If user provided a range
    if args.start_date and args.end_date:
        current = args.start_date
        while current <= args.end_date:
            # FIX: Format strictly as MM/DD/YYYY (with leading zeros)
            formatted_date = current.strftime("%m/%d/%Y")
            dates_to_run.append(formatted_date)
            current += timedelta(days=1)
    else:
        # Fallback to single date or today (also strictly MM/DD/YYYY)
        formatted_date = args.date.strftime("%m/%d/%Y")
        dates_to_run.append(formatted_date)

    return dates_to_run


# ==========================================
# --- MAIN SCRIPT EXECUTION ---
# ==========================================

dates_to_run = get_dates_to_run()
print(f"Dates queued for extraction: {dates_to_run}")

wdfobj = WebDriverFactory(browser="chrome")
driver = wdfobj.getWebDriverInstance()

username = LOGIN_CONFIG['defaultloginusername']
password = LOGIN_CONFIG['defaultloginpassword']

try:
    loginPageObj = LoginPage(driver)
    tsObj = TsStatus(driver)
    basepagenav = NavigationBasePageMenuMap(driver)
    utilobj = Util()
    genericutilobj = GenericFileUtils()

    # 1. Login ONCE at the start of the script
    result = loginPageObj.inventory_gui_login(username, password)
    print("Waiting for 10 seconds to allow cloud dashboard to fully render...")
    time.sleep(10)
    basepagenav.closeReleaseNote()
    print("Closing release note...")
    time.sleep(2)



    # 2. Loop through every date requested
    for target_date in dates_to_run:
        print(f"\n=========================================")
        print(f"--- RUNNING EXTRACTION FOR: {target_date} ---")
        print(f"=========================================\n")

        # --- THE FIX: Force a hard refresh to wipe the SPA state ---
        driver.refresh()
        utilobj.sleep(5) # Give the web app 5 seconds to completely reload the UI
        # -----------------------------------------------------------

        master_dict, masterLst = basepagenav.getAllBlockListForDate(target_date)
        
        # Scrape block info
        data = basepagenav.getTnBlockInfo("Arnold", masterLst)
        utilobj.sleep(4)

        # 3. Print the Console Table
        print("\nSummary Table for Effective Date :: {0}".format(target_date))
        headers = ['Block Number', 'TN ', 'LataName', 'CustomE']
        rows = [[key, *value] for key, value in data.items()]
        
        table = tabulate(rows, headers=headers, tablefmt='grid')
        print(table)

        # 4. Generate the HTML File (Named uniquely by date)
        date_safe_str = target_date.replace('/', '-')
        html_content = basepagenav.dict_to_html_table(data)
        
        output_file = Path(f"dict_table_{date_safe_str}.html")
        output_file.write_text(html_content, encoding="utf-8")
        print(f"HTML table file generated: {output_file.resolve()}")

        # 5. GOOGLE SHEETS CODE CAN GO HERE LATER
        # (It will execute once for every date in the loop)
        # 5. PUSH TO GOOGLE SHEETS
        print("Pushing extracted data to Google Sheets...")
        try:
            # 5a. Set up Authentication using your new Refresh Token
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Now it reads the token.json file you just generated!
            creds = Credentials.from_authorized_user_file("token.json", scopes)
            client = gspread.authorize(creds)
            
            # 5b. Connect to the specific Workbook and Tab
            sheet_name = "Number Range Testing in MW Shift in MDT Time"
            tab_name = "Priority Test numbers with effective dates"
            
            spreadsheet = client.open(sheet_name)
            worksheet = spreadsheet.worksheet(tab_name)
            
            # --- SMART UPSERT LOGIC START ---
            print("Downloading sheet data to check for existing records...")
            
            # 1. Download the ENTIRE sheet data in one fast API call
            all_sheet_data = worksheet.get_all_values()
            
            existing_records = set()
            tested_npa_nxx = set()
            
            # 2. Map out what is already in the sheet
            for row in all_sheet_data[1:]:  # Skip the header row
                if len(row) >= 3:
                    # Normalize dates so "07/14/2026" matches "7/14/2026" from your sheet
                    sheet_date = row[0].strip()
                    parts = sheet_date.split('/')
                    if len(parts) == 3:
                        sheet_date = f"{int(parts[0])}/{int(parts[1])}/{parts[2]}"
                        
                    sheet_block = row[1].strip()
                    sheet_tn = row[2].strip()
                    
                    # Store exact matches (Date, Block, TN) in our bot's memory
                    existing_records.add((sheet_date, sheet_block, sheet_tn))
                    
                    # Store the first 6 digits for the "Already Tested" check
                    if len(sheet_block) >= 6:
                        tested_npa_nxx.add(sheet_block[:6])

            # Normalize our scraped target_date to match the sheet format
            t_parts = target_date.split('/')
            normalized_target_date = f"{int(t_parts[0])}/{int(t_parts[1])}/{t_parts[2]}"

            # 5c. Format and Filter the scraped data
            rows_to_append = []
            for block_number, values in data.items():
                tn = values[0]
                
                # CHECK 1: Does this exact record already exist for this date?
                if (normalized_target_date, block_number, tn) in existing_records:
                    print(f"  -> Skipping {block_number}: Already verified in sheet for {normalized_target_date}.")
                    continue  # This skips the block and moves to the next one!
                
                # CHECK 2: If it's a NEW record, check if the 6-digit NPA-NXX was tested before
                current_npa_nxx = str(block_number)[:6]
                if current_npa_nxx in tested_npa_nxx:
                    status_message = "Block is already tested"
                else:
                    status_message = "" 
                    tested_npa_nxx.add(current_npa_nxx) # Add it so we catch same-day duplicates too
                
                # row = [Col A, Col B, Col C, Col D]
                # We use target_date to keep the format consistent with however you ran the script
                row = [target_date, block_number, tn, status_message]
                rows_to_append.append(row)
                
            # 5d. Bulk append the data to the bottom of the sheet
            if rows_to_append:
                worksheet.append_rows(rows_to_append)
                print(f"✅ Successfully appended {len(rows_to_append)} NEW rows to Google Sheets for {target_date}!")
            else:
                print(f"✅ All records for {target_date} are already up to date in Google Sheets. No new data appended.")
                
        except Exception as e:
            print(f"❌ Failed to update Google Sheets: {e}")
                

        # --- THE FIX: Close the dashboard via the UI before the next loop ---
        basepagenav.closeblockDashboardMenu()
        basepagenav.closeTnDashboardMenu()
        utilobj.sleep(2) # Give it 2 seconds to animate closing
        # --------------------------------------------------------------------

except Exception as e:
    print(f"An error occurred during execution: {e}")

finally:
    print("Taking a screenshot of the final browser state...")
    try:
        if driver:
            driver.save_screenshot("cloud_error.png")
    except Exception as e:
        print("Could not take screenshot:", e)
        
    print("Initiating browser teardown...")
    try:
        # Force-close the active tab first to instantly sever the web app's connection
        if driver:
            driver.close()
            utilobj.sleep(1)
    except Exception as e:
        pass # Ignore errors if the window is already gone
        
    try:
        # Now kill the background driver process
        if driver:
            driver.quit()
    except Exception as e:
        pass
        
    print("Browser closed successfully.")