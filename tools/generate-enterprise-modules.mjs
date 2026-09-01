import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const root = "/home/ubuntu/AI-Smart-Engineer-Enterprise";
const domains = [
  ["projects", "Project", "tenant-aware engineering project orchestration"],
  ["documents", "Document", "ingestion, extraction, retention, and evidence"],
  ["reconciliation", "Reconciliation", "cross-source comparison and deterministic evidence"],
  ["approvals", "Approval", "human-in-the-loop high-impact decisions"],
  ["erp", "Erp", "read-safe integration and controlled outbox delivery"],
  ["agents", "Agent", "bounded AI interpretation and model-routing control"],
];
const features = ["document-intake", "evidence-review", "reconciliation-workbench", "approval-center", "erp-outbox", "audit-explorer"];

async function emit(relativePath, content) {
  const target = path.join(root, relativePath);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, content.trimStart(), "utf8");
}

for (const [domain, entity, purpose] of domains) {
  const folder = `apps/api/app/domain/${domain}`;
  await emit(`${folder}/__init__.py`, `"""${entity} bounded context: ${purpose}."""\nfrom .contracts import ${entity}Snapshot\nfrom .policies import approval_required\n\n__all__ = ["${entity}Snapshot", "approval_required"]\n`);
  await emit(`${folder}/contracts.py`, `from datetime import datetime\nfrom pydantic import BaseModel, Field\n\nclass ${entity}Snapshot(BaseModel):\n    identifier: str = Field(min_length=1, max_length=150)\n    status: str = Field(min_length=1, max_length=40)\n    tenant_id: str | None = None\n    correlation_id: str | None = None\n    updated_at: datetime | None = None\n\nclass ${entity}Page(BaseModel):\n    items: list[${entity}Snapshot] = Field(default_factory=list)\n    next_cursor: str | None = None\n`);
  await emit(`${folder}/commands.py`, `from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Create${entity}:\n    actor_id: str\n    tenant_id: str\n    correlation_id: str\n    reason: str | None = None\n\n@dataclass(frozen=True)\nclass Review${entity}:\n    identifier: str\n    actor_id: str\n    decision: str\n    reason: str\n`);
  await emit(`${folder}/events.py`, `from dataclasses import dataclass\nfrom datetime import datetime, timezone\n\n@dataclass(frozen=True)\nclass ${entity}Event:\n    event_type: str\n    identifier: str\n    correlation_id: str\n    occurred_at: datetime\n\n    @classmethod\n    def now(cls, event_type: str, identifier: str, correlation_id: str):\n        return cls(event_type, identifier, correlation_id, datetime.now(timezone.utc))\n`);
  await emit(`${folder}/policies.py`, `SENSITIVE_ACTIONS = {"ERP_WRITE", "DOCUMENT_DELETE", "MODEL_ROUTE_CHANGE", "EXPORT_EVIDENCE"}\n\ndef approval_required(action: str, risk: str = "LOW") -> bool:\n    return action.upper() in SENSITIVE_ACTIONS or risk.upper() in {"HIGH", "CRITICAL"}\n\ndef may_access_tenant(request_tenant: str, resource_tenant: str) -> bool:\n    return bool(request_tenant) and request_tenant == resource_tenant\n`);
  await emit(`${folder}/repository.py`, `from typing import Protocol\nfrom .contracts import ${entity}Page, ${entity}Snapshot\n\nclass ${entity}Repository(Protocol):\n    def get(self, identifier: str, tenant_id: str) -> ${entity}Snapshot | None: ...\n    def list_for_tenant(self, tenant_id: str, cursor: str | None = None, limit: int = 50) -> ${entity}Page: ...\n`);
  await emit(`${folder}/service.py`, `from .contracts import ${entity}Snapshot\n\ndef display_label(snapshot: ${entity}Snapshot) -> str:\n    return f"{snapshot.identifier} · {snapshot.status}"\n\ndef is_terminal(status: str) -> bool:\n    return status.upper() in {"ARCHIVED", "COMPLETED", "FAILED", "REJECTED"}\n`);
  await emit(`${folder}/telemetry.py`, `METRIC_PREFIX = "smart_engineer.${domain}"\n\ndef metric(name: str) -> str:\n    return f"{METRIC_PREFIX}.{name}"\n\ndef tags(status: str, correlation_id: str | None) -> dict[str, str]:\n    return {"status": status, "correlation_id": correlation_id or "unassigned"}\n`);
  await emit(`apps/api/tests/domain/test_${domain}_domain.py`, `from app.domain.${domain}.contracts import ${entity}Snapshot\nfrom app.domain.${domain}.policies import approval_required\nfrom app.domain.${domain}.service import display_label, is_terminal\n\ndef test_${domain}_contract_and_policy():\n    snapshot = ${entity}Snapshot(identifier="${domain}-001", status="ACTIVE", tenant_id="tenant-1", correlation_id="req-${domain}")\n    assert display_label(snapshot) == "${domain}-001 · ACTIVE"\n    assert is_terminal("COMPLETED")\n    assert approval_required("ERP_WRITE")\n    assert not approval_required("READ")\n`);
  for (const document of ["operating-model", "control-boundary", "acceptance-criteria"]) {
    await emit(`docs/domains/${domain}/${document}.md`, `# ${entity}: ${document.replaceAll("-", " ")}\n\n## Responsibility\n\nThe ${entity} context owns ${purpose}. Tenant scope, actor accountability, correlation identifiers, and policy checks are explicit in its contracts.\n\n## Control boundary\n\nAI may interpret retained evidence but cannot directly override deterministic values, cross a tenant boundary, or execute a sensitive external change without the relevant approval.\n\n## Acceptance signal\n\nA feature is accepted only when domain tests, contract checks, and operational evidence agree.\n`);
  }
}

for (const feature of features) {
  const folder = `apps/web/src/features/${feature}`;
  await emit(`${folder}/types.ts`, `export type ${feature.replaceAll("-", "_")}Record = { id: string; status: string; correlationId?: string };\nexport const featureName = "${feature}";\n`);
  await emit(`${folder}/api.ts`, `export const ${feature.replaceAll("-", "_")}Endpoint = "/api/${feature}";\nexport const withCursor = (endpoint: string, cursor?: string) => cursor ? \`${"${endpoint}"}?cursor=\${encodeURIComponent(cursor)}\` : endpoint;\n`);
  await emit(`${folder}/selectors.ts`, `export const byStatus = <T extends { status: string }>(items: T[], status: string) => status === "ALL" ? items : items.filter(item => item.status === status);\nexport const byQuery = <T extends Record<string, unknown>>(items: T[], query: string, keys: string[]) => { const needle = query.trim().toLowerCase(); return !needle ? items : items.filter(item => keys.some(key => String(item[key] ?? "").toLowerCase().includes(needle))); };\n`);
  await emit(`${folder}/state.ts`, `export type FeatureState<T> = { status: "idle" | "loading" | "ready" | "error"; data: T[]; error: string | null };\nexport const initialState = <T>(): FeatureState<T> => ({ status: "idle", data: [], error: null });\n`);
  await emit(`${folder}/view-model.ts`, `export const toViewModel = (record: Record<string, unknown>) => ({ id: String(record.id ?? ""), status: String(record.status ?? "UNKNOWN"), correlationId: record.correlation_id ?? record.correlationId ?? null });\n`);
  await emit(`${folder}/accessibility.ts`, `export const labels = { loading: "Loading ${feature}", empty: "No ${feature} records", retry: "Retry", refresh: "Refresh ${feature}" } as const;\n`);
  await emit(`${folder}/README.md`, `# ${feature}\n\nThis feature module keeps transport, state, selectors, accessibility, and view models separate so evidence-sensitive operator screens remain maintainable as the project grows.\n`);
}

for (const file of [
  "infrastructure/kubernetes/base/namespace.yaml", "infrastructure/kubernetes/base/api-deployment.yaml", "infrastructure/kubernetes/base/web-deployment.yaml", "infrastructure/kubernetes/base/api-service.yaml", "infrastructure/kubernetes/base/network-policy.yaml", "infrastructure/kubernetes/overlays/staging/kustomization.yaml", "infrastructure/kubernetes/overlays/production/kustomization.yaml", "infrastructure/observability/slo.md", "infrastructure/observability/alerts.md", "infrastructure/security/secret-rotation.md", "docs/data-governance.md", "docs/erp-control-runbook.md", "docs/model-routing-governance.md", "docs/tenant-isolation-review.md"
]) {
  const title = path.basename(file).replaceAll("-", " ");
  await emit(file, file.endsWith(".yaml") ? `apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: smart-engineer-${title.replace(".yaml", "").replaceAll(" ", "-")}\n  labels:\n    app.kubernetes.io/name: ai-smart-engineer\ndata:\n  managed-by: enterprise-expansion\n` : `# ${title}\n\nThis operational artifact records a control boundary for AI Smart Engineer. It is a safe template, not a production credential or permission to execute ERP writes, route sensitive data, or change tenant access.\n`);
}

console.log(`Generated ${domains.length} engineering domains and ${features.length} web feature modules.`);
