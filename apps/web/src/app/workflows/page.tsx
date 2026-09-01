'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { useStore } from '@/store';
import { Task } from '@/types';
import {
  Plus,
  Play,
  Pause,
  CheckCircle,
  Clock,
  AlertCircle,
  MoreVertical,
  Filter,
  Search,
} from 'lucide-react';
import { getStatusColor, formatDate } from '@/utils/helpers';
import toast from 'react-hot-toast';

export default function WorkflowsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const currentProject = useStore((state) => state.currentProject);

  useEffect(() => {
    let active = true;
    api.get('/api/v1/workflows/tasks', { params: currentProject?.id ? { project_id: currentProject.id } : {} })
      .then((res) => { if (active) setTasks(res.data); })
      .catch(() => toast.error('Failed to load tasks'))
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [currentProject?.id]);

  const createTask = async () => {
    if (!currentProject?.id) { toast.error('Select project first'); return; }
    const title = window.prompt('Task title');
    if (!title?.trim()) return;
    try {
      const res = await api.post('/api/v1/workflows/tasks', { project_id: currentProject.id, title: title.trim(), priority: 'medium' });
      setTasks((prev) => [res.data, ...prev]);
      toast.success('Task created');
    } catch {
      toast.error('Failed to create task');
    }
  };
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filtered = tasks.filter((task) => {
    const matchesFilter = filter === 'all' || task.status === filter;
    const matchesSearch =
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      task.description?.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-danger-100 text-danger-700';
      case 'high':
        return 'bg-warning-100 text-warning-700';
      case 'medium':
        return 'bg-primary-100 text-primary-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows & Tasks</h1>
          <p className="text-gray-500 mt-1">Manage tasks and automated workflows</p>
        </div>
        <button
          onClick={createTask}
          className="btn-primary flex items-center gap-2 text-sm"
        >
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Total Tasks</p>
          <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Pending</p>
          <p className="text-2xl font-bold text-warning-600">
            {tasks.filter((t) => t.status === 'pending').length}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">In Progress</p>
          <p className="text-2xl font-bold text-primary-600">
            {tasks.filter((t) => t.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-2xl font-bold text-success-600">
            {tasks.filter((t) => t.status === 'completed').length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tasks..."
            className="input-field pl-10 text-sm"
          />
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="input-field text-sm w-40"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Tasks Table */}
      {loading && <div className="text-sm text-gray-500">Loading tasks...</div>}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Task</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assigned</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{task.title}</p>
                      <p className="text-xs text-gray-500 mt-1">{task.description}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`badge ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`badge ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{task.assigned_to}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {task.due_date ? formatDate(task.due_date) : '-'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {task.status === 'pending' && (
                        <button
                          onClick={() => toast.success('Task started')}
                          className="p-1.5 hover:bg-primary-50 rounded-lg text-primary-600 transition-colors"
                          title="Start"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      )}
                      {task.status === 'in_progress' && (
                        <button
                          onClick={() => toast.success('Task completed')}
                          className="p-1.5 hover:bg-success-50 rounded-lg text-success-600 transition-colors"
                          title="Complete"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                      <button className="p-1.5 hover:bg-gray-100 rounded-lg text-gray-400 transition-colors">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
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
