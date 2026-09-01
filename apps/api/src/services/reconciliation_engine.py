"""Reconciliation Engine - compares data across sources."""
import json
from typing import Dict, List
from datetime import datetime

from src.core.config import get_settings
from src.core.logging import get_logger
from src.ai.llm_provider import LLMRouter
from src.db.models.reconciliation import ReconciliationRun, ReconciliationItem
from src.db.models.engineering import EngineeringItem
from src.db.models.sap import SAPRecord
from src.db.models.procurement import InventoryTransaction, PurchaseOrder

logger = get_logger(__name__)


class ReconciliationEngine:
    """Compare and reconcile data across multiple sources."""

    def __init__(self):
        self.llm_router = LLMRouter()
        self.settings = get_settings()

    async def run(self, run_id: str) -> Dict:
        """Run reconciliation."""
        from sqlalchemy import select, and_
        from src.db.session import async_session

        async with async_session() as db:
            result = await db.execute(select(ReconciliationRun).where(ReconciliationRun.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                return {"status": "error", "message": "Run not found"}

            run.status = "processing"
            run.started_at = datetime.now()
            await db.commit()

            try:
                # Get data from all sources
                sources_data = await self._collect_source_data(run, db)

                # Compare items
                items = await self._compare_items(run, sources_data, db)

                # Analyze variances with AI
                await self._analyze_variances(run, items, db)

                run.status = "completed"
                run.completed_at = datetime.now()
                run.total_items = len(items)
                run.matched_count = sum(1 for i in items if i.status == "matched")
                run.variance_count = sum(1 for i in items if i.status == "variance")

                await db.commit()

                logger.info("Reconciliation completed", run_id=run_id, items=len(items), variances=run.variance_count)
                return {"status": "completed", "run_id": run_id, "variances": run.variance_count}

            except Exception as e:
                run.status = "failed"
                await db.commit()
                logger.error("Reconciliation failed", error=str(e), run_id=run_id)
                return {"status": "error", "message": str(e)}

    async def _collect_source_data(self, run: ReconciliationRun, db) -> Dict:
        """Collect data from all sources."""
        from sqlalchemy import select

        data = {}
        sources = run.sources_compared

        if "engineering" in sources:
            result = await db.execute(
                select(EngineeringItem).where(EngineeringItem.project_id == run.project_id)
            )
            data["engineering"] = {item.item_code: item.quantity for item in result.scalars().all()}

        if "sap" in sources:
            result = await db.execute(
                select(SAPRecord).where(
                    and_(SAPRecord.project_id == run.project_id, SAPRecord.sap_table == "material")
                )
            )
            data["sap"] = {record.sap_key: record.data.get("quantity", 0) for record in result.scalars().all()}

        if "warehouse" in sources:
            result = await db.execute(
                select(InventoryTransaction).where(InventoryTransaction.project_id == run.project_id)
            )
            # Aggregate by material
            warehouse_data = {}
            for txn in result.scalars().all():
                code = txn.material_id
                warehouse_data[code] = warehouse_data.get(code, 0) + txn.quantity
            data["warehouse"] = warehouse_data

        if "purchasing" in sources:
            result = await db.execute(
                select(PurchaseOrder).where(PurchaseOrder.project_id == run.project_id)
            )
            data["purchasing"] = {po.po_number: po.total_amount for po in result.scalars().all()}

        return data

    async def _compare_items(self, run: ReconciliationRun, sources_data: Dict, db) -> List[ReconciliationItem]:
        """Compare items across sources."""
        # Get all unique item codes
        all_items = set()
        for source_data in sources_data.values():
            all_items.update(source_data.keys())

        items = []
        for item_code in all_items:
            source_values = {}
            for source, data in sources_data.items():
                source_values[source] = data.get(item_code, 0)

            # Check for variance
            values = [v for v in source_values.values() if v != 0]
            if len(values) > 1 and max(values) != min(values):
                variance = max(values) - min(values)
                variance_pct = (variance / max(values)) * 100 if max(values) > 0 else 0
                status = "variance"
            else:
                variance = 0
                variance_pct = 0
                status = "matched"

            item = ReconciliationItem(
                reconciliation_run_id=run.id,
                item_code=item_code,
                source_values=source_values,
                variance=variance,
                variance_percentage=variance_pct,
                status=status,
            )
            db.add(item)
            items.append(item)

        await db.commit()
        return items

    async def _analyze_variances(self, run: ReconciliationRun, items: List[ReconciliationItem], db) -> None:
        """Use AI to analyze variance root causes."""
        variance_items = [i for i in items if i.status == "variance"]

        if not variance_items:
            return

        # Build prompt for AI analysis
        variances_text = "\n".join([
            f"Item {item.item_code}: {item.source_values} (variance: {item.variance})"
            for item in variance_items[:20]  # Limit to top 20
        ])

        system_prompt = """You are a reconciliation analysis AI. Analyze the variances between engineering, warehouse, purchasing, and SAP data.
For each variance, suggest the most likely root cause from:
- Receiving delay
- Unposted transaction
- Data-entry error
- Damaged material
- Missing transfer
- Unit conversion error
- Duplicate entry
- Missing goods receipt

Return JSON array of analyses with confidence scores."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Variances to analyze:\n{variances_text}"},
        ]

        try:
            response = await self.llm_router.route(messages, complexity="high")

            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            analyses = json.loads(content)

            # Update items with analysis
            for i, analysis in enumerate(analyses):
                if i < len(variance_items):
                    item = variance_items[i]
                    item.root_cause = analysis.get("root_cause", "Unknown")
                    item.confidence = analysis.get("confidence", 0.5)
                    item.recommended_action = analysis.get("recommended_action", "Review manually")

            await db.commit()

        except Exception as e:
            logger.error("Variance analysis failed", error=str(e))
            # Don't fail the whole reconciliation
