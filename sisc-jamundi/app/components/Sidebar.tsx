import React from 'react';
import { LayoutDashboard, Map as MapIcon, ShieldAlert, BarChart3, Settings, LogOut } from 'lucide-react';

const Sidebar = () => {
    const menuItems = [
        { icon: <LayoutDashboard size={20} />, label: 'Dashboard', active: true },
        { icon: <MapIcon size={20} />, label: 'Mapa de Seguridad' },
        { icon: <ShieldAlert size={20} />, label: 'Alertas Tempranas' },
        { icon: <BarChart3 size={20} />, label: 'Estadísticas' },
        { icon: <Settings size={20} />, label: 'Configuración' },
    ];

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 border-r border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="mb-10 flex items-center gap-3 px-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white">
                    <ShieldAlert size={20} />
                </div>
                <span className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">SISC Jamundí</span>
            </div>

            <nav className="flex h-[calc(100%-8rem)] flex-col justify-between">
                <ul className="space-y-2">
                    {menuItems.map((item, index) => (
                        <li key={index}>
                            <a
                                href="#"
                                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${item.active
                                        ? 'bg-zinc-100 text-zinc-900 dark:bg-zinc-900 dark:text-zinc-50'
                                        : 'text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900/50 dark:hover:text-zinc-50'
                                    }`}
                            >
                                {item.icon}
                                {item.label}
                            </a>
                        </li>
                    ))}
                </ul>

                <button className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition-all hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/10">
                    <LogOut size={20} />
                    Cerrar Sesión
                </button>
            </nav>
        </aside>
    );
};

export default Sidebar;
