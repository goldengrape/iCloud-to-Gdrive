import sqlite3
import json
import hashlib
import csv
from typing import List, Optional
from datetime import datetime, timezone
from dataclasses import asdict
from .models import ManifestRecord, MigrationStatus, DriveUploadSession

class TaskStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS manifest_records (
                    task_id TEXT,
                    record_id TEXT PRIMARY KEY,
                    source_type TEXT,
                    source_stable_id TEXT,
                    source_path TEXT,
                    source_display_name TEXT,
                    source_size INTEGER,
                    source_mtime TEXT,
                    source_md5 TEXT,
                    source_sha256 TEXT,
                    resource_group_id TEXT,
                    resource_kind TEXT,
                    package_original_file_count INTEGER,
                    package_original_total_size INTEGER,
                    target_drive_file_id TEXT,
                    target_parent_folder_id TEXT,
                    target_path TEXT,
                    target_size INTEGER,
                    target_md5 TEXT,
                    target_sha1 TEXT,
                    target_sha256 TEXT,
                    target_head_revision_id TEXT,
                    target_web_view_link TEXT,
                    status TEXT,
                    failure_reason TEXT,
                    retry_count INTEGER,
                    started_at TEXT,
                    uploaded_at TEXT,
                    verified_at TEXT,
                    record_hash TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS upload_sessions (
                    record_id TEXT PRIMARY KEY,
                    upload_session_uri TEXT,
                    target_parent_folder_id TEXT,
                    target_drive_file_id TEXT,
                    confirmed_offset INTEGER,
                    session_created_at TEXT,
                    last_checked_at TEXT,
                    expires_at_estimate TEXT
                )
            """)

    def save_record(self, record: ManifestRecord):
        data = asdict(record)
        data['status'] = record.status.value

        cols = list(data.keys())
        placeholders = ",".join(["?" for _ in cols])

        sql = f"INSERT OR REPLACE INTO manifest_records ({','.join(cols)}) VALUES ({placeholders})"
        with self.conn:
            self.conn.execute(sql, list(data.values()))

    def get_record(self, record_id: str) -> Optional[ManifestRecord]:
        cur = self.conn.execute("SELECT * FROM manifest_records WHERE record_id = ?", (record_id,))
        row = cur.fetchone()
        if not row:
            return None

        data = dict(row)
        data['status'] = MigrationStatus(data['status'])
        return ManifestRecord(**data)

    def list_records(self, task_id: str) -> List[ManifestRecord]:
        cur = self.conn.execute("SELECT * FROM manifest_records WHERE task_id = ?", (task_id,))
        records = []
        for row in cur.fetchall():
            data = dict(row)
            data['status'] = MigrationStatus(data['status'])
            records.append(ManifestRecord(**data))
        return records

    def save_upload_session(self, session: DriveUploadSession):
        data = asdict(session)
        cols = list(data.keys())
        placeholders = ",".join(["?" for _ in cols])
        sql = f"INSERT OR REPLACE INTO upload_sessions ({','.join(cols)}) VALUES ({placeholders})"
        with self.conn:
            self.conn.execute(sql, list(data.values()))

    def get_upload_session(self, record_id: str) -> Optional[DriveUploadSession]:
        cur = self.conn.execute("SELECT * FROM upload_sessions WHERE record_id = ?", (record_id,))
        row = cur.fetchone()
        if not row:
            return None
        return DriveUploadSession(**dict(row))


class ManifestWriter:
    @staticmethod
    def _compute_record_hash(data: dict) -> str:
        # Generate a stable hash for a record excluding the hash itself
        hash_data = {k: v for k, v in data.items() if k != "record_hash" and v is not None}
        # sort keys for stability
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    @classmethod
    def finalize(cls, records: List[ManifestRecord], json_path: str, csv_path: str) -> str:
        manifest_data = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "record_count": len(records)
            },
            "records": []
        }

        # JSON output
        for record in records:
            data = asdict(record)
            data['status'] = record.status.value
            data['record_hash'] = cls._compute_record_hash(data)
            record.record_hash = data['record_hash'] # Update object
            manifest_data["records"].append(data)

        json_bytes = json.dumps(manifest_data, indent=2).encode('utf-8')
        manifest_sha256 = hashlib.sha256(json_bytes).hexdigest()
        manifest_data["metadata"]["manifest_sha256"] = manifest_sha256

        # re-dump with manifest hash
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)

        # CSV output
        if records:
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                headers = list(asdict(records[0]).keys())
                writer.writerow(headers)
                for record in records:
                    row_data = asdict(record)
                    row_data['status'] = record.status.value
                    writer.writerow([row_data.get(h, "") for h in headers])

        return manifest_sha256
