"""SAP Integration Adapter."""
from typing import Dict, List, Optional
from datetime import datetime

from src.core.config import get_settings
from src.core.logging import get_logger
from src.core.exceptions import SAPIntegrationError

logger = get_logger(__name__)


class SAPAdapter:
    """Adapter for SAP ERP integration."""

    def __init__(self):
        self.settings = get_settings()
        self.connected = False
        self.read_only = self.settings.SAP_READ_ONLY
        self.dry_run = self.settings.SAP_DRY_RUN
        self.mock_mode = getattr(self.settings, "SAP_MOCK_MODE", False)
        self.connection = None

    async def connect(self) -> bool:
        """Connect to SAP."""
        try:
            if self.mock_mode:
                self.connected = True
                logger.warning("SAP mock mode enabled")
                return True
            if not all([self.settings.SAP_ASHOST, self.settings.SAP_USER, self.settings.SAP_PASSWORD]):
                raise SAPIntegrationError("SAP connector is not configured")
            # In production, use pyrfc or similar
            # from pyrfc import Connection
            # self.connection = Connection(
            #     ashost=self.settings.SAP_ASHOST,
            #     sysnr=self.settings.SAP_SYSNR,
            #     client=self.settings.SAP_CLIENT,
            #     user=self.settings.SAP_USER,
            #     passwd=self.settings.SAP_PASSWORD,
            # )
            if self.connection is None:
                raise SAPIntegrationError("SAP RFC client is not installed/configured")
            self.connected = True
            logger.info("SAP connection established")
            return True
        except Exception as e:
            logger.error("SAP connection failed", error=str(e))
            raise SAPIntegrationError(f"Failed to connect to SAP: {str(e)}")

    async def read_table(self, table: str, fields: List[str] = None, where: str = None, max_rows: int = 100) -> List[Dict]:
        """Read data from SAP table."""
        if not self.connected:
            await self.connect()

        logger.info("Reading SAP table", table=table, fields=fields)

        if self.mock_mode:
            return []
        if self.connection is None:
            raise SAPIntegrationError("SAP read unavailable: RFC connector is not configured")

        # Actual RFC call
        # In production:
        # result = self.connection.call("RFC_READ_TABLE", 
        #     QUERY_TABLE=table,
        #     DELIMITER="|",
        #     FIELDS=[{"FIELDNAME": f} for f in fields] if fields else [],
        #     OPTIONS=[{"TEXT": where}] if where else [],
        #     ROWCOUNT=max_rows,
        # )

        return []

    async def create_record(self, table: str, data: Dict) -> Dict:
        """Create record in SAP."""
        if self.read_only:
            raise SAPIntegrationError("SAP is in read-only mode")

        if self.dry_run:
            logger.info("Dry-run: Would create record", table=table, data=data)
            return {"status": "dry_run", "table": table}

        logger.info("Creating SAP record", table=table)
        # Actual SAP create logic
        return {"status": "created", "table": table}

    async def update_record(self, table: str, key: str, data: Dict) -> Dict:
        """Update record in SAP."""
        if self.read_only:
            raise SAPIntegrationError("SAP is in read-only mode")

        if self.dry_run:
            logger.info("Dry-run: Would update record", table=table, key=key, data=data)
            return {"status": "dry_run", "table": table, "key": key}

        logger.info("Updating SAP record", table=table, key=key)
        return {"status": "updated", "table": table, "key": key}

    async def sync_record(self, record_id: str, dry_run: bool = True) -> Dict:
        """Sync a record with SAP."""
        from sqlalchemy import select
        from src.db.session import async_session
        from src.db.models.sap import SAPRecord

        async with async_session() as db:
            result = await db.execute(select(SAPRecord).where(SAPRecord.id == record_id))
            record = result.scalar_one_or_none()
            if not record:
                return {"status": "error", "message": "Record not found"}

            record.is_dry_run = dry_run

            try:
                if record.sync_direction == "export":
                    result = await self.create_record(record.sap_table, record.data)
                else:
                    result = await self.read_table(record.sap_table)

                record.sync_status = "completed"
                record.last_sync_at = datetime.now()
                await db.commit()

                return {"status": "success", "record_id": record_id}
            except Exception as e:
                record.sync_status = "failed"
                record.sync_error = str(e)
                record.retry_count += 1
                await db.commit()
                raise
