'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useStore } from '@/store';
import Sidebar from '@/components/layout/Sidebar';
import Navbar from '@/components/layout/Navbar';
import { Toaster } from 'react-hot-toast';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isSidebarOpen } = useStore();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token && pathname !== '/login') {
      router.push('/login');
    }
  }, [pathname, router]);

  if (pathname === '/login') {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <Navbar />
      <main
        className={`pt-16 transition-all duration-300 ${
          isSidebarOpen ? 'ml-64' : 'ml-16'
        }`}
      >
        <div className="p-6">{children}</div>
      </main>
      <Toaster position="top-right" />
    </div>
  );
}
