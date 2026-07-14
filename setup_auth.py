from google_auth_oauthlib.flow import InstalledAppFlow

# These are the permissions we are asking for
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

print("Opening browser for one-time authentication...")

# This reads IT's file and opens your browser
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
creds = flow.run_local_server(port=0)

# This saves your permanent Refresh Token!
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ SUCCESS! 'token.json' has been created. You never have to do this again.")