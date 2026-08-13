/**
 * ARGUS Dashboard Component
 * Main dashboard with metrics, charts, and real-time updates
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
    ResponsiveContainer
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e'];

/**
 * Main Dashboard Component
 */
export default function Dashboard() {
    const [metrics, setMetrics] = useState({
        totalTraces: 0,
        totalCost: 0,
        activeAlerts: 0,
        cacheHitRate: 0,
        avgLatency: 0,
        errorRate: 0,
    });
    const [recentTraces, setRecentTraces] = useState([]);
    const [latencyData, setLatencyData] = useState([]);
    const [costData, setCostData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // WebSocket for real-time updates
    const { isConnected, lastMessage } = useWebSocket('ws://localhost:8000/ws/monitor');

    // Fetch initial data
    const fetchDashboardData = useCallback(async () => {
        try {
            setLoading(true);
            const [metricsRes, tracesRes, latencyRes, costRes] = await Promise.all([
                axios.get('/api/v1/dashboard/metrics'),
                axios.get('/api/v1/traces?limit=20'),
                axios.get('/api/v1/metrics/latency?hours=24'),
                axios.get('/api/v1/metrics/cost?hours=24'),
            ]);

            setMetrics(metricsRes.data);
            setRecentTraces(tracesRes.data);
            setLatencyData(latencyRes.data);
            setCostData(costRes.data);
        } catch (err) {
            console.error('Error fetching dashboard data:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Update metrics from WebSocket
    useEffect(() => {
        if (lastMessage) {
            setMetrics(prev => ({
                ...prev,
                totalTraces: lastMessage.totalTraces || prev.totalTraces,
                activeAlerts: lastMessage.activeAlerts || prev.activeAlerts,
                cacheHitRate: lastMessage.cacheHitRate || prev.cacheHitRate,
            }));
        }
    }, [lastMessage]);

    // Initial data fetch
    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, [fetchDashboardData]);

    // Prepare chart data
    const latencyChartData = latencyData.map(item => ({
        time: new Date(item.timestamp).toLocaleTimeString(),
        latency: Math.round(item.latency_ms || 0),
        ttft: Math.round(item.ttft_ms || 0),
    }));

    const costChartData = costData.map(item => ({
        model: item.model || 'Unknown',
        cost: Math.round((item.cost || 0) * 10000) / 10000,
        tokens: item.tokens || 0,
    }));

    // Pie data for cost distribution
    const pieData = costChartData.map(item => ({
        name: item.model,
        value: item.cost,
    }));

    if (loading) {
        return <DashboardLoader />;
    }

    if (error) {
        return <DashboardError error={error} onRetry={fetchDashboardData} />;
    }

    return (
        <div className="space-y-6">
            {/* Connection Status */}
            <div className="flex items-center justify-end text-sm">
                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-gray-500">
                    {isConnected ? 'Live' : 'Reconnecting...'}
                </span>
            </div>

            {/* Metrics Grid */}
            <MetricsGrid metrics={metrics} />

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <LatencyChart data={latencyChartData} />
                <CostChart data={costChartData} pieData={pieData} />
            </div>

            {/* Recent Traces */}
            <RecentTracesTable traces={recentTraces} />
        </div>
    );
}

/**
 * Metrics Grid Component
 */
function MetricsGrid({ metrics }) {
    const metricCards = [
        {
            title: 'Total Traces',
            value: metrics.totalTraces || 0,
            icon: '📊',
            color: 'indigo',
        },
        {
            title: 'Total Cost',
            value: `$${(metrics.totalCost || 0).toFixed(4)}`,
            icon: '💰',
            color: 'green',
        },
        {
            title: 'Active Alerts',
            value: metrics.activeAlerts || 0,
            icon: '🚨',
            color: 'red',
        },
        {
            title: 'Cache Hit Rate',
            value: `${metrics.cacheHitRate || 0}%`,
            icon: '💾',
            color: 'purple',
        },
        {
            title: 'Avg Latency',
            value: `${Math.round(metrics.avgLatency || 0)}ms`,
            icon: '⏱️',
            color: 'blue',
        },
        {
            title: 'Error Rate',
            value: `${(metrics.errorRate || 0).toFixed(1)}%`,
            icon: '❌',
            color: 'yellow',
        },
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {metricCards.map((card, index) => (
                <MetricCard
                    key={index}
                    title={card.title}
                    value={card.value}
                    icon={card.icon}
                    color={card.color}
                />
            ))}
        </div>
    );
}

/**
 * Individual Metric Card
 */
function MetricCard({ title, value, icon, color }) {
    const colors = {
        indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
        green: 'bg-green-50 text-green-700 border-green-200',
        red: 'bg-red-50 text-red-700 border-red-200',
        purple: 'bg-purple-50 text-purple-700 border-purple-200',
        blue: 'bg-blue-50 text-blue-700 border-blue-200',
        yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    };

    return (
        <div className={`bg-white rounded-lg shadow-sm p-4 border ${colors[color] || 'bg-gray-50 border-gray-200'}`}>
            <div className="flex items-center justify-between">
                <span className="text-2xl">{icon}</span>
            </div>
            <div className="mt-2">
                <p className="text-xl font-bold">{value}</p>
                <p className="text-xs text-gray-500">{title}</p>
            </div>
        </div>
    );
}

/**
 * Latency Chart Component
 */
function LatencyChart({ data }) {
    return (
        <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-4">⏱️ Latency Trends</h3>
            <ResponsiveContainer width="100%" height={200}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="latency"
                        stroke="#6366f1"
                        strokeWidth={2}
                        name="Latency (ms)"
                        dot={false}
                    />
                    <Line
                        type="monotone"
                        dataKey="ttft"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        name="TTFT (ms)"
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

/**
 * Cost Chart Component
 */
function CostChart({ data, pieData }) {
    return (
        <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-4">💰 Cost Distribution</h3>
            <div className="grid grid-cols-2 gap-4">
                <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={pieData}
                                dataKey="value"
                                nameKey="name"
                                cx="50%"
                                cy="50%"
                                innerRadius={40}
                                outerRadius={70}
                                label={({ name, percent }) => 
                                    `${name} ${(percent * 100).toFixed(0)}%`
                                }
                                labelLine={false}
                            >
                                {pieData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data.slice(0, 8)} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis type="number" tick={{ fontSize: 10 }} />
                            <YAxis type="category" dataKey="model" width={60} tick={{ fontSize: 10 }} />
                            <Tooltip formatter={(value) => `$${value.toFixed(4)}`} />
                            <Bar dataKey="cost" fill="#6366f1" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}

/**
 * Recent Traces Table
 */
function RecentTracesTable({ traces }) {
    if (!traces || traces.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-sm p-6 text-center text-gray-500">
                No recent traces
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-700">📈 Recent Traces</h3>
                <span className="text-xs text-gray-400">{traces.length} traces</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-2 text-left text-xs text-gray-500">Time</th>
                            <th className="px-4 py-2 text-left text-xs text-gray-500">Model</th>
                            <th className="px-4 py-2 text-left text-xs text-gray-500">Provider</th>
                            <th className="px-4 py-2 text-right text-xs text-gray-500">Cost</th>
                            <th className="px-4 py-2 text-right text-xs text-gray-500">Latency</th>
                            <th className="px-4 py-2 text-center text-xs text-gray-500">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {traces.slice(0, 10).map((trace) => (
                            <tr key={trace.id} className="hover:bg-gray-50">
                                <td className="px-4 py-2 text-xs text-gray-600">
                                    {new Date(trace.start_time).toLocaleTimeString()}
                                </td>
                                <td className="px-4 py-2 text-sm font-medium text-gray-800">
                                    {trace.model}
                                </td>
                                <td className="px-4 py-2 text-xs text-gray-600">
                                    {trace.provider}
                                </td>
                                <td className="px-4 py-2 text-right text-xs text-gray-600">
                                    ${(trace.cost || 0).toFixed(4)}
                                </td>
                                <td className="px-4 py-2 text-right text-xs text-gray-600">
                                    {trace.latency_ms ? `${Math.round(trace.latency_ms)}ms` : '-'}
                                </td>
                                <td className="px-4 py-2 text-center">
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

/**
 * Status Badge Component
 */
function StatusBadge({ status }) {
    const colors = {
        success: 'bg-green-100 text-green-800',
        error: 'bg-red-100 text-red-800',
        pending: 'bg-yellow-100 text-yellow-800',
    };

    return (
        <span className={`px-2 py-0.5 text-xs rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
            {status || 'unknown'}
        </span>
    );
}

/**
 * Dashboard Loader Component
 */
function DashboardLoader() {
    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
                <div className="spinner mx-auto mb-4" />
                <p className="text-gray-500">Loading dashboard...</p>
            </div>
        </div>
    );
}

/**
 * Dashboard Error Component
 */
function DashboardError({ error, onRetry }) {
    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
                <div className="text-4xl mb-4">⚠️</div>
                <p className="text-red-600 mb-2">Failed to load dashboard</p>
                <p className="text-sm text-gray-500 mb-4">{error}</p>
                <button
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                    onClick={onRetry}
                >
                    Retry
                </button>
            </div>
        </div>
    );
}

export default Dashboard;