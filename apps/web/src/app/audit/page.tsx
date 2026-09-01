'use client';

import { useState } from 'react';
import {
  Shield,
  Search,
  Filter,
  Download,
  Clock,
  User,
  FileText,
  Activity,
} from 'lucide-react';
import { formatDate } from '@/utils/helpers';

const mockLogs = [
  {
    id: '1',
    action: 'DOCUMENT_UPLOAD',
    resource_type: 'Document',
    resource_id: 'doc-123',
    user: 'Ahmed Hassan',
    timestamp: '2024-01-15T10:30:00Z',
    details: 'Uploaded Site-03-Structural-R04.pdf',
  },
  {
    id: '2',
    action: 'EXTRACTION_RUN',
    resource_type: 'Extraction',
    resource_id: 'ext-456',
    user: 'AI System',
    timestamp: '2024-01-15T10:35:00Z',
    details: 'Extracted 47 entities with 97% confidence using GPT-4o',
  },
  {
    id: '3',
    action: 'RECONCILIATION_APPROVE',
    resource_type: 'ReconciliationItem',
    resource_id: 'rec-789',
    user: 'Mohammed Ali',
    timestamp: '2024-01-15T11:00:00Z',
    details: 'Approved variance for STEEL-REBAR-12MM',
  },
  {
    id: '4',
    action: 'SAP_SYNC',
    resource_type: 'SAPRecord',
    resource_id: 'sap-001',
    user: 'System',
    timestamp: '2024-01-15T11:30:00Z',
    details: 'Synced 125 records to SAP (dry-run: false)',
  },
];

export default function AuditPage() {
  const [logs] = useState(mockLogs);
  const [search, setSearch] = useState('');

  const filtered = logs.filter(
    (log) =>
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.user.toLowerCase().includes(search.toLowerCase()) ||
      log.details.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-gray-500 mt-1">Complete history of all system actions</p>
        </div>
        <button className="btn-secondary flex items-center gap-2 text-sm">
          <Download className="w-4 h-4" />
          Export Logs
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audit logs..."
              className="input-field pl-10 text-sm"
            />
          </div>
          <select className="input-field text-sm w-40">
            <option>All Actions</option>
            <option>Document</option>
            <option>Extraction</option>
            <option>Reconciliation</option>
            <option>SAP</option>
          </select>
          <input type="date" className="input-field text-sm w-40" />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(log.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="badge bg-primary-100 text-primary-700">{log.action}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.resource_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      {log.user}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-md truncate">
                    {log.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
