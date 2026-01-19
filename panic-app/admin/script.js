// Panel central — mapa y listado. Soporta modo demo (sin backend).
(function(){
  const API_BASE = localStorage.getItem('panic_api') || 'http://localhost:8000';
  const tblBody = document.querySelector('#tbl tbody');
  const refreshBtn = document.getElementById('refreshBtn');
  const broadcastMsg = document.getElementById('broadcastMsg');
  const sendBroadcast = document.getElementById('sendBroadcast');

  // Mapa Leaflet
  const map = L.map('map').setView([4.65,-74.1], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:19, attribution:'© OSM'}).addTo(map);
  const markers = L.layerGroup().addTo(map);

  async function fetchAlerts(){
    try{
      const r = await fetch(API_BASE + '/api/alerts');
      if(!r.ok) throw new Error('HTTP '+r.status);
      const data = await r.json();
      render(data);
    }catch{
      // modo demo: datos de ejemplo
      const data = [
        {timestamp:new Date().toISOString(), lat:4.65, lon:-74.1, kind:'panic'},
        {timestamp:new Date(Date.now()-600000).toISOString(), lat:4.68, lon:-74.08, kind:'panic'}
      ];
      render(data);
    }
  }

  function render(list){
    markers.clearLayers();
    tblBody.innerHTML = list.map(a=>`<tr><td>${new Date(a.timestamp).toLocaleString()}</td><td>${a.lat?.toFixed?.(5)||''}</td><td>${a.lon?.toFixed?.(5)||''}</td><td>${a.kind}</td></tr>`).join('');
    list.forEach(a=>{ if(a.lat && a.lon){ L.circleMarker([a.lat,a.lon], {radius:8,color:'#ff4d6d'}).addTo(markers); } });
    const first = list.find(a=>a.lat && a.lon); if(first) map.setView([first.lat, first.lon], 13);
  }

  refreshBtn.addEventListener('click', fetchAlerts);
  sendBroadcast.addEventListener('click', async()=>{
    const msg = broadcastMsg.value.trim(); if(!msg) return;
    try{ await fetch(API_BASE + '/api/broadcasts', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg})});
    }catch{ /* demo: sin backend */ }
    broadcastMsg.value='';
  });

  fetchAlerts();
})();

