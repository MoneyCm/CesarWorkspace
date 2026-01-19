import React, { useState, useEffect } from 'react';
import { Search, Plus, Edit2, Trash2, Save, X, ChevronLeft, ChevronRight, Upload } from 'lucide-react';
import * as XLSX from 'xlsx';
import AIAnalysisModal from '../components/AIAnalysisModal';

const API_URL = 'http://localhost:8000/analitica/estadisticas/resumen';
const INGESTA_URL = 'http://localhost:8000/ingesta/upload';

const DataPage = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isAIModalOpen, setIsAIModalOpen] = useState(false);
    const [pendingImportData, setPendingImportData] = useState([]);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({
        fecha: '',
        tipo: '',
        barrio: '',
        descripcion: '',
        estado: 'Abierto'
    });

    // Datos iniciales vacíos, se llenarán desde el backend
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch data on mount
    useEffect(() => {
        fetchIncidents();
    }, []);

    const fetchIncidents = async () => {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error('Error al cargar datos');
            const result = await response.json();
            setData(result);
            setError(null);
        } catch (err) {
            console.error(err);
            setError('No se pudo conectar con el servidor. Asegúrate de que el backend esté corriendo.');
        } finally {
            setLoading(false);
        }
    };

    const filteredData = data.filter(item =>
        item.tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.barrio.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.descripcion.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Nota: Los endpoints de creación/edición individual deben implementarse en FastAPI si se requieren
        alert('Funcionalidad de guardado individual en desarrollo. Use Importar Excel para carga masiva.');
    };

    const handleEdit = (item) => {
        setFormData({
            fecha: item.fecha,
            tipo: item.tipo,
            barrio: item.barrio,
            descripcion: item.descripcion,
            estado: item.estado
        });
        setEditingId(item.id);
        setIsModalOpen(true);
    };

    const handleDelete = async (id) => {
        // Implementación pendiente en backend FastAPI
        alert('Funcionalidad de eliminación en desarrollo.');
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingId(null);
        setFormData({ fecha: '', tipo: '', barrio: '', descripcion: '', estado: 'Abierto' });
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formDataFile = new FormData();
        formDataFile.append('file', file);

        try {
            setLoading(true);
            const response = await fetch(INGESTA_URL, {
                method: 'POST',
                body: formDataFile
            });

            if (!response.ok) throw new Error('Error en la carga');
            const result = await response.json();
            alert(result.message);
            fetchIncidents();
        } catch (err) {
            alert('Error al cargar: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmImport = async (analyzedData) => {
        // En este MVP la ingesta se hace directamente por archivo
        setIsAIModalOpen(false);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800">Gestión de Datos</h2>
                    <p className="text-slate-500">Administración de registros delictivos</p>
                </div>
                <div className="flex space-x-2">
                    <label className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors cursor-pointer">
                        <Upload size={18} />
                        <span>Importar Excel</span>
                        <input type="file" accept=".xlsx, .xls" onChange={handleFileUpload} className="hidden" />
                    </label>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="flex items-center space-x-2 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
                    >
                        <Plus size={18} />
                        <span>Nuevo Registro</span>
                    </button>
                </div>
            </div>

            {/* Barra de Búsqueda */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
                <input
                    type="text"
                    placeholder="Buscar por tipo, barrio o descripción..."
                    className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            {/* Mensaje de Error */}
            {error && (
                <div className="p-4 bg-red-50 text-red-700 rounded-md border border-red-200">
                    {error}
                </div>
            )}

            {/* Tabla */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-50 border-b border-slate-200">
                                <th className="p-4 font-semibold text-slate-600">Fecha</th>
                                <th className="p-4 font-semibold text-slate-600">Tipo de Delito</th>
                                <th className="p-4 font-semibold text-slate-600">Barrio</th>
                                <th className="p-4 font-semibold text-slate-600">Descripción</th>
                                <th className="p-4 font-semibold text-slate-600">Estado</th>
                                <th className="p-4 font-semibold text-slate-600 text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="p-8 text-center text-slate-500">
                                        Cargando datos...
                                    </td>
                                </tr>
                            ) : filteredData.length > 0 ? (
                                filteredData.map((item) => (
                                    <tr key={item.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                                        <td className="p-4 text-slate-700">{item.fecha}</td>
                                        <td className="p-4">
                                            <span className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs font-medium">
                                                {item.tipo}
                                            </span>
                                        </td>
                                        <td className="p-4 text-slate-700">{item.barrio}</td>
                                        <td className="p-4 text-slate-600 text-sm max-w-xs truncate">{item.descripcion}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${item.estado === 'Cerrado' ? 'bg-green-100 text-green-700' :
                                                item.estado === 'En Investigación' ? 'bg-orange-100 text-orange-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>
                                                {item.estado}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right space-x-2">
                                            <button onClick={() => handleEdit(item)} className="text-slate-400 hover:text-primary transition-colors">
                                                <Edit2 size={18} />
                                            </button>
                                            <button onClick={() => handleDelete(item.id)} className="text-slate-400 hover:text-red-600 transition-colors">
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="p-8 text-center text-slate-500">
                                        No se encontraron registros que coincidan con la búsqueda.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Paginación Simple */}
                <div className="p-4 border-t border-slate-200 flex justify-between items-center text-sm text-slate-500">
                    <span>Mostrando {filteredData.length} registros</span>
                    <div className="flex space-x-2">
                        <button className="p-1 border rounded hover:bg-slate-50 disabled:opacity-50" disabled><ChevronLeft size={16} /></button>
                        <button className="p-1 border rounded hover:bg-slate-50 disabled:opacity-50" disabled><ChevronRight size={16} /></button>
                    </div>
                </div>
            </div>

            {/* Modal de Formulario */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
                        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                            <h3 className="font-bold text-lg text-slate-800">{editingId ? 'Editar Registro' : 'Nuevo Registro'}</h3>
                            <button onClick={handleCloseModal} className="text-slate-400 hover:text-slate-600">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Fecha</label>
                                <input
                                    type="date"
                                    name="fecha"
                                    required
                                    value={formData.fecha}
                                    onChange={handleInputChange}
                                    className="w-full border-slate-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Tipo de Delito</label>
                                <select
                                    name="tipo"
                                    required
                                    value={formData.tipo}
                                    onChange={handleInputChange}
                                    className="w-full border-slate-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
                                >
                                    <option value="">Seleccionar...</option>
                                    <option value="Homicidio">Homicidio</option>
                                    <option value="Hurto a Personas">Hurto a Personas</option>
                                    <option value="Hurto a Comercio">Hurto a Comercio</option>
                                    <option value="Lesiones Personales">Lesiones Personales</option>
                                    <option value="Violencia Intrafamiliar">Violencia Intrafamiliar</option>
                                    <option value="Riña">Riña</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Barrio</label>
                                <input
                                    type="text"
                                    name="barrio"
                                    required
                                    value={formData.barrio}
                                    onChange={handleInputChange}
                                    className="w-full border-slate-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
                                <textarea
                                    name="descripcion"
                                    rows="3"
                                    value={formData.descripcion}
                                    onChange={handleInputChange}
                                    className="w-full border-slate-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
                                ></textarea>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Estado</label>
                                <select
                                    name="estado"
                                    value={formData.estado}
                                    onChange={handleInputChange}
                                    className="w-full border-slate-300 rounded-md shadow-sm focus:ring-primary focus:border-primary"
                                >
                                    <option value="Abierto">Abierto</option>
                                    <option value="En Investigación">En Investigación</option>
                                    <option value="Cerrado">Cerrado</option>
                                </select>
                            </div>
                            <div className="pt-4 flex justify-end space-x-3">
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="px-4 py-2 border border-slate-300 rounded-md text-slate-700 hover:bg-slate-50"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 flex items-center"
                                >
                                    <Save size={16} className="mr-2" />
                                    Guardar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Análisis IA */}
            <AIAnalysisModal
                isOpen={isAIModalOpen}
                onClose={() => setIsAIModalOpen(false)}
                data={pendingImportData}
                onConfirm={handleConfirmImport}
            />
        </div>
    );
};

export default DataPage;
