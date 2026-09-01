export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  phone?: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: Role[];
}

export interface Role {
  id: string;
  name: string;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  client?: string;
  location?: string;
  status: string;
  health_score: number;
  sites: Site[];
  departments: Department[];
}

export interface Site {
  id: string;
  name: string;
  code: string;
  location?: string;
  status: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
}

export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: string;
  processing_progress: number;
  confidence?: number;
  extracted_count: number;
  error_count: number;
  review_required: boolean;
  created_at: string;
}

export interface ExtractedEntity {
  id: string;
  entity_type: string;
  value: string;
  normalized_value?: string;
  confidence: number;
  page_number?: number;
  validation_status: string;
  approved: boolean;
}

export interface ReconciliationRun {
  id: string;
  name: string;
  status: string;
  total_items: number;
  matched_count: number;
  variance_count: number;
  created_at: string;
}

export interface ReconciliationItem {
  id: string;
  item_code: string;
  source_values: Record<string, number | string>;
  variance?: number;
  variance_percentage?: number;
  status: string;
  root_cause?: string;
  recommended_action?: string;
}

export interface Task {
  id: string;
  project_id?: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  due_date?: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  severity: string;
  read: boolean;
  created_at: string;
}

export interface AIChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tools_used?: string[];
  confidence?: number;
  requires_approval?: boolean;
}

export interface DashboardStats {
  total_documents: number;
  processing_documents: number;
  total_errors: number;
  pending_tasks: number;
  variance_count: number;
  automation_rate: number;
  data_quality_score: number;
  sap_sync_success_rate: number;
}
