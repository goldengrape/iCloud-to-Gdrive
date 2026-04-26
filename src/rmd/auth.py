from typing import Optional, Dict

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

class GoogleAuthManager:
    # URD-REQ-013: 默认请求 drive.file
    DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self, storage: TokenStorage):
        self.storage = storage

    def get_auth_url(self) -> str:
        # Mock auth URL generation
        scopes_str = "%20".join(self.DEFAULT_SCOPES)
        return f"https://accounts.google.com/o/oauth2/v2/auth?scope={scopes_str}&response_type=code"

    def handle_auth_callback(self, code: str) -> None:
        # Mock token exchange
        if not code:
            raise ValueError("Invalid authorization code")

        # Simulate successful token response
        token_data = {
            "access_token": f"mock_access_token_for_{code}",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3599,
            "scope": " ".join(self.DEFAULT_SCOPES),
            "token_type": "Bearer"
        }
        self.storage.save_token(token_data)

    def get_valid_token(self) -> Optional[str]:
        token_data = self.storage.load_token()
        if not token_data:
            return None
        return token_data.get("access_token")
