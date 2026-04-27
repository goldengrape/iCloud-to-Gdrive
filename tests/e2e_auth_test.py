import sys
import os

# Ensure we can import from src/rmd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rmd.auth import GoogleAuthManager, KeyringTokenStorage

def main():
    print("Starting E2E Google Auth Test...")
    
    # 1. Initialize Storage & Manager
    storage = KeyringTokenStorage()
    
    # Check if client_secrets.json is present
    secrets_path = "client_secret.json"
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} not found.")
        print("Please place your Google Cloud OAuth Client Secrets file in the root directory to run this test.")
        return

    manager = GoogleAuthManager(storage, client_secrets_file=secrets_path)
    
    # 2. Login Flow
    print("\n[Action Required] You will be redirected to your browser to authorize access.")
    print("Please select the account and grant the requested drive.file permissions.")
    try:
        manager.login()
        print("\nLogin successful!")
    except Exception as e:
        print(f"\nLogin failed: {e}")
        return
        
    # 3. Retrieve Token
    token = manager.get_valid_token()
    if token:
        print(f"\nSuccessfully retrieved valid token (starts with: {token[:10]}...)")
    else:
        print("\nFailed to retrieve valid token after login.")
        
    print("\nE2E Test Completed. The token should now be stored in your Windows Credential Manager.")

if __name__ == "__main__":
    main()
