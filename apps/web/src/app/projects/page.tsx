'use client';

import { useState } from 'react';
import { Project } from '@/types';
import {
  Plus,
  Building2,
  MapPin,
  Users,
  FileText,
  Activity,
  MoreVertical,
  Search,
} from 'lucide-react';
import { getStatusColor } from '@/utils/helpers';

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Downtown Tower Complex',
    description: 'Mixed-use development with 45 floors',
    client: 'ABC Development',
    location: 'Downtown District',
    status: 'active',
    health_score: 92,
    sites: [
      { id: 's1', name: 'Main Tower', code: 'MT-01', status: 'active' },
      { id: 's2', name: 'Parking Structure', code: 'PS-01', status: 'active' },
    ],
    departments: [
      { id: 'd1', name: 'Structural', code: 'STR' },
      { id: 'd2', name: 'MEP', code: 'MEP' },
    ],
  },
  {
    id: '2',
    name: 'Highway Extension Phase 2',
    description: '12km highway extension with 3 bridges',
    client: 'Ministry of Transport',
    location: 'Northern Region',
    status: 'active',
    health_score: 78,
    sites: [
      { id: 's3', name: 'Bridge A', code: 'BA-01', status: 'active' },
      { id: 's4', name: 'Bridge B', code: 'BA-02', status: 'warning' },
    ],
    departments: [
      { id: 'd3', name: 'Civil', code: 'CIV' },
      { id: 'd4', name: 'Survey', code: 'SUR' },
    ],
  },
  {
    id: '3',
    name: 'Industrial Park Expansion',
    description: 'Manufacturing facility expansion',
    client: 'Industrial Corp',
    location: 'Eastern Industrial Zone',
    status: 'completed',
    health_score: 100,
    sites: [
      { id: 's5', name: 'Factory A', code: 'FA-01', status: 'completed' },
    ],
    departments: [
      { id: 'd5', name: 'Construction', code: 'CON' },
    ],
  },
];

export default function ProjectsPage() {
  const [projects] = useState<Project[]>(mockProjects);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'bg-success-500';
    if (score >= 70) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-500 mt-1">Manage your engineering projects and sites</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects..."
              className="input-field pl-10 text-sm w-64"
            />
          </div>
          <button className="btn-primary flex items-center gap-2 text-sm">
            <Plus className="w-4 h-4" />
            New Project
          </button>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            onClick={() => setSelectedProject(project)}
            className={`bg-white rounded-xl shadow-sm border transition-all cursor-pointer card-hover ${
              selectedProject?.id === project.id ? 'border-primary-500 ring-2 ring-primary-100' : 'border-gray-100'
            }`}
          >
            {/* Health Score */}
            <div className="px-6 pt-6 flex items-start justify-between">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${getHealthColor(project.health_score)}`}>
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <span className="text-2xl font-bold text-gray-900">{project.health_score}</span>
                  <p className="text-xs text-gray-500">Health Score</p>
                </div>
              </div>
            </div>

            <div className="px-6 py-4">
              <h3 className="font-semibold text-gray-900">{project.name}</h3>
              <p className="text-sm text-gray-500 mt-1 line-clamp-2">{project.description}</p>

              <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {project.location}
                </span>
                <span className={`badge ${getStatusColor(project.status)}`}>
                  {project.status}
                </span>
              </div>

              <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Building2 className="w-4 h-4" />
                  <span>{project.sites.length} Sites</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Users className="w-4 h-4" />
                  <span>{project.departments.length} Depts</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <FileText className="w-4 h-4" />
                  <span>24 Docs</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Project Details */}
      {selectedProject && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-fade-in">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">{selectedProject.name} - Details</h3>
            <button className="p-2 hover:bg-gray-100 rounded-lg">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Sites */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Sites</h4>
              <div className="space-y-2">
                {selectedProject.sites.map((site) => (
                  <div key={site.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{site.name}</p>
                      <p className="text-xs text-gray-500">{site.code}</p>
                    </div>
                    <span className={`badge ${getStatusColor(site.status)}`}>
                      {site.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Departments */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Departments</h4>
              <div className="space-y-2">
                {selectedProject.departments.map((dept) => (
                  <div key={dept.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{dept.name}</p>
                      <p className="text-xs text-gray-500">{dept.code}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
