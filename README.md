# AI Smart Engineer - المهندس الذكي

## Engineering Intelligence & Automation Platform

A comprehensive AI-powered engineering platform for document processing, data extraction, validation, reconciliation, and ERP integration.

## Architecture

```
                    AI SMART ENGINEER
                           │
                    Web Application (Next.js)
                           │
                    API Gateway (FastAPI)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Auth Service      Project Service    Document Service
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    Workflow Engine
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
 AI Engine          Data Engine        Automation Engine
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                 Reconciliation Engine
                           │
                 Decision Engine
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
      SAP              PostgreSQL         Object Storage
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                  Monitoring / Audit
```

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd ai-smart-engineer

# Environment
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Access
# Web App: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Adminer: http://localhost:8080
# Redis Commander: http://localhost:8081
```

## Project Structure

- `apps/web/` - Next.js frontend (React, TypeScript, Tailwind)
- `apps/api/` - FastAPI backend (Python, async, modular)
- `services/` - Microservices (ingestion, AI, SAP, etc.)
- `agents/` - AI agents system
- `integrations/` - ERP/CRM adapters
- `workers/` - Background task workers
- `infrastructure/` - Docker, K8s, Terraform
- `tests/` - Comprehensive test suite

## Features

- Document Intelligence (OCR, Layout Detection, Table Extraction)
- Excel Intelligence (Formula Analysis, Validation)
- AI Extraction with Confidence Scoring
- Cross-Source Reconciliation
- Anomaly Detection (Rule + Statistical + AI)
- SAP Integration with Audit Trail
- Workflow Automation Engine
- Human-in-the-Loop Approval
- Real-time Notifications
- Advanced Search (Keyword + Semantic)
- Knowledge Graph
- Multi-tenant Ready
- RBAC Security
- Full Audit Trail
- AI Cost Control & Routing

## License

Proprietary - AI Smart Engineer Platform


## Hardening status

This build includes tenant-aware project/document access checks, explicit CORS configuration, production secret validation, upload size enforcement, authenticated AI WebSocket sessions, Docker build fixes, and CI checks. SAP remains read-only/dry-run by default.
