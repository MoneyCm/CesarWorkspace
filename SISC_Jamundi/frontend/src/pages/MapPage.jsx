import React, { useState } from 'react';
import MapComponent from '../components/Map/MapComponent';
import { Filter, Calendar, AlertTriangle } from 'lucide-react';

const MapPage = () => {
    return (
        <div className="flex h-full gap-4">
            {/* Sidebar de Filtros */}
            <div className="w-80 bg-white rounded-lg shadow-sm p-4 flex flex-col h-full overflow-y-auto">
                <div className="flex items-center space-x-2 mb-6 text-slate-700 border-b pb-4">
                    <Filter size={20} />
                    <h2 className="font-bold text-lg">Filtros</h2>
                </div>

                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center">
                            <AlertTriangle size={16} className="mr-2 text-primary" />
                            Tipo de Delito
                        </label>
                        <div className="space-y-2">
                            {['Homicidio', 'Hurto a Personas', 'Hurto a Comercio', 'Lesiones Personales', 'Violencia Intrafamiliar'].map((type) => (
                                <label key={type} className="flex items-center space-x-2 text-sm text-slate-600 cursor-pointer hover:text-slate-900">
                                    <input type="checkbox" className="rounded border-slate-300 text-primary focus:ring-primary" defaultChecked />
                                    <span>{type}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center">
                            <Calendar size={16} className="mr-2 text-primary" />
                            Rango de Fechas
                        </label>
                        <div className="space-y-3">
                            <input type="date" className="w-full border-slate-200 rounded-md text-sm focus:ring-primary focus:border-primary" />
                            <input type="date" className="w-full border-slate-200 rounded-md text-sm focus:ring-primary focus:border-primary" />
                        </div>
                    </div>

                    <button className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-primary/90 transition-colors text-sm font-medium shadow-sm">
                        Aplicar Filtros
                    </button>
                </div>
            </div>

            {/* Área del Mapa */}
            <div className="flex-1 bg-white rounded-lg shadow-sm p-1 border border-slate-200 relative z-0">
                <MapComponent />
            </div>
        </div>
    );
};

export default MapPage;
