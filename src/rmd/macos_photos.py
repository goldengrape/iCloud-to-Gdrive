import io
import uuid
from typing import Iterator, Tuple, Dict, List
from dataclasses import dataclass
from .models import TransferItem
from .adapters import SourceAdapter

@dataclass
class MockPhotoAsset:
    local_id: str
    is_live_photo: bool
    is_raw: bool
    has_jpeg: bool
    filename: str
    metadata: Dict

class MockMacPhotosAdapter(SourceAdapter):
    def __init__(self, assets: List[MockPhotoAsset]):
        self.assets = assets

    def list_items(self) -> Iterator[TransferItem]:
        for asset in self.assets:
            group_id = f"group_{asset.local_id}" if (asset.is_live_photo or (asset.is_raw and asset.has_jpeg) or asset.metadata) else None

            # URD-REQ-011: Live Photo
            if asset.is_live_photo:
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}_still",
                    source_type="icloud_photos", source_display_name=asset.filename,
                    resource_kind="live_photo_still", source_size=100, resource_group_id=group_id
                )
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}_video",
                    source_type="icloud_photos", source_display_name=asset.filename.replace(".JPG", ".MOV").replace(".HEIC", ".MOV"),
                    resource_kind="live_photo_video", source_size=500, resource_group_id=group_id
                )
            # URD-REQ-011: RAW+JPEG
            elif asset.is_raw and asset.has_jpeg:
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}_raw",
                    source_type="icloud_photos", source_display_name=asset.filename,
                    resource_kind="raw", source_size=2000, resource_group_id=group_id
                )
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}_jpeg",
                    source_type="icloud_photos", source_display_name=asset.filename.split('.')[0] + ".JPG",
                    resource_kind="photo", source_size=300, resource_group_id=group_id
                )
            else:
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}",
                    source_type="icloud_photos", source_display_name=asset.filename,
                    resource_kind="photo", source_size=150, resource_group_id=group_id
                )

            # Sidecar
            if asset.metadata:
                yield TransferItem(
                    task_id="current_task", record_id=f"rec_{asset.local_id}_sidecar",
                    source_type="icloud_photos", source_display_name=asset.filename + ".json",
                    resource_kind="sidecar", source_size=10, resource_group_id=group_id
                )

    def open_stream(self, record_id: str) -> Tuple[io.BytesIO, Dict]:
        return io.BytesIO(b"mock_data"), {"size": 9}
