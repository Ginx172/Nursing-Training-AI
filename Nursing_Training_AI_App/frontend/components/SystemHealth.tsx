import React, { useState, useEffect } from 'react';
import api from '../../lib/api';
import { Activity, Database, Server, AlertCircle, CheckCircle2 } from 'lucide-react';

interface HealthStatus {
  status: string;
  primary_connected: boolean;
  pool_status: any;
  overall_status: string;
}

const SystemHealth = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const checkHealth = async () => {
    try {
      setLoading(true);
      // Assuming backend is proxy-ed or CORS allows localhost:8000
      const response = await api.get('/api/health');
      setHealth(response.data);
      setError('');
    } catch (err) {
      setError('System is offline or unreachable');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          System Health
        </h2>
        <button 
          onClick={checkHealth}
          className="text-sm text-slate-500 hover:text-blue-600 transition-colors"
        >
          Refresh
        </button>
      </div>

      {loading && !health ? (
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-slate-100 rounded w-3/4"></div>
          <div className="h-4 bg-slate-100 rounded w-1/2"></div>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-600 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Server className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-medium">API Service</span>
            </div>
            <span className="flex items-center gap-1.5 text-sm text-emerald-600 font-medium bg-emerald-50 px-2 py-1 rounded">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Operational
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <Database className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-medium">Database (PostgreSQL)</span>
            </div>
            {health?.primary_connected ? (
               <span className="flex items-center gap-1.5 text-sm text-emerald-600 font-medium">
                 <CheckCircle2 className="w-4 h-4" /> Connected
               </span>
            ) : (
               <span className="flex items-center gap-1.5 text-sm text-red-600 font-medium">
                 <AlertCircle className="w-4 h-4" /> Disconnected
               </span>
            )}
          </div>
          
          <div className="text-xs text-slate-400 mt-2 text-center">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemHealth;
