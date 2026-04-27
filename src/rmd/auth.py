import json
import os
import keyring
from typing import Optional, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class TokenStorage:
    def save_token(self, token_data: Dict) -> None:
        raise NotImplementedError

    def load_token(self) -> Optional[Dict]:
        raise NotImplementedError

class DummyTokenStorage(TokenStorage):
    def __init__(self):
        self._token = None

    def save_token(self, token_data: Dict) -> None:
        # TDD-TEST-020: 确保 token 不进入普通日志（这里只做内存存储模拟安全存储）
        if "apple_id" in token_data or "apple_password" in token_data:
            raise ValueError("Credentials cannot contain Apple ID/password")
        self._token = token_data

    def load_token(self) -> Optional[Dict]:
        return self._token

class KeyringTokenStorage(TokenStorage):
    def __init__(self, service_name: str = "icloud_to_gdrive", username: str = "google_drive_oauth_token"):
        self.service_name = service_name
        self.username = username

    def save_token(self, token_data: Dict) -> None:
        if "apple_id" in token_data or "apple_password" in token_data:
            raise ValueError("Credentials cannot contain Apple ID/password")
        token_str = json.dumps(token_data)
        keyring.set_password(self.service_name, self.username, token_str)

    def load_token(self) -> Optional[Dict]:
        token_str = keyring.get_password(self.service_name, self.username)
        if token_str:
            try:
                return json.loads(token_str)
            except json.JSONDecodeError:
                return None
        return None

class GoogleAuthManager:
    # URD-REQ-013: 默认请求 drive.file
    DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self, storage: TokenStorage, client_secrets_file: str = "client_secret.json"):
        self.storage = storage
        self.client_secrets_file = client_secrets_file
        self._credentials = None

    def get_auth_url(self) -> str:
        # 兼容原本的 mock 接口，如果是真实执行此方法可能不常用
        scopes_str = "%20".join(self.DEFAULT_SCOPES)
        return f"https://accounts.google.com/o/oauth2/v2/auth?scope={scopes_str}&response_type=code"

    def handle_auth_callback(self, code: str) -> None:
        # Mock token exchange
        if not code:
            raise ValueError("Invalid authorization code")
        token_data = {
            "access_token": f"mock_access_token_for_{code}",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3599,
            "scope": " ".join(self.DEFAULT_SCOPES),
            "token_type": "Bearer"
        }
        self.storage.save_token(token_data)

    def login(self) -> None:
        """真实拉起本地浏览器授权并将获取到的凭证存储到 keyring"""
        creds = self.get_credentials()
        if creds and creds.valid:
            return
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(self.client_secrets_file):
                raise FileNotFoundError(f"Client secrets file not found at {self.client_secrets_file}")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, scopes=self.DEFAULT_SCOPES
            )
            # TDD-TEST-002: 真实拉起本地浏览器
            creds = flow.run_local_server(port=0)

        # 保存 credentials 状态
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        self.storage.save_token(token_data)
        self._credentials = creds

    def get_credentials(self) -> Optional[Credentials]:
        if self._credentials and self._credentials.valid:
            return self._credentials
            
        token_data = self.storage.load_token()
        if not token_data:
            return None
            
        # 根据存入的格式判断是 mock token 还是真实 google token
        if "token" in token_data:
            self._credentials = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes")
            )
            return self._credentials
        return None

    def get_valid_token(self) -> Optional[str]:
        creds = self.get_credentials()
        if creds and creds.valid:
            return creds.token
            
        # Fallback to mock token format
        token_data = self.storage.load_token()
        if token_data and "access_token" in token_data:
            return token_data.get("access_token")
            
        return None
