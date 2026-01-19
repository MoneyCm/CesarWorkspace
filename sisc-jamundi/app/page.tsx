'use client';

import React from 'react';
import Sidebar from './components/Sidebar';
import StatsCard from './components/StatsCard';
import dynamic from 'next/dynamic';
const SecurityMap = dynamic(() => import('./components/SecurityMap'), { ssr: false });
import { Users, ShieldCheck, AlertTriangle, Calendar, MapPin } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <Sidebar />

      <main className="ml-64 flex-1 p-8">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">Panel de Control SISC</h1>
            <p className="text-zinc-500 dark:text-zinc-400">Sistema Integrado de Seguridad y Convivencia - Jamundí</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm font-medium text-zinc-600 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-400">
              <Calendar size={16} />
              21 de mayo, 2024
            </span>
          </div>
        </header>

        <section className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Incidentes Hoy"
            value="12"
            change={8}
            trend="down"
            icon={<AlertTriangle size={24} />}
          />
          <StatsCard
            title="Patrullas Activas"
            value="34"
            change={5}
            trend="up"
            icon={<ShieldCheck size={24} />}
          />
          <StatsCard
            title="Líderes Comunitarios"
            value="256"
            change={2}
            trend="up"
            icon={<Users size={24} />}
          />
          <StatsCard
            title="Zonas de Atención"
            value="5"
            change={12}
            trend="down"
            icon={<MapPin size={24} />}
          />
        </section>

        <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-bold text-zinc-900 dark:text-zinc-50">Mapa de Eventos en Tiempo Real</h2>
              <button className="text-sm font-medium text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 dark:hover:text-emerald-300">
                Ver Mapa Completo
              </button>
            </div>
            <div className="h-[450px]">
              <SecurityMap />
            </div>
          </div>

          <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
            <h2 className="mb-6 text-lg font-bold text-zinc-900 dark:text-zinc-50">Alertas Recientes</h2>
            <div className="space-y-4">
              {[
                { time: '10:45 AM', type: 'Hurto', location: 'Barrio El Rosario', severity: 'Alta' },
                { time: '09:30 AM', type: 'Riña', location: 'Parque Principal', severity: 'Media' },
                { time: '08:15 AM', type: 'Sospechoso', location: 'Sector La Pradera', severity: 'Baja' },
              ].map((alert, i) => (
                <div key={i} className="flex items-start gap-3 rounded-lg border border-zinc-100 p-3 dark:border-zinc-900">
                  <div className={`mt-1 h-2 w-2 rounded-full ${alert.severity === 'Alta' ? 'bg-red-500' : alert.severity === 'Media' ? 'bg-amber-500' : 'bg-blue-500'
                    }`} />
                  <div>
                    <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">{alert.type} - {alert.location}</h4>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">{alert.time} • Prioridad {alert.severity}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function MapPinIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}
