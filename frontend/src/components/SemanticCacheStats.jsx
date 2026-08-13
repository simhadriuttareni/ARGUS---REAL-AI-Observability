import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7'];

export default function SemanticCacheStats() {
  const [stats, setStats] = useState({
    entries: 0,
    responses: 0,
    hit_rate: 0,
    by_model: [],
    recent_hits: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/cache/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching cache stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  const pieData = [
    { name: 'Hits', value: stats.hit_rate || 0 },
    { name: 'Misses', value: 100 - (stats.hit_rate || 0) }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">💾 Semantic Cache</h3>
        
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 rounded p-4 text-center">
            <div className="text-2xl font-bold text-indigo-600">{stats.entries}</div>
            <div className="text-sm text-gray-500">Cached Embeddings</div>
          </div>
          <div className="bg-gray-50 rounded p-4 text-center">
            <div className="text-2xl font-bold text-indigo-600">{stats.responses}</div>
            <div className="text-sm text-gray-500">Cached Responses</div>
          </div>
          <div className="bg-gray-50 rounded p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{stats.hit_rate}%</div>
            <div className="text-sm text-gray-500">Hit Rate</div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Hit / Miss Ratio</h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Cache Hits by Model</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats.by_model}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="hits" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Cache Hits</h4>
        {stats.recent_hits && stats.recent_hits.length > 0 ? (
          <div className="space-y-2">
            {stats.recent_hits.map((hit, index) => (
              <div key={index} className="text-sm text-gray-600 border-b border-gray-100 py-1">
                <span className="font-medium">"{hit.query}"</span>
                <span className="text-gray-400 ml-2">→ {hit.response.slice(0, 50)}...</span>
                <span className="text-xs text-gray-400 ml-2">similarity: {hit.similarity.toFixed(3)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-500">No recent cache hits</div>
        )}
      </div>
    </div>
  );
}