import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

const KPICard = ({ kpi }) => {
    const { label, value, change, trend, unit, description } = kpi;

    const getTrendIcon = () => {
        switch (trend) {
            case 'up':
                return <TrendingUp size={18} className="text-green-400" />;
            case 'down':
                return <TrendingDown size={18} className="text-red-400" />;
            default:
                return <Minus size={18} className="text-gray-400" />;
        }
    };

    const getTrendColor = () => {
        switch (trend) {
            case 'up':
                return 'text-green-400 bg-green-400/10';
            case 'down':
                return 'text-red-400 bg-red-400/10';
            default:
                return 'text-gray-400 bg-gray-400/10';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm hover:bg-white/10 transition-all"
        >
            <div className="flex items-start justify-between mb-3">
                <p className="text-sm text-gray-400 font-medium">{label}</p>
                {trend && getTrendIcon()}
            </div>

            <div className="flex items-baseline gap-2 mb-2">
                <h3 className="text-3xl font-bold text-white">
                    {value}
                </h3>
                {unit && (
                    <span className="text-lg text-gray-400">{unit}</span>
                )}
            </div>

            {change !== null && change !== undefined && (
                <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-sm font-medium ${getTrendColor()}`}>
                    {change > 0 ? '+' : ''}{change.toFixed(1)}%
                </div>
            )}

            {description && (
                <p className="text-xs text-gray-500 mt-3">{description}</p>
            )}
        </motion.div>
    );
};

export default KPICard;
