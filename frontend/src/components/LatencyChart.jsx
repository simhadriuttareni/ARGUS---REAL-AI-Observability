import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function LatencyChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLatencyData = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/metrics/latency`);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching latency data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchLatencyData();
  }, []);

  if (loading) return <div className="text-center py-8">Loading...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-semibold mb-4">⏱️ Latency Trends</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="latency" stroke="#6366f1" name="Latency (ms)" />
          <Line type="monotone" dataKey="ttft" stroke="#8b5cf6" name="TTFT (ms)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}