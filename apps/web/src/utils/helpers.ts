import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    completed: 'bg-success-500 text-white',
    processing: 'bg-primary-500 text-white',
    pending: 'bg-warning-500 text-white',
    failed: 'bg-danger-500 text-white',
    active: 'bg-success-500 text-white',
    variance: 'bg-danger-500 text-white',
    matched: 'bg-success-500 text-white',
    critical: 'bg-danger-700 text-white',
    warning: 'bg-warning-500 text-white',
    info: 'bg-primary-500 text-white',
  };
  return colors[status] || 'bg-gray-500 text-white';
}

export function getConfidenceBadge(confidence: number): { label: string; color: string } {
  if (confidence >= 0.95) return { label: 'Auto Accept', color: 'bg-success-500' };
  if (confidence >= 0.80) return { label: 'Review', color: 'bg-warning-500' };
  return { label: 'Human Review', color: 'bg-danger-500' };
}
