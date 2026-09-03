import { apiClient } from './client';
import { mockDb } from '../mock/db';

export const dashboardApi = {
  getDashboardData: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data;
  },
  getKPIs: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data.kpis;
  },
  getActivityFeed: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data.activityFeed;
  },
  getTrendData: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data.trendData;
  },
  getRiskDistribution: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data.riskDistribution;
  },
  getRecentPredictions: async () => {
    // Keep mock for now since we didn't add it to FastAPI yet
    return mockDb.recentPredictions;
  }
};
