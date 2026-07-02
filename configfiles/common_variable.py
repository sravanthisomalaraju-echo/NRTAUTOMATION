import os

# os.environ.get() looks for the environment variable first (from GitHub Actions).
# If it doesn't find it, it falls back to the second value (for your local computer).

LOGIN_CONFIG = {
    'baseurl' : 'https://dish-nventory-temp.10xpeople.com/#/login', #test-setup
    'defaultloginusername': os.environ.get('PORTAL_USER', 'Sravanthi.Somalaraju@dish.com'),
    'defaultloginpassword': os.environ.get('PORTAL_PASS', 'Dish123!')
}

# ... any other variables you already have in this file ...
