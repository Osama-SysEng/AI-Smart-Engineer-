"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('department_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('mfa_enabled', sa.Boolean, default=False),
        sa.Column('mfa_secret', sa.String(255), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.String(36), default='default'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, default=False),
    )

    # Roles
    op.create_table('roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Permissions
    op.create_table('permissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # UserRoles
    op.create_table('user_roles',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # RolePermissions
    op.create_table('role_permissions',
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('permission_id', sa.String(36), sa.ForeignKey('permissions.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Projects
    op.create_table('projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('client', sa.String(255), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('budget', sa.Float, nullable=True),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('tenant_id', sa.String(36), default='default'),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('health_score', sa.Integer, default=100),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, default=False),
    )

    # Sites
    op.create_table('sites',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('manager_id', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, default=False),
    )

    # Departments
    op.create_table('departments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('head_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Documents
    op.create_table('documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('uploaded_by', sa.String(36), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('status', sa.String(50), default='uploaded'),
        sa.Column('processing_progress', sa.Integer, default=0),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('extracted_count', sa.Integer, default=0),
        sa.Column('error_count', sa.Integer, default=0),
        sa.Column('warning_count', sa.Integer, default=0),
        sa.Column('review_required', sa.Boolean, default=False),
        sa.Column('virus_scanned', sa.Boolean, default=False),
        sa.Column('virus_clean', sa.Boolean, default=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, default=False),
    )

    # DocumentVersions
    op.create_table('document_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('version_number', sa.Integer, nullable=False),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('changes_summary', sa.Text, nullable=True),
        sa.Column('diff_data', postgresql.JSON, nullable=True),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # DocumentPages
    op.create_table('document_pages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('page_number', sa.Integer, nullable=False),
        sa.Column('ocr_text', sa.Text, nullable=True),
        sa.Column('layout_data', postgresql.JSON, nullable=True),
        sa.Column('image_path', sa.String(1000), nullable=True),
        sa.Column('width', sa.Float, nullable=True),
        sa.Column('height', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ExtractedEntities
    op.create_table('extracted_entities',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('extraction_run_id', sa.String(36), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_subtype', sa.String(100), nullable=True),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('normalized_value', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, default=0.0),
        sa.Column('page_number', sa.Integer, nullable=True),
        sa.Column('bounding_box', postgresql.JSON, nullable=True),
        sa.Column('source_region', sa.String(255), nullable=True),
        sa.Column('validation_status', sa.String(50), default='pending'),
        sa.Column('approved', sa.Boolean, default=False),
        sa.Column('approved_by', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ExtractionRuns
    op.create_table('extraction_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('pipeline_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_entities', sa.Integer, default=0),
        sa.Column('success_count', sa.Integer, default=0),
        sa.Column('error_count', sa.Integer, default=0),
        sa.Column('avg_confidence', sa.Float, nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('error_log', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ValidationResults
    op.create_table('validation_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('entity_id', sa.String(36), sa.ForeignKey('extracted_entities.id'), nullable=False),
        sa.Column('rule_name', sa.String(255), nullable=False),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('passed', sa.Boolean, default=False),
        sa.Column('severity', sa.String(20), default='warning'),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('expected_value', sa.Text, nullable=True),
        sa.Column('actual_value', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ReconciliationRuns
    op.create_table('reconciliation_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('sources_compared', postgresql.JSON, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_items', sa.Integer, default=0),
        sa.Column('matched_count', sa.Integer, default=0),
        sa.Column('variance_count', sa.Integer, default=0),
        sa.Column('error_count', sa.Integer, default=0),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ReconciliationItems
    op.create_table('reconciliation_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('reconciliation_run_id', sa.String(36), sa.ForeignKey('reconciliation_runs.id'), nullable=False),
        sa.Column('item_code', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('source_values', postgresql.JSON, nullable=False),
        sa.Column('variance', sa.Float, nullable=True),
        sa.Column('variance_percentage', sa.Float, nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('root_cause', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('recommended_action', sa.Text, nullable=True),
        sa.Column('approved', sa.Boolean, default=False),
        sa.Column('approved_by', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # EngineeringItems
    op.create_table('engineering_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('item_code', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('source_document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('source_revision', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float, default=0.0),
        sa.Column('normalized', sa.Boolean, default=False),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Materials
    op.create_table('materials',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('specifications', postgresql.JSON, nullable=True),
        sa.Column('aliases', postgresql.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Suppliers
    op.create_table('suppliers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(100), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('contact', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(100), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('rating', sa.Float, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # PurchaseOrders
    op.create_table('purchase_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('po_number', sa.String(100), unique=True, nullable=False),
        sa.Column('supplier_id', sa.String(36), sa.ForeignKey('suppliers.id'), nullable=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('total_amount', sa.Float, nullable=True),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sap_reference', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # InventoryTransactions
    op.create_table('inventory_transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('material_id', sa.String(36), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Float, nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('reference_doc', sa.String(255), nullable=True),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sap_reference', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # CostRecords
    op.create_table('cost_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('item_code', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('planned_cost', sa.Float, nullable=True),
        sa.Column('actual_cost', sa.Float, nullable=True),
        sa.Column('variance', sa.Float, nullable=True),
        sa.Column('currency', sa.String(10), default='USD'),
        sa.Column('period', sa.String(50), nullable=False),
        sa.Column('cost_type', sa.String(50), nullable=False),
        sa.Column('sap_reference', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # QualityRecords
    op.create_table('quality_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('inspection_type', sa.String(100), nullable=False),
        sa.Column('item_code', sa.String(255), nullable=True),
        sa.Column('result', sa.String(50), nullable=False),
        sa.Column('inspector', sa.String(255), nullable=True),
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('attachments', postgresql.JSON, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # WorkOrders
    op.create_table('work_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('wo_number', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_hours', sa.Float, nullable=True),
        sa.Column('actual_hours', sa.Float, nullable=True),
        sa.Column('sap_reference', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # SAPRecords
    op.create_table('sap_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('sap_table', sa.String(100), nullable=False),
        sa.Column('sap_key', sa.String(255), nullable=False),
        sa.Column('record_type', sa.String(100), nullable=False),
        sa.Column('data', postgresql.JSON, nullable=False),
        sa.Column('sync_status', sa.String(50), default='pending'),
        sa.Column('sync_direction', sa.String(20), default='import'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_error', sa.Text, nullable=True),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('is_dry_run', sa.Boolean, default=False),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Workflows
    op.create_table('workflows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('trigger_type', sa.String(100), nullable=False),
        sa.Column('trigger_config', postgresql.JSON, nullable=False),
        sa.Column('steps', postgresql.JSON, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # WorkflowRuns
    op.create_table('workflow_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflows.id'), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('trigger_event', sa.String(255), nullable=False),
        sa.Column('context', postgresql.JSON, nullable=True),
        sa.Column('current_step', sa.Integer, default=0),
        sa.Column('total_steps', sa.Integer, default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('trace_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Tasks
    op.create_table('tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('site_id', sa.String(36), sa.ForeignKey('sites.id'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('assigned_to', sa.String(36), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Approvals
    op.create_table('approvals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('request_type', sa.String(100), nullable=False),
        sa.Column('request_id', sa.String(36), nullable=False),
        sa.Column('requested_by', sa.String(36), nullable=False),
        sa.Column('approver_id', sa.String(36), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('evidence', postgresql.JSON, nullable=True),
        sa.Column('impact_summary', sa.Text, nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.String(36), nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # AIRequests
    op.create_table('ai_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('agent_type', sa.String(100), nullable=False),
        sa.Column('intent', sa.String(500), nullable=True),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('input_tokens', sa.Integer, nullable=True),
        sa.Column('output_tokens', sa.Integer, nullable=True),
        sa.Column('total_tokens', sa.Integer, nullable=True),
        sa.Column('latency_ms', sa.Integer, nullable=True),
        sa.Column('estimated_cost', sa.Float, nullable=True),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('tools_used', postgresql.JSON, nullable=True),
        sa.Column('trace_id', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # AIUsage
    op.create_table('ai_usage',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('period', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('total_requests', sa.Integer, default=0),
        sa.Column('total_tokens_in', sa.Integer, default=0),
        sa.Column('total_tokens_out', sa.Integer, default=0),
        sa.Column('total_cost', sa.Float, default=0.0),
        sa.Column('avg_latency_ms', sa.Float, nullable=True),
        sa.Column('project_id', sa.String(36), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # AuditLogs
    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('before_state', postgresql.JSON, nullable=True),
        sa.Column('after_state', postgresql.JSON, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('source_ip', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('request_id', sa.String(100), nullable=True),
        sa.Column('trace_id', sa.String(100), nullable=True),
        sa.Column('ai_model', sa.String(100), nullable=True),
        sa.Column('prompt_version', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # SystemEvents
    op.create_table('system_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), default='info'),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('trace_id', sa.String(100), nullable=True),
        sa.Column('workflow_id', sa.String(36), nullable=True),
        sa.Column('run_id', sa.String(36), nullable=True),
        sa.Column('resolved', sa.Boolean, default=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Notifications
    op.create_table('notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), default='info'),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('read', sa.Boolean, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_url', sa.String(1000), nullable=True),
        sa.Column('metadata', postgresql.JSON, nullable=True),
        sa.Column('dedup_key', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes
    op.create_index('idx_documents_project', 'documents', ['project_id'])
    op.create_index('idx_documents_status', 'documents', ['status'])
    op.create_index('idx_extracted_entities_doc', 'extracted_entities', ['document_id'])
    op.create_index('idx_reconciliation_run_project', 'reconciliation_runs', ['project_id'])
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_tasks_project', 'tasks', ['project_id'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('system_events')
    op.drop_table('audit_logs')
    op.drop_table('ai_usage')
    op.drop_table('ai_requests')
    op.drop_table('approvals')
    op.drop_table('tasks')
    op.drop_table('workflow_runs')
    op.drop_table('workflows')
    op.drop_table('sap_records')
    op.drop_table('work_orders')
    op.drop_table('quality_records')
    op.drop_table('cost_records')
    op.drop_table('inventory_transactions')
    op.drop_table('purchase_orders')
    op.drop_table('suppliers')
    op.drop_table('materials')
    op.drop_table('engineering_items')
    op.drop_table('reconciliation_items')
    op.drop_table('reconciliation_runs')
    op.drop_table('validation_results')
    op.drop_table('extraction_runs')
    op.drop_table('extracted_entities')
    op.drop_table('document_pages')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('departments')
    op.drop_table('sites')
    op.drop_table('projects')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
