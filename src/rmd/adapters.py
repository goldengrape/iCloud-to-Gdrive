import io
import uuid
from typing import Iterator, Optional, Tuple, Dict
from dataclasses import dataclass
from .models import TransferItem
from .verification import DriveFileMetadata

class SourceAdapter:
    def list_items(self) -> Iterator[TransferItem]:
        raise NotImplementedError

    def open_stream(self, record_id: str) -> Tuple[io.BytesIO, Dict]:
        raise NotImplementedError

@dataclass
class DriveUploadResult:
    target_drive_file_id: Optional[str] = None
    confirmed_offset: int = 0
    metadata: Optional[DriveFileMetadata] = None
    is_completed: bool = False
    error: Optional[str] = None

class TargetAdapter:
    def upload(self, item: TransferItem, stream: io.BytesIO, **kwargs) -> DriveUploadResult:
        raise NotImplementedError

class FakeSourceAdapter(SourceAdapter):
    def __init__(self, items: list[Tuple[TransferItem, bytes]]):
        self._items = items
        self._data_map = {item.record_id: data for item, data in items}

    def list_items(self) -> Iterator[TransferItem]:
        for item, _ in self._items:
            yield item

    def open_stream(self, record_id: str) -> Tuple[io.BytesIO, Dict]:
        data = self._data_map.get(record_id)
        if data is None:
            raise FileNotFoundError(f"Record {record_id} not found")
        return io.BytesIO(data), {"size": len(data)}

class FakeTargetAdapter(TargetAdapter):
    def __init__(self):
        self.uploaded_files = {} # file_id -> (metadata, data)

    def upload(self, item: TransferItem, stream: io.BytesIO, **kwargs) -> DriveUploadResult:
        data = stream.read()
        
        if len(data) != item.source_size:
            return DriveUploadResult(error="FAILED_SOURCE_READ")
            
        file_id = f"fake_drive_id_{uuid.uuid4().hex[:8]}"

        # Calculate real md5/sha256 of the uploaded data to simulate Drive
        import hashlib
        md5Checksum = hashlib.md5(data).hexdigest()
        sha256Checksum = hashlib.sha256(data).hexdigest()

        metadata = DriveFileMetadata(
            size=len(data),
            md5Checksum=md5Checksum,
            sha256Checksum=sha256Checksum
        )

        self.uploaded_files[file_id] = (metadata, data)

        return DriveUploadResult(
            target_drive_file_id=file_id,
            confirmed_offset=len(data),
            metadata=metadata,
            is_completed=True
        )
