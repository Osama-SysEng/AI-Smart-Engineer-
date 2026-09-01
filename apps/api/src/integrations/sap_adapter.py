"""SAP OData adapter with OAuth2 client credentials and fail-closed controls."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote, urlparse

import httpx

from app.domain.erp.contracts import ErpPage, ErpSnapshot
from src.core.config import get_settings
from src.core.exceptions import AIProviderError
from src.core.logging import get_logger

logger = get_logger(__name__)


class SapAdapter:
    def __init__(self, settings: Optional[Any] = None):
        self.settings = settings or get_settings()
        self.base_url = (self.settings.SAP_HOST or "").rstrip("/")
        self.client_id = self.settings.SAP_CLIENT_ID
        self.client_secret = self.settings.SAP_CLIENT_SECRET
        self.token_url = self.settings.SAP_TOKEN_URL
        self.allowed_hosts = {host.casefold() for host in (self.settings.SAP_ALLOWED_HOSTS or [])}
        self.timeout = max(2, min(int(self.settings.SAP_TIMEOUT_SECONDS), 30))
        self.mock_mode = bool(self.settings.SAP_MOCK_MODE)

    def _validate_endpoint(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.casefold() not in self.allowed_hosts:
            raise RuntimeError("SAP endpoint must use HTTPS and an explicit SAP_ALLOWED_HOSTS entry")

    def _configured_for_live(self) -> bool:
        return bool(self.base_url and self.client_id and self.client_secret and self.token_url and self.allowed_hosts)

    async def _access_token(self, client: httpx.AsyncClient) -> str:
        if not self._configured_for_live():
            raise RuntimeError("SAP OAuth client credentials are incomplete")
        token_endpoint = urlparse(self.token_url)
        if token_endpoint.scheme != "https" or not token_endpoint.hostname or token_endpoint.hostname.casefold() not in self.allowed_hosts:
            raise RuntimeError("SAP token endpoint must be HTTPS and allowlisted")
        response = await client.post(self.token_url, data={"grant_type": "client_credentials"}, auth=(self.client_id, self.client_secret))
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token or not isinstance(token, str):
            raise RuntimeError("SAP token response did not contain access_token")
        return token

    async def get_snapshot(self, identifier: str, tenant_id: str) -> Optional[ErpSnapshot]:
        if not identifier or len(identifier) > 150 or not tenant_id or len(tenant_id) > 120:
            raise ValueError("identifier and tenant_id are required and bounded")
        if self.mock_mode:
            return ErpSnapshot(identifier=identifier, status="MOCK_ACTIVE", tenant_id=tenant_id, correlation_id="mock", updated_at=datetime.now(timezone.utc))
        if not self.settings.SAP_READ_ONLY or not self.settings.SAP_DRY_RUN:
            raise RuntimeError("live SAP writes are not supported by this adapter")
        self._validate_endpoint()
        encoded_id = quote(identifier, safe="")
        url = f"{self.base_url}/sap/opu/odata/sap/API_PURCHASE_ORDER_PROCESS_SRV/A_PurchaseOrder('{encoded_id}')"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            token = await self._access_token(client)
            response = await client.get(url, params={"sap-client": self.settings.SAP_CLIENT, "$filter": f"TenantID eq '{tenant_id}'"}, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json().get("d", response.json())
            return ErpSnapshot(identifier=str(data.get("PurchaseOrder", identifier)), status=str(data.get("PurchaseOrderType", "UNKNOWN")), tenant_id=tenant_id, correlation_id=response.headers.get("x-sap-correlation-id"), updated_at=datetime.now(timezone.utc))

    async def list_snapshots(self, tenant_id: str, cursor: Optional[str] = None, limit: int = 50) -> ErpPage:
        if not tenant_id or not 1 <= limit <= 100:
            raise ValueError("tenant_id and bounded limit are required")
        if self.mock_mode:
            return ErpPage(items=[], next_cursor=None)
        raise NotImplementedError("SAP list pagination requires an approved tenant-specific OData contract")
