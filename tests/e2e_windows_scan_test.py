import os
import sys
from pathlib import Path
from rmd.windows_drive import RealWindowsICloudAdapter
from rmd.models import TransferItem

def run_e2e_scan():
    print("Starting E2E Real Windows iCloud Local File Scanning Test...")
    
    # Try to find default iCloud Drive
    user_home = Path.home()
    icloud_path = user_home / "iCloudDrive"
    
    if not icloud_path.exists():
        print(f"Skipping test: {icloud_path} does not exist.")
        print("Please ensure iCloud Drive is installed and configured on this Windows machine.")
        return

    print(f"Scanning target directory: {icloud_path}")
    adapter = RealWindowsICloudAdapter(root_dir=str(icloud_path))
    
    ready_count = 0
    placeholder_count = 0
    
    try:
        items = list(adapter.list_items())
    except Exception as e:
        print(f"Failed to scan directory: {e}")
        return
        
    for item in items:
        if isinstance(item, TransferItem):
            ready_count += 1
            # print(f"[READY] {item.source_display_name} ({item.source_size} bytes)")
        else:
            placeholder_count += 1
            # print(f"[OFFLINE] {item.path} - {item.message}")
            
    print(f"\nScan completed!")
    print(f"Total ready files to upload: {ready_count}")
    print(f"Total offline placeholder files skipped: {placeholder_count}")
    
    if ready_count == 0 and placeholder_count == 0:
        print("Warning: The iCloud Drive folder appears to be completely empty.")

if __name__ == "__main__":
    run_e2e_scan()
