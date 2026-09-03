export const mockDb = {
  kpis: {
    totalModels: 24,
    activeSimulations: 8,
    systemHealth: 98.4,
    criticalAlerts: 2,
    predictionsLast24h: 14502,
    avgConfidence: 94.2,
  },
  activityFeed: [
    { id: 1, type: 'alert', message: 'Risk threshold exceeded in region EU-West', time: '10 min ago', status: 'critical' },
    { id: 2, type: 'success', message: 'Model "Demand-Forecast-v2" deployed successfully', time: '45 min ago', status: 'success' },
    { id: 3, type: 'info', message: 'User "Jane Doe" initiated a new simulation', time: '2 hours ago', status: 'info' },
    { id: 4, type: 'warning', message: 'API rate limit warning (90% usage)', time: '3 hours ago', status: 'warning' },
  ],
  trendData: [
    { name: 'Mon', predictions: 4000, accuracy: 92 },
    { name: 'Tue', predictions: 3000, accuracy: 91 },
    { name: 'Wed', predictions: 2000, accuracy: 93 },
    { name: 'Thu', predictions: 2780, accuracy: 95 },
    { name: 'Fri', predictions: 1890, accuracy: 96 },
    { name: 'Sat', predictions: 2390, accuracy: 94 },
    { name: 'Sun', predictions: 3490, accuracy: 94 },
  ],
  riskDistribution: [
    { name: 'Low Risk', value: 400, color: '#22C55E' },
    { name: 'Medium Risk', value: 300, color: '#F59E0B' },
    { name: 'High Risk', value: 300, color: '#EF4444' },
    { name: 'Unknown', value: 100, color: '#64748B' },
  ],
  recentPredictions: [
    { id: 'PRD-1023', target: 'Q3 Revenue', result: '$4.2M', confidence: 94, status: 'Completed', date: '2026-09-01' },
    { id: 'PRD-1024', target: 'Supply Chain Disrupt', result: 'High Risk', confidence: 88, status: 'Completed', date: '2026-09-01' },
    { id: 'PRD-1025', target: 'Customer Churn (EU)', result: '12.4%', confidence: 91, status: 'Processing', date: '2026-09-01' },
    { id: 'PRD-1026', target: 'Equipment Failure', result: 'Low Risk', confidence: 99, status: 'Completed', date: '2026-08-31' },
  ]
};
