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
from datetime import datetime
from tabulate import tabulate
from pathlib import Path
import argparse


def argCheck():
    parser = argparse.ArgumentParser(description="Example script that accepts a date in m/d/yyyy format.")

    parser.add_argument(
        "--date",
        type=valid_date,
        default=valid_date(datetime.today().strftime("%m/%d/%Y")),  # default = today's date
        help="Date in m/d/yyyy format (e.g., 10/08/2025)."
    )

    args = parser.parse_args()
    #effectiveDate = args.date
    effectiveDate = args.date.strftime("%m/%d/%Y")

    return effectiveDate
    
def valid_date(date_str):
    """Validate date in m/d/yyyy format."""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date: '{date_str}'. Expected format: m/d/yyyy (e.g., 10/08/2025)"
        )

today_str = datetime.today().strftime("%m/%d/%Y")

effectiveDate = argCheck()  

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

    
    #today = datetime.today().strftime("%m/%d/%Y")
    #print(today)

    #today = "10/06/2025"
    today =  effectiveDate
    print("Effective date :: {0}".format(today))

    result = loginPageObj.inventory_gui_login(username,password)

    #if result == False:
    #    driver.quit()

    #print(driver.current_url)
    basepagenav.closeReleaseNote()

    #print(driver.current_url)
    master_dict, masterLst = basepagenav.getAllBlockListForDate(today)

    #print(master_dict)
    #print(masterLst)
    
    data = basepagenav.getTnBlockInfo("Arnold",masterLst)
    
    utilobj.sleep(4)

    driver.quit()
    
    print("")
    print("")
    print("Summary Table for Effective Date :: {0}".format(today))
    print("")
    headers = ['Block Number', 'TN ', 'LataName', 'CustomE']
    rows = [[key, *value] for key, value in data.items()]
    
    table = tabulate(rows, headers=headers, tablefmt='grid')

    print(table)

    html_content = basepagenav.dict_to_html_table(data)
    # Save to file
    output_file = Path("dict_table.html")
    output_file.write_text(html_content, encoding="utf-8")

    print(f"HTML table file generated: {output_file.resolve()}")
    

except Exception as e:
    print(e)
    driver.quit()
 