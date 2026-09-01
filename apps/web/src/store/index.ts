import { create } from 'zustand';
import { User, Project, DashboardStats, Notification, AIChatMessage } from '@/types';

interface AppState {
  user: User | null;
  projects: Project[];
  currentProject: Project | null;
  stats: DashboardStats | null;
  notifications: Notification[];
  unreadCount: number;
  chatMessages: AIChatMessage[];
  isSidebarOpen: boolean;
  isLoading: boolean;

  setUser: (user: User | null) => void;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  setStats: (stats: DashboardStats) => void;
  setNotifications: (notifications: Notification[]) => void;
  setUnreadCount: (count: number) => void;
  addChatMessage: (message: AIChatMessage) => void;
  toggleSidebar: () => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  projects: [],
  currentProject: null,
  stats: null,
  notifications: [],
  unreadCount: 0,
  chatMessages: [],
  isSidebarOpen: true,
  isLoading: false,

  setUser: (user) => set({ user }),
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),
  setStats: (stats) => set({ stats }),
  setNotifications: (notifications) => set({ notifications }),
  setUnreadCount: (count) => set({ unreadCount: count }),
  addChatMessage: (message) => set((state) => ({ 
    chatMessages: [...state.chatMessages, message] 
  })),
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setLoading: (loading) => set({ isLoading: loading }),
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, projects: [], currentProject: null });
  },
}));
