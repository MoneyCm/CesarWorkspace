import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Trash2, Plus, Sparkles, Calendar, Bell } from 'lucide-react';

interface TaskPanelProps {
    dateIndex: number;
    tasks: any[];
    onAddTask: (dateIndex: number, task: any) => void;
    onToggleTask: (dateIndex: number, taskId: number) => void;
    onRemoveTask: (dateIndex: number, taskId: number) => void;
    onSuggestTasks: (dateIndex: number, goal: string) => void;
}

export const TaskPanel = ({ dateIndex, tasks = [], onAddTask, onToggleTask, onRemoveTask, onSuggestTasks }: TaskPanelProps) => {
    const [newGoal, setNewGoal] = useState('');
    const [manualTask, setManualTask] = useState('');

    const handleAddManual = (e: React.FormEvent) => {
        e.preventDefault();
        if (!manualTask.trim()) return;
        onAddTask(dateIndex, { title: manualTask });
        setManualTask('');
    };

    return (
        <div className="flex flex-col h-full glass-card rounded-2xl p-6 border-l border-white/10">
            <div className="mb-8">
                <h2 className="text-3xl font-bold font-outfit text-white mb-1">Día {dateIndex + 1}</h2>
                <p className="text-slate-400 text-sm">Gestiona tus micro-pasos y eventos</p>
            </div>

            {/* AI Planner Section */}
            <div className="mb-8 p-4 rounded-xl bg-accent-neon/10 border border-accent-neon/20">
                <div className="flex items-center gap-2 mb-3 text-accent-neon">
                    <Sparkles size={18} />
                    <span className="font-semibold text-sm uppercase tracking-wider">Planificador con IA</span>
                </div>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newGoal}
                        onChange={(e) => setNewGoal(e.target.value)}
                        placeholder="Ej: Limpiar la casa..."
                        className="flex-grow bg-slate-900/50 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-neon"
                    />
                    <button
                        onClick={() => onSuggestTasks(dateIndex, newGoal)}
                        className="bg-accent-neon hover:bg-accent-neon/80 text-white p-2 rounded-lg transition-colors"
                    >
                        <Plus size={20} />
                    </button>
                </div>
            </div>

            {/* Tasks List */}
            <div className="flex-grow overflow-y-auto pr-2 space-y-3 mb-6">
                <AnimatePresence mode="popLayout">
                    {tasks.map((task, idx) => (
                        <motion.div
                            key={task.id || idx}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 group hover:bg-white/10 transition-colors"
                        >
                            <button
                                onClick={() => onToggleTask(dateIndex, task.id)}
                                className={task.status === 'completed' ? 'text-accent-emerald' : 'text-slate-500'}
                            >
                                {task.status === 'completed' ? <CheckCircle2 size={20} /> : <Circle size={20} />}
                            </button>
                            <span className={`flex-grow text-sm ${task.status === 'completed' ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                                {task.title}
                            </span>
                            <button
                                onClick={() => onRemoveTask(dateIndex, task.id)}
                                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity"
                            >
                                <Trash2 size={16} />
                            </button>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Quick Add and Actions */}
            <div className="mt-auto pt-6 border-t border-white/10 space-y-4">
                <form onSubmit={handleAddManual} className="flex gap-2">
                    <input
                        type="text"
                        value={manualTask}
                        onChange={(e) => setManualTask(e.target.value)}
                        placeholder="Añadir paso manual..."
                        className="flex-grow bg-slate-900/50 border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-emerald"
                    />
                    <button type="submit" className="bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg transition-colors">
                        <Plus size={20} />
                    </button>
                </form>

                <div className="flex gap-3">
                    <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-600/30 hover:bg-blue-600/30 transition-colors text-sm font-semibold">
                        <Calendar size={16} /> Google Cal
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-accent-amber/10 text-accent-amber border border-accent-amber/20 hover:bg-accent-amber/20 transition-colors text-sm font-semibold">
                        <Bell size={16} /> Alerta
                    </button>
                </div>
            </div>
        </div>
    );
};
