import React from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, ScatterChart, Scatter, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

const ChartRenderer = ({ chartConfig }) => {
    if (!chartConfig || !chartConfig.data || chartConfig.data.length === 0) {
        return (
            <div className="p-8 text-center text-gray-400 bg-white/5 rounded-xl border border-white/10">
                <p>No data available for visualization</p>
            </div>
        );
    }

    const { chart_type, data, x_key, y_key, title, x_label, y_label } = chartConfig;

    const renderChart = () => {
        switch (chart_type) {
            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                            <XAxis
                                dataKey={x_key}
                                stroke="#9ca3af"
                                label={{ value: x_label || x_key, position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                            />
                            <YAxis
                                stroke="#9ca3af"
                                label={{ value: y_label || y_key, angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                            />
                            <Legend wrapperStyle={{ color: '#9ca3af' }} />
                            <Bar dataKey={y_key} fill="#3b82f6" />
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                            <XAxis
                                dataKey={x_key}
                                stroke="#9ca3af"
                                label={{ value: x_label || x_key, position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                            />
                            <YAxis
                                stroke="#9ca3af"
                                label={{ value: y_label || y_key, angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                            />
                            <Legend wrapperStyle={{ color: '#9ca3af' }} />
                            <Line type="monotone" dataKey={y_key} stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                            <Pie
                                data={data}
                                dataKey={y_key || 'value'}
                                nameKey={x_key}
                                cx="50%"
                                cy="50%"
                                outerRadius={120}
                                label={(entry) => `${entry[x_key]}: ${entry[y_key || 'value']}`}
                                labelLine={true}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                            />
                            <Legend wrapperStyle={{ color: '#9ca3af' }} />
                        </PieChart>
                    </ResponsiveContainer>
                );

            case 'scatter':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <ScatterChart>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                            <XAxis
                                dataKey={x_key}
                                stroke="#9ca3af"
                                label={{ value: x_label || x_key, position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                            />
                            <YAxis
                                dataKey={y_key}
                                stroke="#9ca3af"
                                label={{ value: y_label || y_key, angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                            />
                            <Scatter data={data} fill="#3b82f6" />
                        </ScatterChart>
                    </ResponsiveContainer>
                );

            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <AreaChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                            <XAxis
                                dataKey={x_key}
                                stroke="#9ca3af"
                                label={{ value: x_label || x_key, position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                            />
                            <YAxis
                                stroke="#9ca3af"
                                label={{ value: y_label || y_key, angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    color: '#fff'
                                }}
                            />
                            <Legend wrapperStyle={{ color: '#9ca3af' }} />
                            <Area type="monotone" dataKey={y_key} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                        </AreaChart>
                    </ResponsiveContainer>
                );

            default:
                return <p className="text-gray-400">Unsupported chart type: {chart_type}</p>;
        }
    };

    return (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
            {title && (
                <h3 className="text-lg font-semibold text-gray-200 mb-4">{title}</h3>
            )}
            {renderChart()}
        </div>
    );
};

export default ChartRenderer;
