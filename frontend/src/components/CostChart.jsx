import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899'];

export default function CostChart({ detailed = false }) {
  const [data, setData] = useState({ by_model: [], by_provider: [], total: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCostData = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/metrics/cost`);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching cost data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCostData();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  if (detailed) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">💰 Cost Breakdown by Model</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.by_model}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
              <Legend />
              <Bar dataKey="cost" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Cost by Provider</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.by_provider}
                dataKey="cost"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {data.by_provider.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Total Cost</span>
            <span className="text-2xl font-bold">${data.total.toFixed(4)}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-md font-semibold">💰 Cost Overview</h3>
        <span className="text-sm text-gray-500">${data.total.toFixed(4)} total</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data.by_model}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
          <Bar dataKey="cost" fill="#6366f1" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}