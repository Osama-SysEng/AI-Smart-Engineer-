'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import api from '@/lib/api';
import { Document, ExtractedEntity } from '@/types';
import {
  Upload,
  FileText,
  Image,
  Table,
  CheckCircle,
  AlertTriangle,
  Eye,
  Download,
  Trash2,
  Loader2,
  Search,
  Filter,
} from 'lucide-react';
import { formatFileSize, getStatusColor, getConfidenceBadge } from '@/utils/helpers';
import toast from 'react-hot-toast';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      filename: 'Site-03-Structural-R04.pdf',
      original_filename: 'Site-03-Structural-R04.pdf',
      file_type: '.pdf',
      file_size: 2457600,
      status: 'completed',
      processing_progress: 100,
      confidence: 0.97,
      extracted_count: 47,
      error_count: 0,
      review_required: false,
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: '2',
      filename: 'BOQ_Site_05.xlsx',
      original_filename: 'BOQ_Site_05.xlsx',
      file_type: '.xlsx',
      file_size: 512000,
      status: 'processing',
      processing_progress: 65,
      confidence: 0.0,
      extracted_count: 0,
      error_count: 0,
      review_required: false,
      created_at: '2024-01-15T11:00:00Z',
    },
    {
      id: '3',
      filename: 'Drawing_R03.dwg',
      original_filename: 'Drawing_R03.dwg',
      file_type: '.dwg',
      file_size: 10485760,
      status: 'pending',
      processing_progress: 0,
      confidence: 0.0,
      extracted_count: 0,
      error_count: 0,
      review_required: false,
      created_at: '2024-01-15T11:30:00Z',
    },
  ]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    for (const file of acceptedFiles) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_id', 'default');

      try {
        await api.post('/api/v1/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        toast.success(`Uploaded: ${file.name}`);
      } catch (error) {
        toast.error(`Failed to upload: ${file.name}`);
      }
    }
    setUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff'],
    },
  });

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return <FileText className="w-5 h-5 text-red-500" />;
    if (type.includes('xls') || type.includes('csv')) return <Table className="w-5 h-5 text-green-500" />;
    if (type.includes('image')) return <Image className="w-5 h-5 text-blue-500" />;
    return <FileText className="w-5 h-5 text-gray-500" />;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Document Center</h1>
          <p className="text-gray-500 mt-1">Upload, process, and manage engineering documents</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              className="input-field pl-10 text-sm w-64"
            />
          </div>
          <button className="btn-secondary flex items-center gap-2 text-sm">
            <Filter className="w-4 h-4" />
            Filter
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400 bg-white'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        {uploading ? (
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin" />
            <p className="text-gray-600">Uploading...</p>
          </div>
        ) : (
          <>
            <p className="text-gray-600 font-medium">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to select'}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Supports PDF, Excel, Word, Images, DWG (max 100MB)
            </p>
          </>
        )}
      </div>

      {/* Document Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document List */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="font-semibold text-gray-900">Documents ({documents.length})</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => setSelectedDoc(doc)}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedDoc?.id === doc.id ? 'bg-primary-50 border-l-4 border-primary-500' : ''
                }`}
              >
                <div className="flex items-center gap-4">
                  {getFileIcon(doc.file_type)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 truncate">{doc.original_filename}</p>
                      {doc.review_required && (
                        <AlertTriangle className="w-4 h-4 text-warning-500" />
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs text-gray-500">{formatFileSize(doc.file_size)}</span>
                      <span className={`badge ${getStatusColor(doc.status)}`}>
                        {doc.status}
                      </span>
                      {doc.confidence > 0 && (
                        <span className={`badge ${getConfidenceBadge(doc.confidence).color} text-white`}>
                          {getConfidenceBadge(doc.confidence).label}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {doc.status === 'processing' && (
                      <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
                    )}
                    {doc.status === 'completed' && (
                      <CheckCircle className="w-4 h-4 text-success-500" />
                    )}
                  </div>
                </div>
                {doc.status === 'processing' && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-primary-500 h-1.5 rounded-full transition-all duration-500"
                        style={{ width: `${doc.processing_progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{doc.processing_progress}% processed</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Document Preview / Details */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          {selectedDoc ? (
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Document Details</h3>

              {/* Preview placeholder */}
              <div className="aspect-[3/4] bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-16 h-16 text-gray-300" />
              </div>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Filename</span>
                  <span className="text-sm font-medium text-gray-900 truncate max-w-[200px]">
                    {selectedDoc.original_filename}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Size</span>
                  <span className="text-sm font-medium text-gray-900">
                    {formatFileSize(selectedDoc.file_size)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Status</span>
                  <span className={`badge ${getStatusColor(selectedDoc.status)}`}>
                    {selectedDoc.status}
                  </span>
                </div>
                {selectedDoc.confidence > 0 && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Confidence</span>
                    <span className="text-sm font-medium text-gray-900">
                      {(selectedDoc.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                {selectedDoc.extracted_count > 0 && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Entities</span>
                    <span className="text-sm font-medium text-gray-900">
                      {selectedDoc.extracted_count}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-6 space-y-2">
                <button className="w-full btn-primary text-sm flex items-center justify-center gap-2">
                  <Eye className="w-4 h-4" />
                  View Full Document
                </button>
                <button className="w-full btn-secondary text-sm flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Download
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-danger-600 hover:bg-danger-50 rounded-lg transition-colors">
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Select a document to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
