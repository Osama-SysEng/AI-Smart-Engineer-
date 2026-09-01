"""AI Extraction Engine."""
import json
from datetime import datetime, timezone
from typing import Dict, List

from src.core.config import get_settings
from src.core.logging import get_logger
from src.ai.llm_provider import LLMRouter
from src.db.models.document import Document, DocumentPage, ExtractedEntity
from src.db.models.extraction import ExtractionRun
from src.db.models.engineering import Material

logger = get_logger(__name__)


class ExtractionEngine:
    """Extract structured data from documents using AI."""

    def __init__(self):
        self.llm_router = LLMRouter()
        self.settings = get_settings()

    async def run(self, run_id: str, model_override: str = None) -> Dict:
        """Run extraction on a document."""
        from sqlalchemy import select
        from src.db.session import async_session

        async with async_session() as db:
            result = await db.execute(select(ExtractionRun).where(ExtractionRun.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                return {"status": "error", "message": "Run not found"}

            run.status = "processing"
            run.started_at = datetime.now()
            await db.commit()

            try:
                # Get document
                result = await db.execute(select(Document).where(Document.id == run.document_id))
                doc = result.scalar_one_or_none()

                await self.extract_from_document(doc, db, run, model_override)

                run.status = "completed"
                run.completed_at = datetime.now()
                await db.commit()

                return {"status": "completed", "run_id": run_id}
            except Exception as e:
                run.status = "failed"
                run.error_log = str(e)
                await db.commit()
                logger.error("Extraction failed", error=str(e), run_id=run_id)
                return {"status": "error", "message": str(e)}

    async def extract_from_document(self, doc: Document, db, run: ExtractionRun = None, model_override: str = None) -> List[ExtractedEntity]:
        """Extract entities from a document."""
        # Guarantee an extraction run because extracted_entities requires one.
        if run is None:
            run = ExtractionRun(
                document_id=doc.id,
                pipeline_type="document_ai",
                status="processing",
                started_at=datetime.now(timezone.utc),
            )
            db.add(run)
            await db.flush()

        # Build prompt
        system_prompt = """You are an engineering document extraction AI.
Extract the following entities from the document content:
- Project name
- Site name
- Drawing number
- Revision
- Date
- Engineer name
- Contractor
- Materials with quantities and units
- Dimensions
- Levels
- Equipment
- Cost information

Return ONLY a JSON array of extracted entities with this structure:
[
  {
    "entity_type": "material|dimension|date|...",
    "value": "extracted value",
    "normalized_value": "normalized form",
    "confidence": 0.95,
    "page_number": 1,
    "source_region": "description of where found"
  }
]

Rules:
- Do not hallucinate - only extract what is present
- Provide confidence scores (0-1)
- Normalize units to standard forms (TON, M3, M2, etc.)
- Flag ambiguous extractions with lower confidence"""

        # Get document text
        document_text = await self._get_document_text(doc, db)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Document content:\n{document_text[:8000]}"},  # Limit context
        ]

        response = await self.llm_router.route(
            messages=messages,
            complexity="high",
            model=model_override,
        )

        # Parse extracted entities
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            entities_data = json.loads(content)

            extracted = []
            for entity_data in entities_data:
                entity = ExtractedEntity(
                    document_id=doc.id,
                    extraction_run_id=run.id if run else None,
                    entity_type=entity_data.get("entity_type", "unknown"),
                    value=entity_data.get("value", ""),
                    normalized_value=entity_data.get("normalized_value"),
                    confidence=entity_data.get("confidence", 0.5),
                    page_number=entity_data.get("page_number"),
                    source_region=entity_data.get("source_region"),
                )
                db.add(entity)
                extracted.append(entity)

            # Update document stats
            doc.extracted_count = len(extracted)
            doc.confidence = sum(e.confidence for e in extracted) / len(extracted) if extracted else 0
            doc.review_required = any(e.confidence < self.settings.CONFIDENCE_REVIEW for e in extracted)

            if run:
                run.total_entities = len(extracted)
                run.success_count = len(extracted)
                run.avg_confidence = doc.confidence
                run.model_used = response.model
                run.status = "completed"
                run.completed_at = datetime.now(timezone.utc)

            await db.commit()
            logger.info("Extraction completed", document_id=doc.id, entities=len(extracted))
            return extracted

        except json.JSONDecodeError as e:
            logger.error("Failed to parse extraction response", error=str(e), response=response.content[:500])
            raise

    async def _get_document_text(self, doc: Document, db) -> str:
        """Get text content from document."""
        from sqlalchemy import select

        # Try pages first
        result = await db.execute(select(DocumentPage).where(DocumentPage.document_id == doc.id))
        pages = result.scalars().all()

        if pages:
            return "\n\n".join([p.ocr_text or "" for p in pages])

        # Try metadata
        if doc.metadata and "text" in doc.metadata:
            return doc.metadata["text"]

        # Fallback - read file directly for text files
        if doc.file_type in [".txt", ".csv"]:
            with open(doc.storage_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        return ""
