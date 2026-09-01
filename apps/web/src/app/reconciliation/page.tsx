'use client';

import { useState } from 'react';
import { ReconciliationRun, ReconciliationItem } from '@/types';
import {
  GitCompare,
  Play,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Filter,
} from 'lucide-react';
import { getStatusColor } from '@/utils/helpers';
import toast from 'react-hot-toast';

const mockRuns: ReconciliationRun[] = [
  {
    id: '1',
    name: 'Weekly Material Reconciliation',
    status: 'completed',
    total_items: 156,
    matched_count: 142,
    variance_count: 14,
    created_at: '2024-01-15T08:00:00Z',
  },
  {
    id: '2',
    name: 'Monthly Cost Comparison',
    status: 'processing',
    total_items: 0,
    matched_count: 0,
    variance_count: 0,
    created_at: '2024-01-15T10:00:00Z',
  },
];

const mockItems: ReconciliationItem[] = [
  {
    id: 'i1',
    item_code: 'STEEL-REBAR-12MM',
    source_values: { engineering: 120, warehouse: 116, sap: 115, purchasing: 118 },
    variance: 5,
    variance_percentage: 4.17,
    status: 'variance',
    root_cause: 'Missing goods receipt in SAP',
    recommended_action: 'Post missing GR document',
  },
  {
    id: 'i2',
    item_code: 'CONCRETE-C35',
    source_values: { engineering: 450, warehouse: 450, sap: 450, purchasing: 450 },
    variance: 0,
    variance_percentage: 0,
    status: 'matched',
  },
  {
    id: 'i3',
    item_code: 'CEMENT-OPC',
    source_values: { engineering: 200, warehouse: 195, sap: 195, purchasing: 200 },
    variance: 5,
    variance_percentage: 2.5,
    status: 'variance',
    root_cause: 'Receiving delay at warehouse',
    recommended_action: 'Verify delivery schedule',
  },
];

export default function ReconciliationPage() {
  const [runs] = useState<ReconciliationRun[]>(mockRuns);
  const [selectedRun, setSelectedRun] = useState<ReconciliationRun | null>(mockRuns[0]);
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  const filteredItems = mockItems.filter((item) => {
    if (filter === 'all') return true;
    return item.status === filter;
  });

  const runReconciliation = () => {
    toast.success('Reconciliation queued!');
  };

  const approveItem = (itemId: string) => {
    toast.success('Item approved');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reconciliation</h1>
          <p className="text-gray-500 mt-1">Compare and reconcile data across sources</p>
        </div>
        <button
          onClick={runReconciliation}
          className="btn-primary flex items-center gap-2 text-sm"
        >
          <Play className="w-4 h-4" />
          Run Reconciliation
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Total Items</p>
          <p className="text-2xl font-bold text-gray-900">{selectedRun?.total_items || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Matched</p>
          <p className="text-2xl font-bold text-success-600">{selectedRun?.matched_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Variances</p>
          <p className="text-2xl font-bold text-danger-600">{selectedRun?.variance_count || 0}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Accuracy</p>
          <p className="text-2xl font-bold text-primary-600">
            {selectedRun?.total_items
              ? ((selectedRun.matched_count / selectedRun.total_items) * 100).toFixed(1)
              : 0}
            %
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Runs List */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900">Runs</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {runs.map((run) => (
              <div
                key={run.id}
                onClick={() => setSelectedRun(run)}
                className={`p-4 cursor-pointer transition-colors ${
                  selectedRun?.id === run.id ? 'bg-primary-50 border-l-4 border-primary-500' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{run.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(run.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`badge ${getStatusColor(run.status)}`}>
                    {run.status}
                  </span>
                </div>
                {run.status === 'completed' && (
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>{run.total_items} items</span>
                    <span>{run.variance_count} variances</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Items List */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Reconciliation Items</h3>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All</option>
                <option value="matched">Matched</option>
                <option value="variance">Variance</option>
              </select>
            </div>
          </div>

          <div className="divide-y divide-gray-100">
            {filteredItems.map((item) => (
              <div key={item.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => setExpandedItem(expandedItem === item.id ? null : item.id)}
                >
                  <div className="flex items-center gap-3">
                    {item.status === 'matched' ? (
                      <CheckCircle className="w-5 h-5 text-success-500" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-danger-500" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900">{item.item_code}</p>
                      <div className="flex items-center gap-2 mt-1">
                        {Object.entries(item.source_values).map(([source, value]) => (
                          <span key={source} className="text-xs text-gray-500">
                            {source}: {value}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {item.variance > 0 && (
                      <span className="text-sm font-medium text-danger-600">
                        -{item.variance} ({item.variance_percentage?.toFixed(1)}%)
                      </span>
                    )}
                    {expandedItem === item.id ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedItem === item.id && item.status === 'variance' && (
                  <div className="mt-4 ml-8 p-4 bg-gray-50 rounded-lg animate-fade-in">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      {Object.entries(item.source_values).map(([source, value]) => (
                        <div key={source} className="bg-white p-3 rounded-lg">
                          <p className="text-xs text-gray-500 capitalize">{source}</p>
                          <p className="text-lg font-semibold text-gray-900">{value}</p>
                        </div>
                      ))}
                    </div>

                    {item.root_cause && (
                      <div className="mb-3">
                        <p className="text-xs text-gray-500 mb-1">Root Cause Analysis</p>
                        <p className="text-sm text-gray-700 bg-amber-50 p-2 rounded-lg border border-amber-200">
                          {item.root_cause}
                        </p>
                      </div>
                    )}

                    {item.recommended_action && (
                      <div className="mb-3">
                        <p className="text-xs text-gray-500 mb-1">Recommended Action</p>
                        <p className="text-sm text-primary-700 bg-primary-50 p-2 rounded-lg border border-primary-200">
                          {item.recommended_action}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-2 mt-4">
                      <button
                        onClick={() => approveItem(item.id)}
                        className="btn-primary text-sm flex items-center gap-2"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Approve & Action
                      </button>
                      <button className="btn-secondary text-sm">Investigate</button>
                      <button className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                        Ignore
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
