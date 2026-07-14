from datetime import datetime, timedelta
import argparse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    basepagenav.closeReleaseNote()

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

        # --- THE FIX: Close the dashboard via the UI before the next loop ---
        basepagenav.closeblockDashboardMenu()
        basepagenav.closeTnDashboardMenu()
        utilobj.sleep(2) # Give it 2 seconds to animate closing
        # --------------------------------------------------------------------

except Exception as e:
    print(f"An error occurred during execution: {e}")

finally:
    # Always close the browser when finished, even if an error occurs
    driver.quit()
    print("Browser closed successfully.")