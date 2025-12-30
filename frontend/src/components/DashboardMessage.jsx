import React from 'react';
import ChartRenderer from './ChartRenderer';
import KPICard from './KPICard';
import DataTableComponent from './DataTableComponent';
import { motion } from 'framer-motion';

const DashboardMessage = ({ dashboardData }) => {
    const { text, charts, kpis, tables } = dashboardData;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6 w-full"
        >
            {/* Text explanation - REMOVED */}

            {/* KPI Cards Grid */}
            {kpis && kpis.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {kpis.map((kpi, idx) => (
                        <KPICard key={idx} kpi={kpi} />
                    ))}
                </div>
            )}

            {/* Charts */}
            {charts && charts.length > 0 && (
                <div className="space-y-6">
                    {charts.map((chart, idx) => (
                        <ChartRenderer key={idx} chartConfig={chart} />
                    ))}
                </div>
            )}

            {/* Tables */}
            {tables && tables.length > 0 && (
                <div className="space-y-6">
                    {tables.map((table, idx) => (
                        <DataTableComponent key={idx} tableData={table} />
                    ))}
                </div>
            )}
        </motion.div>
    );
};

export default DashboardMessage;
