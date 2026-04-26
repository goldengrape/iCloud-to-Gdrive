import pytest
from rmd.auth import GoogleAuthManager, DummyTokenStorage

def test_google_auth_manager_scopes():
    # TDD-TEST-008: drive.file 权限
    storage = DummyTokenStorage()
    manager = GoogleAuthManager(storage)
    auth_url = manager.get_auth_url()
    assert "https://www.googleapis.com/auth/drive.file" in auth_url

def test_google_auth_manager_token_storage():
    storage = DummyTokenStorage()
    manager = GoogleAuthManager(storage)

    assert manager.get_valid_token() is None

    manager.handle_auth_callback("mock_auth_code_123")

    assert manager.get_valid_token() == "mock_access_token_for_mock_auth_code_123"

def test_token_storage_security():
    # TDD-TEST-001: 不收集 Apple ID 密码
    storage = DummyTokenStorage()
    with pytest.raises(ValueError):
        storage.save_token({"apple_password": "secret_password"})
