import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: string | number;
    change: number;
    trend: 'up' | 'down';
    icon: React.ReactNode;
}

const StatsCard = ({ title, value, change, trend, icon }: StatsCardProps) => {
    return (
        <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-50 text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
                    {icon}
                </div>
                <div className={`flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${trend === 'up'
                        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/10 dark:text-emerald-400'
                        : 'bg-red-50 text-red-700 dark:bg-red-900/10 dark:text-red-400'
                    }`}>
                    {trend === 'up' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {change}%
                </div>
            </div>
            <div className="mt-4">
                <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400">{title}</h3>
                <p className="mt-1 text-2xl font-bold text-zinc-900 dark:text-zinc-50">{value}</p>
            </div>
        </div>
    );
};

export default StatsCard;
