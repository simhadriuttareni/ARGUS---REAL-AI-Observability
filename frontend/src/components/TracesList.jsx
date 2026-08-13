import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function TracesList() {
  const [traces, setTraces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchTraces = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/traces?limit=50`);
        setTraces(response.data);
      } catch (error) {
        console.error('Error fetching traces:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTraces();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold">📈 Recent Traces</h2>
        <div className="flex space-x-2">
          <FilterButton active={filter === 'all'} onClick={() => setFilter('all')}>All</FilterButton>
          <FilterButton active={filter === 'success'} onClick={() => setFilter('success')}>✅ Success</FilterButton>
          <FilterButton active={filter === 'error'} onClick={() => setFilter('error')}>❌ Error</FilterButton>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tokens</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Latency</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {traces.map((trace) => (
              <tr key={trace.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-600">
                  {new Date(trace.start_time).toLocaleTimeString()}
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {trace.model}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {trace.provider}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {trace.total_tokens || 0}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  ${(trace.cost || 0).toFixed(4)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {trace.latency_ms ? `${trace.latency_ms.toFixed(0)}ms` : '-'}
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={trace.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FilterButton({ active, onClick, children }) {
  return (
    <button
      className={`px-3 py-1 text-sm rounded-md transition-colors ${
        active ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function StatusBadge({ status }) {
  const colors = {
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    pending: 'bg-yellow-100 text-yellow-800'
  };
  
  return (
    <span className={`px-2 py-1 text-xs rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status || 'unknown'}
    </span>
  );
}