'use client';

import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  FileText,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

const monthlyData = [
  { month: 'Jan', documents: 120, processed: 110, errors: 5 },
  { month: 'Feb', documents: 150, processed: 145, errors: 3 },
  { month: 'Mar', documents: 180, processed: 175, errors: 8 },
  { month: 'Apr', documents: 220, processed: 210, errors: 4 },
  { month: 'May', documents: 280, processed: 270, errors: 6 },
  { month: 'Jun', documents: 350, processed: 340, errors: 2 },
];

const categoryData = [
  { name: 'Structural', value: 35, color: '#3b82f6' },
  { name: 'MEP', value: 25, color: '#22c55e' },
  { name: 'Civil', value: 20, color: '#f59e0b' },
  { name: 'Architectural', value: 15, color: '#ef4444' },
  { name: 'Other', value: 5, color: '#6b7280' },
];

const kpiCards = [
  { title: 'Automation Rate', value: '75%', change: '+12%', trend: 'up', icon: Activity },
  { title: 'Manual Hours Saved', value: '120h', change: '+24h', trend: 'up', icon: Clock },
  { title: 'Avg Processing Time', value: '3.5m', change: '-0.8m', trend: 'up', icon: FileText },
  { title: 'Error Rate', value: '2%', change: '-1.5%', trend: 'up', icon: AlertTriangle },
];

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('monthly');

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500 mt-1">Performance metrics and insights</p>
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="input-field text-sm w-40"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi) => (
          <div key={kpi.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 card-hover">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{kpi.title}</p>
                <h3 className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</h3>
                <div className={`flex items-center gap-1 mt-2 text-sm ${kpi.trend === 'up' ? 'text-success-600' : 'text-danger-600'}`}>
                  {kpi.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span>{kpi.change}</span>
                </div>
              </div>
              <div className="p-3 bg-primary-50 rounded-lg">
                <kpi.icon className="w-5 h-5 text-primary-600" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Processing</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="documents" fill="#3b82f6" name="Total" />
              <Bar dataKey="processed" fill="#22c55e" name="Processed" />
              <Bar dataKey="errors" fill="#ef4444" name="Errors" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="processed" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="errors" stroke="#ef4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Categories</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {categoryData.map((cat) => (
              <div key={cat.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                  <span className="text-sm text-gray-600">{cat.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{cat.value}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            {[
              { name: 'API Response Time', value: 95, status: 'good' },
              { name: 'Database Connection', value: 99, status: 'good' },
              { name: 'Queue Processing', value: 88, status: 'warning' },
              { name: 'AI Provider Availability', value: 100, status: 'good' },
              { name: 'Storage Capacity', value: 72, status: 'good' },
            ].map((metric) => (
              <div key={metric.name}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">{metric.name}</span>
                  <span className="text-sm font-medium text-gray-900">{metric.value}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      metric.status === 'good' ? 'bg-success-500' : 'bg-warning-500'
                    }`}
                    style={{ width: `${metric.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
