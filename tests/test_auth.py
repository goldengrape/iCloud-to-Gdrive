import pytest
from unittest.mock import patch, MagicMock
from rmd.auth import GoogleAuthManager, DummyTokenStorage, KeyringTokenStorage
import json

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

@patch('rmd.auth.keyring')
def test_keyring_token_storage(mock_keyring):
    storage = KeyringTokenStorage()
    
    # Test saving
    token_data = {"token": "my_secure_token", "scopes": ["scope1"]}
    storage.save_token(token_data)
    mock_keyring.set_password.assert_called_once_with(
        "icloud_to_gdrive", 
        "google_drive_oauth_token", 
        json.dumps(token_data)
    )
    
    # Test loading
    mock_keyring.get_password.return_value = json.dumps(token_data)
    loaded_token = storage.load_token()
    assert loaded_token == token_data
    mock_keyring.get_password.assert_called_once_with("icloud_to_gdrive", "google_drive_oauth_token")
    
    # Test security interception
    with pytest.raises(ValueError):
        storage.save_token({"apple_id": "user@example.com"})

@patch('rmd.auth.InstalledAppFlow')
@patch('rmd.auth.os.path.exists')
def test_real_google_auth_login(mock_exists, mock_flow_class):
    mock_exists.return_value = True
    
    mock_flow_instance = MagicMock()
    mock_flow_class.from_client_secrets_file.return_value = mock_flow_instance
    
    mock_creds = MagicMock()
    mock_creds.token = "real_access_token"
    mock_creds.refresh_token = "real_refresh"
    mock_creds.token_uri = "https://oauth2.googleapis.com/token"
    mock_creds.client_id = "client123"
    mock_creds.client_secret = "secret123"
    mock_creds.scopes = ["scope"]
    mock_creds.valid = True
    mock_flow_instance.run_local_server.return_value = mock_creds

    storage = DummyTokenStorage()
    manager = GoogleAuthManager(storage, client_secrets_file="dummy_secret.json")
    
    # Trigger login
    manager.login()
    
    # Assert flow was called correctly
    mock_flow_class.from_client_secrets_file.assert_called_once_with(
        "dummy_secret.json", scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    mock_flow_instance.run_local_server.assert_called_once_with(port=0)
    
    # Assert token was saved
    assert storage.load_token()["token"] == "real_access_token"
    
    # Assert we can get it back
    assert manager.get_valid_token() == "real_access_token"
