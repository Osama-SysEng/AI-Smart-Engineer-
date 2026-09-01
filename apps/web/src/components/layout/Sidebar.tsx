'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useStore } from '@/store';
import {
  LayoutDashboard,
  FolderOpen,
  FileText,
  Bot,
  GitCompare,
  Workflow,
  BarChart3,
  Bell,
  Settings,
  Shield,
  ChevronLeft,
  ChevronRight,
  Building2,
} from 'lucide-react';
import { cn } from '@/utils/helpers';

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
  { icon: Building2, label: 'Projects', href: '/projects' },
  { icon: FolderOpen, label: 'Sites', href: '/sites' },
  { icon: FileText, label: 'Documents', href: '/documents' },
  { icon: Bot, label: 'AI Assistant', href: '/ai-chat' },
  { icon: GitCompare, label: 'Reconciliation', href: '/reconciliation' },
  { icon: Workflow, label: 'Workflows', href: '/workflows' },
  { icon: BarChart3, label: 'Analytics', href: '/analytics' },
  { icon: Bell, label: 'Notifications', href: '/notifications' },
  { icon: Shield, label: 'Audit', href: '/audit' },
  { icon: Settings, label: 'Settings', href: '/settings' },
];

export default function Sidebar() {
  const { isSidebarOpen, toggleSidebar, user } = useStore();
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-white border-r border-gray-200 transition-all duration-300 z-50',
        isSidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        {isSidebarOpen && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900 text-sm">AI Engineer</span>
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'sidebar-item',
                isActive && 'active',
                !isSidebarOpen && 'justify-center px-2'
              )}
              title={!isSidebarOpen ? item.label : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {isSidebarOpen && <span className="text-sm">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      {isSidebarOpen && user && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-primary-700 font-medium text-sm">
                {user.full_name.charAt(0)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
