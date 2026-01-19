import React from 'react';
import { motion } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility for Tailwind class merging
 */
function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface DayCellProps {
    index: number;
    tasks: any[];
    isSelected: boolean;
    onSelect: (index: number) => void;
    progress: number;
}

export const DayCell = ({ index, tasks = [], isSelected, onSelect, progress }: DayCellProps) => {
    // 7x7 Grid (49 cells)
    const gridCells = Array.from({ length: 49 });

    return (
        <motion.div
            onClick={() => onSelect(index)}
            whileHover={{ scale: 1.02 }}
            className={cn(
                "min-w-[140px] h-[180px] p-3 rounded-xl cursor-pointer transition-all duration-300",
                "flex flex-col gap-2 relative overflow-hidden",
                isSelected
                    ? "glass-card ring-2 ring-accent-neon shadow-[0_0_20px_rgba(139,92,246,0.3)]"
                    : "glass hover:bg-white/5"
            )}
        >
            <div className="flex justify-between items-center z-10">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                    Día {index + 1}
                </span>
                {progress > 0 && (
                    <span className={cn(
                        "text-[10px] px-1.5 py-0.5 rounded bg-slate-800/50 font-bold",
                        progress === 100 ? "text-accent-emerald" : "text-accent-amber"
                    )}>
                        {progress}%
                    </span>
                )}
            </div>

            {/* 7x7 Fractal Grid */}
            <div className="grid grid-cols-7 grid-rows-7 gap-[2px] flex-grow bg-slate-900/50 p-1 rounded-md border border-white/5">
                {gridCells.map((_, i) => {
                    const task = tasks[i];
                    return (
                        <div
                            key={i}
                            className={cn(
                                "w-full pt-[100%] rounded-[1px] transition-colors duration-500",
                                !task && "bg-slate-800/30",
                                task?.status === 'pending' && "bg-accent-amber shadow-[0_0_5px_rgba(245,158,11,0.5)]",
                                task?.status === 'completed' && "bg-accent-emerald shadow-[0_0_5px_rgba(16,185,129,0.5)]"
                            )}
                        />
                    );
                })}
            </div>

            {/* Status Indicators (Google Calendar Mock) */}
            <div className="flex gap-1 h-1">
                {index % 5 === 0 && <div className="w-1 h-1 rounded-full bg-blue-400" title="Evento de Google" />}
            </div>

            {/* Background radial gradient for focus */}
            {isSelected && (
                <div className="absolute inset-0 bg-radial-gradient from-accent-neon/10 to-transparent pointer-events-none" />
            )}
        </motion.div>
    );
};
