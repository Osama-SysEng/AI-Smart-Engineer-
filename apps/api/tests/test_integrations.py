from types import SimpleNamespace
import unittest

from src.integrations.sap_adapter import SapAdapter
from src.core.config import Settings


class IntegrationTests(unittest.TestCase):
    def test_sap_mock_is_explicit_and_non_networked(self):
        settings = SimpleNamespace(SAP_HOST=None, SAP_CLIENT_ID=None, SAP_CLIENT_SECRET=None, SAP_TOKEN_URL=None, SAP_ALLOWED_HOSTS=[], SAP_TIMEOUT_SECONDS=10, SAP_MOCK_MODE=True, SAP_READ_ONLY=True, SAP_DRY_RUN=True, SAP_CLIENT="100")
        adapter = SapAdapter(settings)
        self.assertTrue(adapter.mock_mode)
        self.assertTrue(adapter._configured_for_live() is False)

    def test_sap_live_endpoint_requires_https_and_allowlist(self):
        settings = SimpleNamespace(SAP_HOST="http://sap.example", SAP_CLIENT_ID="id", SAP_CLIENT_SECRET="secret", SAP_TOKEN_URL="https://sap.example/token", SAP_ALLOWED_HOSTS=["sap.example"], SAP_TIMEOUT_SECONDS=10, SAP_MOCK_MODE=False, SAP_READ_ONLY=True, SAP_DRY_RUN=True, SAP_CLIENT="100")
        adapter = SapAdapter(settings)
        with self.assertRaises(RuntimeError):
            adapter._validate_endpoint()

    def test_production_settings_reject_weak_signing_key(self):
        settings = Settings(ENVIRONMENT="production", DEBUG=False, SECRET_KEY="short", CORS_ORIGINS=["http://localhost:3000"], DATABASE_SSL_MODE="require")
        with self.assertRaises(RuntimeError):
            settings.validate_runtime_security()


if __name__ == "__main__":
    unittest.main()
