import io
import os
from rmd.auth import GoogleAuthManager, KeyringTokenStorage
from rmd.drive import RealGoogleDriveAdapter
from rmd.models import TransferItem

def run_e2e_upload():
    print("Starting E2E Real Google Drive Upload Test...")
    
    # Initialize Auth Manager
    storage = KeyringTokenStorage(service_name="icloud_to_gdrive", username="google_drive_oauth_token")
    auth_manager = GoogleAuthManager(storage=storage, client_secrets_file="client_secret.json")
    
    # Ensure logged in
    creds = auth_manager.get_credentials()
    if not creds or not creds.valid:
        print("Credentials invalid or missing. Attempting login...")
        auth_manager.login()
        creds = auth_manager.get_credentials()
        if not creds or not creds.valid:
            print("Failed to obtain valid credentials.")
            return
    print("Authentication successful.")

    # Create dummy data (about 6MB to force multipart)
    print("Generating 6MB dummy file data in memory...")
    size = 6 * 1024 * 1024
    dummy_data = os.urandom(size)
    stream = io.BytesIO(dummy_data)
    
    item = TransferItem(
        task_id="e2e_task",
        record_id="e2e_record",
        source_type="icloud",
        source_display_name="e2e_test_upload.bin",
        resource_kind="file",
        source_size=size
    )
    
    adapter = RealGoogleDriveAdapter(auth_manager=auth_manager)
    print("Uploading to Google Drive (folder: iCloud-to-Gdrive-Migration)...")
    result = adapter.upload(item, stream)
    
    if result.is_completed:
        print(f"Upload complete! Drive File ID: {result.target_drive_file_id}")
        print(f"Metadata received: {result.metadata}")
    else:
        print(f"Upload failed or incomplete. Result: {result}")
        if result.error:
            print(f"Error detail: {result.error}")

if __name__ == "__main__":
    run_e2e_upload()
