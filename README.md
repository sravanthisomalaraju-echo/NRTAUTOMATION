# NRT Inventory Automation Framework

A Python and Selenium-based test automation framework using the Page Object Model (POM) design pattern. This tool automates the process of logging into the NRT web application, navigating the Block and TN Dashboards, extracting specific inventory data (e.g., Pending status), and reporting the data to the console, an HTML file, and a master Google Sheet.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
* **Python 3.10+**
* **Google Chrome** browser
* **Git** (or GitHub Desktop)

---

## 🚀 Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/your-username/NRTAUTOMATION.git](https://github.com/your-username/NRTAUTOMATION.git)
cd NRTAUTOMATION

2. Install required Python packages:
Run the following command to install the necessary libraries (Selenium, Tabulate, Google Auth, etc.):

Bash
pip install selenium webdriver-manager tabulate gspread google-auth requests urllib3
3. Configure Login Credentials:

Navigate to configfiles/common_variable.py.

Update the LOGIN_CONFIG dictionary with your valid application username and password.

4. Google Sheets API Configuration (Important):
To allow the script to write data to Google Sheets, you need a Service Account JSON key provided by the IT department.

Obtain the google_credentials.json file.

Place this file inside the configfiles/ directory.

Security Note: Ensure google_credentials.json is listed in your .gitignore file so it is never pushed to the remote repository.

Share the target Google Sheet with the Service Account email address as an "Editor".

💻 How to Run the Tests
The main execution script is located in the tests folder.

Run for the current date:

Bash
python tests/getDataTest.py
Run for a specific future/past date:
You can pass a specific effective date using the --date argument (Format: m/d/yyyy).

Bash
python tests/getDataTest.py --date 7/2/2026
Expected Output
Console: A formatted grid table displaying Block Number, TN, LataName, and CustomE.

HTML: A dict_table.html file generated in the root directory.

Google Sheets: The extracted rows will be appended to the next available empty row in the configured master spreadsheet.

Logs: Execution logs are saved in dynamically generated tests/Automation-YYYY-MM-DD/ folders.

📁 Project Structure
This framework strictly follows the Page Object Model (POM) to separate test logic from UI elements.

/base: Core Selenium WebDriver initialization and custom wrapper methods (e.g., explicit waits, custom clicks).

/pages: Page Object classes containing locators (XPath) and methods specific to individual web pages (e.g., login_page.py, navigation_basepage_menu_map.py).

/tests: The actual test scripts that orchestrate the browser actions and data extraction (e.g., getDataTest.py).

/configfiles: Environment variables, credentials, and configuration data.

/utilities: Helper tools for custom logging, data formatting, and test status tracking.

⚠️ Troubleshooting
Corporate Network / SSL Certificate Errors:
If you encounter an [SSL: CERTIFICATE_VERIFY_FAILED] error when the script attempts to download the ChromeDriver, this is likely due to the corporate VPN/Proxy.

Fix: The framework is configured to bypass this by setting os.environ['WDM_SSL_VERIFY'] = '0' inside base/webdriverfactory.py. An InsecureRequestWarning will appear in the console during execution; this is expected behavior and can be ignored.


***

### Next Steps

1.  Open your IDE or GitHub Desktop.
2.  Create a new file called `README.md` at the very top level of your project (the same place your `.gitattributes` file lives).
3.  Paste the markdown code above into it and save.
4.  Commit and push this new file to GitHub.