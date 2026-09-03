/* eslint-disable react/only-export-components */
import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { AuthLayout } from '../layouts/AuthLayout';
import { Dashboard } from '../pages/Dashboard';
import { Analytics } from '../pages/Analytics';
import { Prediction } from '../pages/Prediction';
import { RiskMaps } from '../pages/RiskMaps';
import { Simulation } from '../pages/Simulation';
import { Users } from '../pages/Users';

import { Decisions } from '../pages/Decisions';
import { Reports } from '../pages/Reports';
import { Models } from '../pages/Models';
import { Datasets } from '../pages/Datasets';
import { History } from '../pages/History';
import { Notifications } from '../pages/Notifications';
import { Settings } from '../pages/Settings';
import { HelpCenter } from '../pages/HelpCenter';
import { PredictionCards } from '../pages/PredictionCards';

import { FairnessBias } from '../pages/FairnessBias';
import { DriftMonitoring } from '../pages/DriftMonitoring';
import { BusinessImpact } from '../pages/BusinessImpact';

// Temporary placeholder component until pages are built
const Placeholder = ({ title }: { title: string }) => (
  <div className="flex h-full items-center justify-center">
    <h1 className="text-2xl font-bold text-slate-400">{title}</h1>
  </div>
);

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <Placeholder title="404 Not Found" />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'prediction',
        element: <Prediction />,
      },
      {
        path: 'prediction-cards',
        element: <PredictionCards />,
      },
      {
        path: 'simulation',
        element: <Simulation />,
      },
      {
        path: 'maps',
        element: <RiskMaps />,
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
      {
        path: 'decisions',
        element: <Decisions />,
      },
      {
        path: 'reports',
        element: <Reports />,
      },
      {
        path: 'models',
        element: <Models />,
      },
      {
        path: 'drift',
        element: <DriftMonitoring />,
      },
      {
        path: 'fairness',
        element: <FairnessBias />,
      },
      {
        path: 'impact',
        element: <BusinessImpact />,
      },
      {
        path: 'datasets',
        element: <Datasets />,
      },
      {
        path: 'history',
        element: <History />,
      },
      {
        path: 'notifications',
        element: <Notifications />,
      },
      {
        path: 'admin',
        element: <Users />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
      {
        path: 'help',
        element: <HelpCenter />,
      },
    ],
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <Placeholder title="Login Form" />,
      },
      {
        path: 'register',
        element: <Placeholder title="Register Form" />,
      },
      {
        path: 'forgot-password',
        element: <Placeholder title="Forgot Password Form" />,
      }
    ],
  },
]);
