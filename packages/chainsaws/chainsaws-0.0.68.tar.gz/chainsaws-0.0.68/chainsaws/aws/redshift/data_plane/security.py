"""Security utilities for Redshift connections and access control."""

import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import boto3
from cryptography.fernet import Fernet


@dataclass
class ConnectionCredentials:
    """Redshift connection credentials."""
    host: str
    port: int
    database: str
    user: str
    password: str
    ssl: bool = True
    ssl_cert_path: Optional[str] = None


class CredentialManager:
    """Manage secure storage and retrieval of credentials."""

    def __init__(self, key_path: Optional[str] = None):
        if key_path and os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                self._key = f.read()
        else:
            self._key = Fernet.generate_key()
            if key_path:
                with open(key_path, 'wb') as f:
                    f.write(self._key)
        self._cipher = Fernet(self._key)

    def encrypt_credentials(self, credentials: ConnectionCredentials) -> str:
        """Encrypt connection credentials."""
        data = {
            'host': credentials.host,
            'port': credentials.port,
            'database': credentials.database,
            'user': credentials.user,
            'password': credentials.password,
            'ssl': credentials.ssl,
            'ssl_cert_path': credentials.ssl_cert_path,
        }
        json_data = json.dumps(data)
        encrypted = self._cipher.encrypt(json_data.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_credentials(self, encrypted: str) -> ConnectionCredentials:
        """Decrypt connection credentials."""
        encrypted_bytes = base64.b64decode(encrypted)
        decrypted = self._cipher.decrypt(encrypted_bytes)
        data = json.loads(decrypted)
        return ConnectionCredentials(**data)


class TokenManager:
    """Manage temporary access tokens."""

    def __init__(self, secret_key: Optional[str] = None):
        self._secret_key = secret_key or secrets.token_hex(32)

    def generate_token(
        self,
        user_id: str,
        permissions: List[str],
        expiry: Optional[timedelta] = None,
    ) -> str:
        """Generate a temporary access token."""
        if not expiry:
            expiry = timedelta(hours=1)

        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': int((datetime.now() + expiry).timestamp()),
            'iat': int(datetime.now().timestamp()),
            'nonce': secrets.token_hex(8),
        }

        # Create signature
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self._secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine payload and signature
        token_data = {
            'payload': payload,
            'signature': signature,
        }
        return base64.b64encode(
            json.dumps(token_data).encode()
        ).decode()

    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate a token and return its payload if valid."""
        try:
            # Decode token
            token_json = base64.b64decode(token.encode()).decode()
            token_data = json.loads(token_json)

            # Verify signature
            payload = token_data['payload']
            provided_signature = token_data['signature']
            message = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self._secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(provided_signature, expected_signature):
                return None

            # Check expiration
            if payload['exp'] < datetime.now().timestamp():
                return None

            return payload
        except Exception:
            return None


class IAMAuthenticator:
    """Authenticate using AWS IAM credentials."""

    def __init__(self, cluster_id: str, region: str):
        self.cluster_id = cluster_id
        self.region = region
        self._client = boto3.client('redshift', region_name=region)

    def get_cluster_credentials(
        self,
        db_user: str,
        db_name: Optional[str] = None,
        duration_seconds: int = 3600,
        auto_create: bool = False,
    ) -> ConnectionCredentials:
        """Get temporary database credentials using GetClusterCredentials."""
        params = {
            'DbUser': db_user,
            'ClusterIdentifier': self.cluster_id,
            'DurationSeconds': duration_seconds,
            'AutoCreate': auto_create,
        }
        if db_name:
            params['DbName'] = db_name

        response = self._client.get_cluster_credentials(**params)

        # Get cluster endpoint
        cluster = self._client.describe_clusters(
            ClusterIdentifier=self.cluster_id
        )['Clusters'][0]
        endpoint = cluster['Endpoint']

        return ConnectionCredentials(
            host=endpoint['Address'],
            port=endpoint['Port'],
            database=db_name or 'dev',
            user=response['DbUser'],
            password=response['DbPassword'],
            ssl=True,
        )


class AccessController:
    """Control access to Redshift resources."""

    def __init__(self):
        self._permissions: Dict[str, List[str]] = {}

    def grant_permission(self, user_id: str, permission: str) -> None:
        """Grant a permission to a user."""
        if user_id not in self._permissions:
            self._permissions[user_id] = []
        if permission not in self._permissions[user_id]:
            self._permissions[user_id].append(permission)

    def revoke_permission(self, user_id: str, permission: str) -> None:
        """Revoke a permission from a user."""
        if user_id in self._permissions:
            self._permissions[user_id] = [
                p for p in self._permissions[user_id]
                if p != permission
            ]

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if a user has a specific permission."""
        return (
            user_id in self._permissions and
            permission in self._permissions[user_id]
        )

    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user."""
        return self._permissions.get(user_id, [])
