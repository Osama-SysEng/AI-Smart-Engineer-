'use client';

import { useState } from 'react';
import { Notification } from '@/types';
import {
  Bell,
  CheckCircle,
  AlertTriangle,
  Info,
  X,
  Trash2,
  Filter,
} from 'lucide-react';
import { getStatusColor, formatDate } from '@/utils/helpers';

const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'Variance Detected',
    message: 'Steel quantity in Site 4 differs from SAP by 5 units',
    severity: 'warning',
    read: false,
    created_at: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    title: 'Document Processing Complete',
    message: 'Site-03-Structural-R04.pdf has been processed with 97% confidence',
    severity: 'info',
    read: false,
    created_at: '2024-01-15T09:00:00Z',
  },
  {
    id: '3',
    title: 'Approval Required',
    message: 'Reconciliation item STEEL-REBAR-12MM requires your approval',
    severity: 'critical',
    read: true,
    created_at: '2024-01-14T16:00:00Z',
  },
  {
    id: '4',
    title: 'SAP Sync Failed',
    message: 'Connection timeout during sync operation. Retry scheduled.',
    severity: 'warning',
    read: true,
    created_at: '2024-01-14T14:30:00Z',
  },
];

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [filter, setFilter] = useState('all');

  const filtered = notifications.filter((n) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    return n.severity === filter;
  });

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-5 h-5 text-danger-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-warning-500" />;
      default:
        return <Info className="w-5 h-5 text-primary-500" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-500 mt-1">Stay updated on your engineering operations</p>
        </div>
        <div className="flex gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-field text-sm w-40"
          >
            <option value="all">All</option>
            <option value="unread">Unread</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <button onClick={markAllAsRead} className="btn-secondary text-sm">
            Mark All Read
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="divide-y divide-gray-100">
          {filtered.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 hover:bg-gray-50 transition-colors ${
                !notification.read ? 'bg-blue-50/30' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                {getIcon(notification.severity)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className={`text-sm font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-600'}`}>
                      {notification.title}
                    </h4>
                    {!notification.read && (
                      <span className="w-2 h-2 bg-primary-500 rounded-full" />
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{notification.message}</p>
                  <p className="text-xs text-gray-400 mt-2">{formatDate(notification.created_at)}</p>
                </div>
                <div className="flex items-center gap-2">
                  {!notification.read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-primary-600 transition-colors"
                      title="Mark as read"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotification(notification.id)}
                    className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-danger-600 transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
