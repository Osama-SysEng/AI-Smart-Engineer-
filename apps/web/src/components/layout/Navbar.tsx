'use client';

import { useStore } from '@/store';
import { Bell, Search, LogOut, Moon, Sun } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { user, unreadCount, logout, isSidebarOpen } = useStore();
  const [darkMode, setDarkMode] = useState(false);

  return (
    <header
      className={`fixed top-0 right-0 h-16 bg-white border-b border-gray-200 z-40 transition-all duration-300 ${
        isSidebarOpen ? 'left-64' : 'left-16'
      }`}
    >
      <div className="h-full px-6 flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents, projects, materials..."
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {/* Dark mode toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          {/* Notifications */}
          <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Logout */}
          <button
            onClick={logout}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
