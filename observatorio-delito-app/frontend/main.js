const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
  ? 'http://localhost:8000' : 'http://localhost:8000';

const delitoSelect = document.getElementById('delitoSelect');
const inicioInput = document.getElementById('inicio');
const finInput = document.getElementById('fin');
const agrupacionSelect = document.getElementById('agrupacion');
const btnActualizar = document.getElementById('btnActualizar');
const fileInput = document.getElementById('fileInput');
const btnCargar = document.getElementById('btnCargar');
const btnCargarEjemplo = document.getElementById('btnCargarEjemplo');
const uploadStatus = document.getElementById('uploadStatus');

// Default dates: last 180 days
const today = new Date();
const past = new Date();
past.setDate(today.getDate() - 180);
const toISO = d => d.toISOString().slice(0,10);
inicioInput.value = toISO(past);
finInput.value = toISO(today);

// Chart
const ctx = document.getElementById('chart');
const chart = new Chart(ctx, {
  type: 'line',
  data: { labels: [], datasets: [{ label: 'Casos', data: [] }] },
  options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
});

// Map
const map = L.map('map').setView([3.262, -76.540], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap'
}).addTo(map);
let markersLayer = L.layerGroup().addTo(map);

async function cargarDelitos() {
  try {
    const r = await fetch(`${API_BASE}/delitos/disponibles`);
    const data = await r.json();
    delitoSelect.innerHTML = '<option value="">(Todos)</option>';
    data.delitos.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d;
      opt.textContent = d;
      delitoSelect.appendChild(opt);
    });
  } catch (error) {
    console.error('Error cargando delitos:', error);
  }
}

async function actualizar() {
  try {
    const params = new URLSearchParams({
      inicio: inicioInput.value,
      fin: finInput.value,
      agrupacion: agrupacionSelect.value
    });
    if (delitoSelect.value) params.append('delito', delitoSelect.value);

    // Serie
    const rs = await fetch(`${API_BASE}/estadisticas?` + params.toString());
    const serie = await rs.json();
    chart.data.labels = serie.serie.map(x => x.periodo);
    chart.data.datasets[0].data = serie.serie.map(x => x.total);
    chart.update();

    // Geodatos
    const rg = await fetch(`${API_BASE}/geodatos?` + params.toString());
    const geos = await rg.json();
    markersLayer.clearLayers();
    geos.items.forEach(it => {
      if (it.lat && it.lon) {
        const m = L.marker([it.lat, it.lon]).bindPopup(`<b>${it.delito}</b><br>${it.barrio || ''}<br>${it.fecha}`);
        markersLayer.addLayer(m);
      }
    });
  } catch (error) {
    console.error('Error actualizando datos:', error);
  }
}

async function cargarArchivo() {
  const file = fileInput.files[0];
  if (!file) {
    mostrarStatus('Por favor selecciona un archivo', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    mostrarStatus('Cargando archivo...', '');
    const response = await fetch(`${API_BASE}/cargar-excel`, {
      method: 'POST',
      body: formData
    });

    const result = await response.json();
    
    if (response.ok) {
      mostrarStatus(`✅ ${result.message}`, 'success');
      await cargarDelitos();
      await actualizar();
    } else {
      mostrarStatus(`❌ Error: ${result.detail}`, 'error');
    }
  } catch (error) {
    mostrarStatus(`❌ Error de conexión: ${error.message}`, 'error');
  }
}

async function cargarDatosEjemplo() {
  try {
    mostrarStatus('Cargando datos de ejemplo...', '');
    const response = await fetch(`${API_BASE}/cargar-datos-ejemplo`, {
      method: 'POST'
    });

    const result = await response.json();
    
    if (response.ok) {
      mostrarStatus(`✅ ${result.message}`, 'success');
      await cargarDelitos();
      await actualizar();
    } else {
      mostrarStatus(`❌ Error: ${result.detail}`, 'error');
    }
  } catch (error) {
    mostrarStatus(`❌ Error de conexión: ${error.message}`, 'error');
  }
}

function mostrarStatus(mensaje, tipo) {
  uploadStatus.textContent = mensaje;
  uploadStatus.className = tipo;
}

// Event listeners
btnActualizar.addEventListener('click', actualizar);
btnCargar.addEventListener('click', cargarArchivo);
btnCargarEjemplo.addEventListener('click', cargarDatosEjemplo);

(async () => {
  await cargarDelitos();
  await actualizar();
})();