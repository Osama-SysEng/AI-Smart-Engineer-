'use client';

import { useState } from 'react';
import { Site } from '@/types';
import {
  Building2,
  MapPin,
  FileText,
  Users,
  Plus,
  Search,
} from 'lucide-react';
import { getStatusColor } from '@/utils/helpers';

const mockSites: Site[] = [
  { id: '1', name: 'Main Tower', code: 'MT-01', location: 'Downtown District', status: 'active' },
  { id: '2', name: 'Parking Structure', code: 'PS-01', location: 'Downtown District', status: 'active' },
  { id: '3', name: 'Bridge A', code: 'BA-01', location: 'Northern Region', status: 'active' },
  { id: '4', name: 'Bridge B', code: 'BA-02', location: 'Northern Region', status: 'warning' },
  { id: '5', name: 'Factory A', code: 'FA-01', location: 'Eastern Industrial Zone', status: 'completed' },
];

export default function SitesPage() {
  const [sites] = useState<Site[]>(mockSites);
  const [search, setSearch] = useState('');

  const filtered = sites.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sites</h1>
          <p className="text-gray-500 mt-1">Manage construction sites and locations</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search sites..."
              className="input-field pl-10 text-sm w-64"
            />
          </div>
          <button className="btn-primary flex items-center gap-2 text-sm">
            <Plus className="w-4 h-4" />
            New Site
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((site) => (
          <div key={site.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 card-hover">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-primary-600" />
              </div>
              <span className={`badge ${getStatusColor(site.status)}`}>
                {site.status}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900">{site.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{site.code}</p>
            <div className="flex items-center gap-2 mt-3 text-sm text-gray-500">
              <MapPin className="w-4 h-4" />
              {site.location}
            </div>
            <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center gap-1 text-sm text-gray-600">
                <FileText className="w-4 h-4" />
                <span>12 Docs</span>
              </div>
              <div className="flex items-center gap-1 text-sm text-gray-600">
                <Users className="w-4 h-4" />
                <span>8 Staff</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
