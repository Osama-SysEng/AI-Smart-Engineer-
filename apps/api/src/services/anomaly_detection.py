"""Anomaly Detection Engine - Hybrid detection (Rule + Statistical + AI)."""
import statistics
from typing import Dict, List, Optional
from datetime import datetime

from src.core.config import get_settings
from src.core.logging import get_logger
from src.ai.llm_provider import LLMRouter

logger = get_logger(__name__)


class AnomalyDetector:
    """Detect anomalies in engineering data."""

    def __init__(self):
        self.llm_router = LLMRouter()
        self.settings = get_settings()

    async def detect(self, data: List[Dict], rules: List[Dict] = None) -> List[Dict]:
        """Run hybrid anomaly detection."""
        anomalies = []

        # Rule-based detection
        rule_anomalies = await self._rule_based_detection(data, rules or [])
        anomalies.extend(rule_anomalies)

        # Statistical detection
        stat_anomalies = await self._statistical_detection(data)
        anomalies.extend(stat_anomalies)

        # AI-based detection (for complex patterns)
        if len(data) > 10:
            ai_anomalies = await self._ai_detection(data)
            anomalies.extend(ai_anomalies)

        # Deduplicate
        seen = set()
        unique_anomalies = []
        for a in anomalies:
            key = (a.get("item_code"), a.get("type"))
            if key not in seen:
                seen.add(key)
                unique_anomalies.append(a)

        return unique_anomalies

    async def _rule_based_detection(self, data: List[Dict], rules: List[Dict]) -> List[Dict]:
        """Rule-based anomaly detection."""
        anomalies = []

        for item in data:
            # Check negative quantities
            if item.get("quantity", 0) < 0:
                anomalies.append({
                    "item_code": item.get("item_code"),
                    "type": "negative_quantity",
                    "severity": "critical",
                    "message": f"Negative quantity detected: {item.get('quantity')}",
                    "value": item.get("quantity"),
                    "rule": "quantity >= 0",
                })

            # Check zero quantities
            if item.get("quantity", 0) == 0:
                anomalies.append({
                    "item_code": item.get("item_code"),
                    "type": "zero_quantity",
                    "severity": "warning",
                    "message": "Zero quantity detected",
                    "value": 0,
                    "rule": "quantity > 0",
                })

            # Check date validity
            if item.get("date"):
                try:
                    item_date = datetime.fromisoformat(str(item["date"]))
                    if item_date > datetime.now():
                        anomalies.append({
                            "item_code": item.get("item_code"),
                            "type": "future_date",
                            "severity": "warning",
                            "message": f"Future date: {item['date']}",
                            "value": item["date"],
                            "rule": "date <= today",
                        })
                except:
                    anomalies.append({
                        "item_code": item.get("item_code"),
                        "type": "invalid_date",
                        "severity": "warning",
                        "message": f"Invalid date format: {item.get('date')}",
                        "value": item.get("date"),
                        "rule": "valid date format",
                    })

        return anomalies

    async def _statistical_detection(self, data: List[Dict]) -> List[Dict]:
        """Statistical anomaly detection using Z-score."""
        anomalies = []

        quantities = [item.get("quantity", 0) for item in data if item.get("quantity", 0) > 0]
        if len(quantities) < 3:
            return anomalies

        mean = statistics.mean(quantities)
        stdev = statistics.stdev(quantities) if len(quantities) > 1 else 0

        if stdev == 0:
            return anomalies

        for item in data:
            qty = item.get("quantity", 0)
            if qty > 0:
                z_score = abs(qty - mean) / stdev
                if z_score > 3:  # Beyond 3 standard deviations
                    anomalies.append({
                        "item_code": item.get("item_code"),
                        "type": "statistical_outlier",
                        "severity": "warning",
                        "message": f"Statistical outlier (Z-score: {z_score:.2f})",
                        "value": qty,
                        "expected_range": f"{mean - 3*stdev:.2f} - {mean + 3*stdev:.2f}",
                        "z_score": z_score,
                    })

        return anomalies

    async def _ai_detection(self, data: List[Dict]) -> List[Dict]:
        """AI-based anomaly detection for complex patterns."""
        # Simplified - in production, use more sophisticated analysis
        system_prompt = """You are an anomaly detection AI for engineering data.
Analyze the provided data and identify any anomalies or suspicious patterns.
Return JSON array of anomalies found, or empty array if none."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Data: {data[:50]}"},  # Limit data
        ]

        try:
            response = await self.llm_router.route(messages, complexity="medium")
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            import json
            anomalies = json.loads(content)
            if not isinstance(anomalies, list):
                return []
            return anomalies
        except Exception as e:
            logger.error("AI detection failed", error=str(e))
            return []
