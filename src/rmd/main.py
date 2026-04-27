import argparse
import sys
import uuid
import os
from datetime import datetime
from rmd.auth import GoogleAuthManager, KeyringTokenStorage
from rmd.windows_drive import RealWindowsICloudAdapter
from rmd.drive import RealGoogleDriveAdapter
from rmd.store import TaskStore, ManifestWriter
from rmd.engine import MigrationEngine

def main():
    parser = argparse.ArgumentParser(description="iCloud to Google Drive Migration Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Start the migration process")
    migrate_parser.add_argument("--source", type=str, default=r"~\iCloudDrive", help="Source directory (default: ~\\iCloudDrive)")
    migrate_parser.add_argument("--client-secret", type=str, default="client_secret.json", help="Path to Google OAuth client secret JSON")
    migrate_parser.add_argument("--db-path", type=str, default="migration.db", help="Path to SQLite database for state management")
    
    args = parser.parse_args()
    
    if args.command == "migrate":
        run_migration(args)
    else:
        parser.print_help()

def run_migration(args):
    print("=" * 50)
    print("iCloud to Google Drive Migration")
    print("=" * 50)
    
    # 1. Setup Auth
    print(f"Initializing Google Auth (client secret: {args.client_secret})...")
    storage = KeyringTokenStorage(service_name="icloud_to_gdrive", username="google_drive_oauth_token")
    auth_manager = GoogleAuthManager(storage=storage, client_secrets_file=args.client_secret)
    
    creds = auth_manager.get_credentials()
    if not creds or not creds.valid:
        print("Credentials invalid or missing. Launching browser login...")
        try:
            auth_manager.login()
        except Exception as e:
            print(f"Login failed: {e}")
            sys.exit(1)
            
    print("Authentication successful.")
    
    # 2. Setup Adapters
    source_path = os.path.expanduser(args.source)
    print(f"Scanning source directory: {source_path}")
    source_adapter = RealWindowsICloudAdapter(root_dir=source_path)
    target_adapter = RealGoogleDriveAdapter(auth_manager=auth_manager)
    
    # 3. Setup Store and Engine
    print(f"Using state database: {args.db_path}")
    store = TaskStore(db_path=args.db_path)
    engine = MigrationEngine(source=source_adapter, target=target_adapter, store=store)
    
    # 4. Run Migration
    # We will use a consistent task ID for today to ensure resume works simply for testing,
    # or just use a new one. But store.list_records(task_id) depends on it. 
    # For now, let's just make it a single task id or pass it via args.
    # We can default to "default_migration_task" so resuming picks up records from before,
    # because ManifestWriter exports by task_id.
    task_id = "default_migration_task"
    
    try:
        engine.run(task_id)
    except KeyboardInterrupt:
        print("\nMigration paused by user. You can resume later by running the command again.")
    except Exception as e:
        print(f"\nMigration encountered a fatal error: {e}")
        
    # 5. Finalize Manifest
    print("\nGenerating final manifest reports...")
    records = store.list_records(task_id)
    if not records:
        print("No records processed in this session.")
        return
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = f"manifest_{timestamp}.json"
    csv_path = f"manifest_{timestamp}.csv"
    manifest_hash = ManifestWriter.finalize(records, json_path, csv_path)
    
    print(f"Manifest exported:")
    print(f"  JSON: {json_path}")
    print(f"  CSV: {csv_path}")
    print(f"  SHA256: {manifest_hash}")
    print("Migration completed successfully!")

if __name__ == "__main__":
    main()
