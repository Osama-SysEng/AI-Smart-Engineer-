'use client';

import { useState, useRef, useEffect } from 'react';
import api from '@/lib/api';
import { AIChatMessage } from '@/types';
import {
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  Wrench,
  FileSearch,
  BarChart3,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { formatDate } from '@/utils/helpers';
import toast from 'react-hot-toast';

const suggestedQueries = [
  { icon: FileSearch, text: 'Review Site 3 documents and compare with SAP' },
  { icon: BarChart3, text: 'Generate weekly material variance report' },
  { icon: AlertCircle, text: 'Why is steel quantity different from SAP?' },
  { icon: Wrench, text: 'Extract all data from the structural drawing' },
];

export default function AIChatPage() {
  const [messages, setMessages] = useState<AIChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am your AI Engineering Assistant. I can help you with:

• Analyzing documents and drawings
• Comparing data across sources
• Detecting anomalies and variances
• Generating reports
• Querying SAP data
• Creating tasks and workflows

What would you like to work on today?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text: string = input) => {
    if (!text.trim()) return;

    const userMessage: AIChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/api/v1/ai/chat', {
        message: text,
        context: {},
      });

      const assistantMessage: AIChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        tools_used: response.data.tools_used,
        confidence: response.data.confidence,
        requires_approval: response.data.requires_approval,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Failed to get response');
      const errorMessage: AIChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Engineering Assistant</h1>
            <p className="text-sm text-gray-500">Powered by multiple AI models with evidence-based reasoning</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge bg-success-100 text-success-700">Online</span>
          <span className="text-xs text-gray-400">GPT-4o • Claude • Local</span>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'assistant'
                    ? 'bg-primary-100'
                    : 'bg-gray-100'
                }`}
              >
                {message.role === 'assistant' ? (
                  <Bot className="w-4 h-4 text-primary-600" />
                ) : (
                  <User className="w-4 h-4 text-gray-600" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`max-w-[80%] ${
                  message.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`rounded-2xl px-5 py-3 ${
                    message.role === 'assistant'
                      ? 'bg-gray-50 text-gray-900'
                      : 'bg-primary-600 text-white'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>

                {/* Metadata */}
                <div className="flex items-center gap-3 mt-1 px-1">
                  <span className="text-xs text-gray-400">
                    {formatDate(message.timestamp)}
                  </span>
                  {message.tools_used && message.tools_used.length > 0 && (
                    <span className="text-xs text-primary-600 flex items-center gap-1">
                      <Wrench className="w-3 h-3" />
                      {message.tools_used.length} tools used
                    </span>
                  )}
                  {message.confidence !== undefined && (
                    <span className="text-xs text-gray-500">
                      Confidence: {(message.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                  {message.requires_approval && (
                    <span className="text-xs text-warning-600 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      Requires approval
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary-600" />
              </div>
              <div className="bg-gray-50 rounded-2xl px-5 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Queries (only when no messages except welcome) */}
        {messages.length === 1 && (
          <div className="px-6 pb-4">
            <p className="text-xs text-gray-500 mb-2">Suggested queries:</p>
            <div className="grid grid-cols-2 gap-2">
              {suggestedQueries.map((query, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(query.text)}
                  className="flex items-center gap-2 p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
                >
                  <query.icon className="w-4 h-4 text-primary-600 flex-shrink-0" />
                  <span className="text-xs text-gray-700">{query.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything about your engineering data..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-sm"
                rows={2}
              />
            </div>
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="px-4 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            AI responses are evidence-based. Always verify critical data before acting.
          </p>
        </div>
      </div>
    </div>
  );
}
