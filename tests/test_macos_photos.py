import pytest
from rmd.macos_photos import MockMacPhotosAdapter, MockPhotoAsset

def test_macos_photos_live_photo():
    assets = [MockPhotoAsset(local_id="L1", is_live_photo=True, is_raw=False, has_jpeg=False, filename="IMG_001.HEIC", metadata={})]
    adapter = MockMacPhotosAdapter(assets)
    items = list(adapter.list_items())
    assert len(items) == 2
    assert items[0].resource_group_id == items[1].resource_group_id == "group_L1"

def test_macos_photos_raw_jpeg():
    assets = [MockPhotoAsset(local_id="R1", is_live_photo=False, is_raw=True, has_jpeg=True, filename="IMG_002.CR2", metadata={})]
    adapter = MockMacPhotosAdapter(assets)
    items = list(adapter.list_items())
    assert len(items) == 2
    assert items[0].resource_group_id == items[1].resource_group_id == "group_R1"

def test_macos_photos_sidecar():
    assets = [MockPhotoAsset(local_id="S1", is_live_photo=False, is_raw=False, has_jpeg=False, filename="IMG_003.JPG", metadata={"album": "Vacation"})]
    adapter = MockMacPhotosAdapter(assets)
    items = list(adapter.list_items())
    assert len(items) == 2
    assert items[0].resource_kind == "photo"
    assert items[1].resource_kind == "sidecar"
    assert items[0].resource_group_id == items[1].resource_group_id == "group_S1"
