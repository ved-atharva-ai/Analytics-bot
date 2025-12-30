import React, { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

const DataTableComponent = ({ tableData }) => {
    const { columns, rows, title } = tableData;
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

    if (!rows || rows.length === 0) {
        return (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <p className="text-gray-400 text-center">No data available</p>
            </div>
        );
    }

    const handleSort = (column) => {
        let direction = 'asc';
        if (sortConfig.key === column && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key: column, direction });
    };

    const sortedRows = [...rows].sort((a, b) => {
        if (!sortConfig.key) return 0;

        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    return (
        <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-sm">
            {title && (
                <div className="px-6 py-4 border-b border-white/10">
                    <h3 className="text-lg font-semibold text-gray-200">{title}</h3>
                </div>
            )}

            <div className="overflow-x-auto max-h-96">
                <table className="w-full">
                    <thead className="bg-white/5 sticky top-0">
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column}
                                    onClick={() => handleSort(column)}
                                    className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-white/10 transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        {column}
                                        {sortConfig.key === column && (
                                            sortConfig.direction === 'asc'
                                                ? <ChevronUp size={14} />
                                                : <ChevronDown size={14} />
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {sortedRows.map((row, idx) => (
                            <tr key={idx} className="hover:bg-white/5 transition-colors">
                                {columns.map((column) => (
                                    <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                        {row[column] !== null && row[column] !== undefined ? String(row[column]) : '-'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DataTableComponent;
