import React, { useRef, useEffect } from 'react';
import { Timeline } from './components/Timeline';
import { TaskPanel } from './components/TaskPanel';
import { useTasks } from './hooks/useTasks';
import { DayCell } from './components/DayCell';
import { motion } from 'framer-motion';

function App() {
    const {
        tasks,
        selectedDate,
        setSelectedDate,
        addTask,
        toggleTaskStatus,
        removeTask,
        setDayTasks,
        getDayProgress
    } = useTasks();

    const scrollContainerRef = useRef < HTMLDivElement > (null);

    // Mock AI Suggestion
    const handleSuggestTasks = (dateIndex: number, goal: string) => {
        const mockSteps = [
            `Preparar herramientas para ${goal}`,
            `Fase inicial de ${goal}`,
            `Punto de control 1`,
            `Ejecución profunda`,
            `Revisión de calidad`,
            `Finalización de ${goal}`,
            `Limpieza y orden`
        ].map(title => ({ title }));

        // Fill up to 7 for visualization or keep as is
        setDayTasks(dateIndex, mockSteps.map((s, i) => ({ ...s, id: Date.now() + i, status: 'pending' })));
    };

    return (
        <div className="min-h-screen bg-dark-950 text-slate-100 flex flex-col font-inter selection:bg-accent-neon/30">
            {/* Top Navigation / Header */}
            <header className="h-20 flex items-center justify-between px-8 border-b border-white/5 glass z-50">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-neon to-accent-emerald flex items-center justify-center shadow-[0_0_15px_rgba(139,92,246,0.4)]">
                        <div className="w-5 h-5 grid grid-cols-2 gap-0.5">
                            <div className="bg-white rounded-full" />
                            <div className="bg-white/50 rounded-full" />
                            <div className="bg-white/70 rounded-full" />
                            <div className="bg-white rounded-full" />
                        </div>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold font-outfit tracking-tight">HyperGrid <span className="text-accent-neon">49</span></h1>
                        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">Neuro-Adaptive Productivity</p>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex flex-col items-end">
                        <span className="text-xs font-semibold text-slate-400">Progreso Total</span>
                        <div className="w-48 h-2 bg-slate-800 rounded-full mt-1 overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-accent-neon to-accent-emerald w-1/3" />
                        </div>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-slate-800 border border-white/10" />
                </div>
            </header>

            <main className="flex-grow flex overflow-hidden">
                {/* Main Content Area: Timeline */}
                <div className="flex-grow flex flex-col overflow-hidden">
                    <div className="p-8 pb-4">
                        <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Próximos 49 Días</h2>
                    </div>

                    <div
                        ref={scrollContainerRef}
                        className="flex-grow overflow-x-auto overflow-y-hidden px-8 pb-8 custom-scrollbar scroll-smooth"
                    >
                        <div className="flex gap-4 min-w-max h-full items-start">
                            {Array.from({ length: 49 }).map((_, i) => (
                                <DayCell
                                    key={i}
                                    index={i}
                                    tasks={tasks[i] || []}
                                    isSelected={selectedDate === i}
                                    onSelect={setSelectedDate}
                                    progress={getDayProgress(i)}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Efficiency / Stats Footer */}
                    <div className="h-32 px-8 py-6 border-t border-white/5 glass flex gap-12 items-center">
                        <div className="flex flex-col">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Eficiencia Hoy</span>
                            <span className="text-3xl font-bold font-outfit text-accent-emerald">84%</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Dopamina Generada</span>
                            <span className="text-3xl font-bold font-outfit text-accent-neon">+1,240</span>
                        </div>
                        <div className="flex-grow h-4 bg-slate-900 rounded-full overflow-hidden relative">
                            <div className="absolute inset-y-0 left-0 bg-accent-emerald w-[84%] shadow-[0_0_15px_rgba(16,185,129,0.4)]" />
                        </div>
                    </div>
                </div>

                {/* Side Panel: Task Details */}
                <aside className="w-[400px] flex-shrink-0">
                    <TaskPanel
                        dateIndex={selectedDate}
                        tasks={tasks[selectedDate] || []}
                        onAddTask={addTask}
                        onToggleTask={toggleTaskStatus}
                        onRemoveTask={removeTask}
                        onSuggestTasks={handleSuggestTasks}
                    />
                </aside>
            </main>
        </div>
    );
}

export default App;
