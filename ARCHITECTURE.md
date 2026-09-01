# AI Smart Engineer — Architecture

```text
Web UI / AI Chat
      |
      v
FastAPI API Gateway
      |
      +-- Auth / RBAC / Tenant Boundary
      +-- Projects / Sites / Documents / Workflows
      +-- AI Orchestrator
      |
      +-------------------------+
      |                         |
      v                         v
Celery + Redis             PostgreSQL
      |                         |
      +-- OCR                   +-- Engineering data
      +-- Extraction            +-- Documents
      +-- Reconciliation        +-- Audit
      +-- Reports               +-- Workflow state
      +-- AI analysis           +-- AI usage
      +-- SAP sync
      |
      v
AI Provider Router
  +-- OpenAI
  +-- Anthropic
  +-- Google Gemini
  +-- DeepSeek
  +-- Ollama
      |
      v
Specialist Agents
  +-- Document
  +-- Engineering
  +-- Validation
  +-- Data
  +-- Reconciliation
  +-- Anomaly
  +-- Reporting
  +-- SAP
  +-- Quality
  +-- Security
  +-- DevOps
  +-- Assistant
```

Core rule: deterministic systems validate numbers and permissions; AI interprets evidence and recommends actions. High-impact mutations remain behind authorization and approval boundaries.
