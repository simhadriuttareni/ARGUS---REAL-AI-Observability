import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ModelComparison() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/metrics/comparison`);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching comparison:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-semibold mb-4">📊 Model Comparison</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={100} />
          <Tooltip />
          <Legend />
          <Bar dataKey="latency" fill="#6366f1" name="Latency (ms)" />
          <Bar dataKey="cost" fill="#8b5cf6" name="Cost ($)" />
          <Bar dataKey="tokens" fill="#a855f7" name="Tokens/sec" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}