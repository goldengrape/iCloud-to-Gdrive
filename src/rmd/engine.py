import time
from typing import Optional
from datetime import datetime, timezone
from rmd.models import TransferItem, MigrationStatus, ManifestRecord
from rmd.adapters import SourceAdapter, TargetAdapter
from rmd.store import TaskStore
from rmd.verification import VerificationEngine, SourceDigest

class MigrationEngine:
    def __init__(self, source: SourceAdapter, target: TargetAdapter, store: TaskStore):
        self.source = source
        self.target = target
        self.store = store

    def run(self, task_id: str):
        print(f"Starting migration task: {task_id}")
        
        for item in self.source.list_items():
            # For dynamic imports or generic handling, use duck typing or class names instead of direct import
            if type(item).__name__ == "WinFileEvent":
                # Placeholder
                record = self.store.get_record(item.record_id)
                if not record:
                    record = ManifestRecord(
                        task_id=task_id,
                        record_id=item.record_id,
                        source_type="icloud_drive",
                        source_stable_id=item.record_id,
                        source_path=item.path,
                        source_display_name=item.path.split('\\')[-1] if '\\' in item.path else item.path.split('/')[-1],
                        source_size=0,
                        resource_kind="file",
                        status=MigrationStatus.TRANSFERRING,
                        failure_reason=item.message,
                        started_at=datetime.now(timezone.utc).isoformat(),
                        record_hash=""
                    )
                else:
                    record.status = item.status
                    record.failure_reason = item.message
                self.store.save_record(record)
                print(f"Skipped placeholder: {item.path}")
                continue
                
            if isinstance(item, TransferItem):
                self._process_item(item, task_id)
                
    def _process_item(self, item: TransferItem, task_id: str):
        # 1. Check if already successfully verified
        record = self.store.get_record(item.record_id)
        if record and record.status == MigrationStatus.VERIFIED_MATCH:
            print(f"Skipping already verified file: {item.source_display_name}")
            return

        # 2. Open stream
        try:
            stream, meta = self.source.open_stream(item.record_id)
        except Exception as e:
            print(f"Failed to open source stream for {item.source_display_name}: {e}")
            if not record:
                record = self._create_initial_record(item, task_id)
            record.status = MigrationStatus.FAILED_SOURCE_READ
            record.failure_reason = f"Stream open error: {str(e)}"
            self.store.save_record(record)
            return

        # 3. Calculate hash
        print(f"Calculating hash for {item.source_display_name}...")
        try:
            digest = VerificationEngine.calculate_digest_from_stream(stream)
            stream.seek(0)
        except Exception as e:
            print(f"Failed to calculate hash for {item.source_display_name}: {e}")
            stream.close()
            if not record:
                record = self._create_initial_record(item, task_id)
            record.status = MigrationStatus.FAILED_SOURCE_READ
            record.failure_reason = f"Hash calculation error: {str(e)}"
            self.store.save_record(record)
            return

        # 4. Initialize record and set to TRANSFERRING
        if not record:
            record = self._create_initial_record(item, task_id)
        
        record.source_size = digest.size
        record.source_md5 = digest.md5
        record.source_sha256 = digest.sha256
        record.status = MigrationStatus.TRANSFERRING
        record.retry_count = (record.retry_count or 0) + 1
        record.started_at = record.started_at or datetime.now(timezone.utc).isoformat()
        
        self.store.save_record(record)

        # 5. Upload
        print(f"Uploading {item.source_display_name}...")
        try:
            result = self.target.upload(item, stream)
        finally:
            stream.close()

        # 6. Check upload result
        if not result.is_completed:
            record.status = MigrationStatus.FAILED_UPLOAD
            record.failure_reason = result.error or "Upload incomplete"
            self.store.save_record(record)
            print(f"Upload failed: {record.failure_reason}")
            return

        # 7. Verification
        record.uploaded_at = datetime.now(timezone.utc).isoformat()
        record.target_drive_file_id = result.target_drive_file_id
        record.target_size = result.metadata.size if result.metadata else None
        
        if result.metadata:
            record.target_md5 = result.metadata.md5Checksum
            record.target_sha256 = result.metadata.sha256Checksum
            record.target_head_revision_id = result.metadata.headRevisionId

            status = VerificationEngine.verify(digest, result.metadata)
            record.status = status
            record.verified_at = datetime.now(timezone.utc).isoformat()
            
            if status == MigrationStatus.VERIFIED_MATCH or status == MigrationStatus.VERIFIED_WEAK:
                print(f"Successfully verified {item.source_display_name}.")
            else:
                record.failure_reason = "Verification mismatch"
                print(f"Verification failed for {item.source_display_name}: {status.value}")
        else:
            record.status = MigrationStatus.FAILED_TARGET_VERIFY
            record.failure_reason = "No target metadata returned"
            print(f"Failed to verify {item.source_display_name}: No metadata")

        self.store.save_record(record)

    def _create_initial_record(self, item: TransferItem, task_id: str) -> ManifestRecord:
        return ManifestRecord(
            task_id=task_id,
            record_id=item.record_id,
            source_type=item.source_type,
            source_stable_id=item.record_id,
            source_path=item.source_path,
            source_display_name=item.source_display_name,
            source_size=item.source_size,
            resource_kind=item.resource_kind,
            status=MigrationStatus.TRANSFERRING,
            started_at=datetime.now(timezone.utc).isoformat(),
            record_hash=""
        )
