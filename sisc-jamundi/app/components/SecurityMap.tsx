'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import with SSR disabled for Leaflet components
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });

// Helper component to fix the "gray area" / "broken tiles" issue in Leaflet + Next.js
const InvalidateSizeHandler = () => {
    const map = (require('react-leaflet') as any).useMap();
    useEffect(() => {
        setTimeout(() => {
            map.invalidateSize();
        }, 500);
    }, [map]);
    return null;
};

const SecurityMap = () => {
    const [L, setL] = useState<any>(null);
    const [jamundiCenter] = useState<[number, number]>([3.2625, -76.5367]);
    const [useMapHook, setUseMapHook] = useState<any>(null);

    useEffect(() => {
        // Import leaflet only on the client side
        import('leaflet').then((leaflet) => {
            setL(leaflet);
            // Fix for default markers
            delete (leaflet.Icon.Default.prototype as any)._getIconUrl;
            leaflet.Icon.Default.mergeOptions({
                iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
                iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
                shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
            });
        });

        import('react-leaflet').then((mod) => {
            setUseMapHook(() => mod.useMap);
        });
    }, []);

    if (!L || !useMapHook) {
        return (
            <div className="flex h-full w-full items-center justify-center bg-zinc-100 dark:bg-zinc-900">
                <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Cargando Mapa...</p>
            </div>
        );
    }

    // Define the inner component here to have access to useMapHook
    const InvalidateSizeInner = () => {
        const map = useMapHook();
        useEffect(() => {
            if (map) {
                setTimeout(() => map.invalidateSize(), 200);
            }
        }, [map]);
        return null;
    };

    const mockEvents = [
        { id: 1, type: 'Hurto', pos: [3.265, -76.540], severity: 'Alta' },
        { id: 2, type: 'Riña', pos: [3.260, -76.530], severity: 'Media' },
        { id: 3, type: 'Patrulla', pos: [3.262, -76.536], severity: 'Baja' },
    ];

    return (
        <div className="h-full w-full overflow-hidden rounded-lg shadow-inner">
            <MapContainer
                center={jamundiCenter}
                zoom={14}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <InvalidateSizeInner />
                {mockEvents.map(event => (
                    <Marker key={event.id} position={event.pos as [number, number]}>
                        <Popup>
                            <div className="p-1">
                                <h3 className="font-bold">{event.type}</h3>
                                <p className="text-xs">Prioridad: {event.severity}</p>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
};

export default SecurityMap;
