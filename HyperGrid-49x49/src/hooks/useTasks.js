import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'hypergrid_tasks';

export const useTasks = () => {
    const [tasks, setTasks] = useState(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        return saved ? JSON.parse(saved) : {};
    });

    const [selectedDate, setSelectedDate] = useState(0); // 0 to 48

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    }, [tasks]);

    const addTask = (dateIndex, task) => {
        setTasks(prev => {
            const dateTasks = prev[dateIndex] || [];
            return {
                ...prev,
                [dateIndex]: [...dateTasks, { ...task, id: Date.now(), status: 'pending' }]
            };
        });
    };

    const toggleTaskStatus = (dateIndex, taskId) => {
        setTasks(prev => {
            const dateTasks = prev[dateIndex] || [];
            return {
                ...prev,
                [dateIndex]: dateTasks.map(t =>
                    t.id === taskId
                        ? { ...t, status: t.status === 'completed' ? 'pending' : 'completed' }
                        : t
                )
            };
        });
    };

    const removeTask = (dateIndex, taskId) => {
        setTasks(prev => ({
            ...prev,
            [dateIndex]: (prev[dateIndex] || []).filter(t => t.id !== taskId)
        }));
    };

    const setDayTasks = (dateIndex, newTasks) => {
        setTasks(prev => ({
            ...prev,
            [dateIndex]: newTasks
        }));
    };

    const getDayProgress = (dateIndex) => {
        const dateTasks = tasks[dateIndex] || [];
        if (dateTasks.length === 0) return 0;
        const completed = dateTasks.filter(t => t.status === 'completed').length;
        return Math.round((completed / Math.max(dateTasks.length, 1)) * 100);
    };

    return {
        tasks,
        selectedDate,
        setSelectedDate,
        addTask,
        toggleTaskStatus,
        removeTask,
        setDayTasks,
        getDayProgress
    };
};
