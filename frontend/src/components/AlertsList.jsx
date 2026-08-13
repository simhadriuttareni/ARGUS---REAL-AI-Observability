import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function AlertsList({ full = false }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/alerts`);
        setAlerts(response.data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  const displayAlerts = full ? alerts : alerts.slice(0, 5);

  if (displayAlerts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        ✅ No active alerts
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold">🚨 Active Alerts</h2>
        <span className="text-sm text-gray-500">{alerts.length} total</span>
      </div>
      <div className="divide-y divide-gray-200">
        {displayAlerts.map((alert) => (
          <AlertItem key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
}

function AlertItem({ alert }) {
  const severityColors = {
    critical: 'bg-red-100 text-red-800 border-red-400',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-400',
    info: 'bg-blue-100 text-blue-800 border-blue-400'
  };
  
  const severityIcons = {
    critical: '🚨',
    warning: '⚠️',
    info: 'ℹ️'
  };

  return (
    <div className={`px-6 py-4 border-l-4 ${severityColors[alert.severity] || 'bg-gray-100 text-gray-800 border-gray-400'}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xl">{severityIcons[alert.severity] || '🔔'}</span>
            <span className="font-medium">{alert.rule_name}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              alert.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {alert.status}
            </span>
          </div>
          <p className="text-sm text-gray-600 mt-1">{alert.reason}</p>
          <div className="text-xs text-gray-400 mt-1">
            {alert.model} • {alert.provider}
          </div>
        </div>
        <div className="text-xs text-gray-400">
          {new Date(alert.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}