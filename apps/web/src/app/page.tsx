'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/store';
import api from '@/lib/api';
import { DashboardStats } from '@/types';
import {
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Activity,
  Zap,
  Database,
} from 'lucide-react';
import { formatNumber, getStatusColor } from '@/utils/helpers';

const StatCard = ({ title, value, icon: Icon, color, subtitle }: any) => (
  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 card-hover">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm text-gray-500 mb-1">{title}</p>
        <h3 className="text-2xl font-bold text-gray-900">{value}</h3>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
    </div>
  </div>
);

const ProgressBar = ({ label, value, color }: any) => (
  <div className="mb-4">
    <div className="flex justify-between mb-1">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="text-sm font-medium text-gray-900">{value}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${value}%` }}
      />
    </div>
  </div>
);

export default function Dashboard() {
  const { stats, setStats } = useStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/v1/analytics/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>
    );
  }

  const data = stats || {
    total_documents: 0,
    processing_documents: 0,
    total_errors: 0,
    pending_tasks: 0,
    variance_count: 0,
    automation_rate: 0,
    data_quality_score: 0,
    sap_sync_success_rate: 0,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Real-time overview of your engineering operations</p>
        </div>
        <div className="flex gap-3">
          <select className="input-field text-sm py-2">
            <option>All Projects</option>
            <option>Project Alpha</option>
            <option>Project Beta</option>
          </select>
          <button className="btn-primary text-sm">Generate Report</button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Documents"
          value={data.total_documents}
          icon={FileText}
          color="bg-blue-500"
          subtitle={`${data.processing_documents} processing`}
        />
        <StatCard
          title="Pending Tasks"
          value={data.pending_tasks}
          icon={Clock}
          color="bg-amber-500"
        />
        <StatCard
          title="Open Variances"
          value={data.variance_count}
          icon={AlertTriangle}
          color="bg-red-500"
        />
        <StatCard
          title="Total Errors"
          value={data.total_errors}
          icon={Activity}
          color="bg-purple-500"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Metrics */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Performance Metrics</h3>
          <ProgressBar
            label="Automation Rate"
            value={Math.round(data.automation_rate * 100)}
            color="bg-primary-500"
          />
          <ProgressBar
            label="Data Quality Score"
            value={Math.round(data.data_quality_score * 100)}
            color="bg-success-500"
          />
          <ProgressBar
            label="SAP Sync Success Rate"
            value={Math.round(data.sap_sync_success_rate * 100)}
            color="bg-blue-500"
          />
          <ProgressBar
            label="Document Processing"
            value={data.total_documents > 0 ? Math.round(((data.total_documents - data.processing_documents) / data.total_documents) * 100) : 0}
            color="bg-purple-500"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
              <FileText className="w-5 h-5 text-primary-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">Upload Document</p>
                <p className="text-xs text-gray-500">Process new engineering files</p>
              </div>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
              <Zap className="w-5 h-5 text-amber-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Run Reconciliation</p>
                <p className="text-xs text-gray-500">Compare cross-source data</p>
              </div>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
              <Database className="w-5 h-5 text-green-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Sync with SAP</p>
                <p className="text-xs text-gray-500">Update ERP records</p>
              </div>
            </button>
            <button className="w-full flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
              <TrendingUp className="w-5 h-5 text-purple-500" />
              <div>
                <p className="text-sm font-medium text-gray-900">Generate Report</p>
                <p className="text-xs text-gray-500">Create executive summary</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { action: 'Document processed', detail: 'Site-03-Structural-R04.pdf', time: '2 min ago', status: 'success' },
            { action: 'Variance detected', detail: 'Steel quantity mismatch in Site 4', time: '15 min ago', status: 'warning' },
            { action: 'SAP sync completed', detail: '125 records updated', time: '1 hour ago', status: 'success' },
            { action: 'AI extraction completed', detail: '47 entities extracted with 94% confidence', time: '2 hours ago', status: 'success' },
          ].map((activity, i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className={`w-2 h-2 rounded-full ${activity.status === 'success' ? 'bg-success-500' : 'bg-warning-500'}`} />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                <p className="text-xs text-gray-500">{activity.detail}</p>
              </div>
              <span className="text-xs text-gray-400">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
