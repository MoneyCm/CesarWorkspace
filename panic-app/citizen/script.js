// App ciudadana — Botón de pánico con geolocalización, evidencia y cola offline
(function(){
  const API_BASE = localStorage.getItem('panic_api') || 'http://localhost:8000';
  const panicBtn = document.getElementById('panicBtn');
  const retryBtn = document.getElementById('retryBtn');
  const statusEl = document.getElementById('status');
  const evidenceInput = document.getElementById('evidence');
  const evidenceList = document.getElementById('evidenceList');
  const inbox = document.getElementById('inbox');

  let evidenceQueue = [];

  function setStatus(msg, color){ statusEl.textContent = 'Estado: ' + msg; if(color) statusEl.style.color = color; else statusEl.style.color=''; }
  function queueStore(key, data){ localStorage.setItem(key, JSON.stringify(data)); }
  function queueLoad(key){ try{ return JSON.parse(localStorage.getItem(key)||'[]'); }catch{ return []; } }

  // Agregar evidencia al envío
  evidenceInput.addEventListener('change', (e)=>{
    const files = Array.from(e.target.files||[]);
    evidenceQueue.push(...files);
    renderEvidence();
  });
  function renderEvidence(){ evidenceList.innerHTML = evidenceQueue.map(f=>`<li>• ${f.name} (${Math.round(f.size/1024)} KB)</li>`).join(''); }

  async function getPosition(){
    return new Promise((resolve,reject)=>{
      if(!('geolocation' in navigator)) return reject(new Error('Geolocalización no disponible'));
      navigator.geolocation.getCurrentPosition(p=>{
        resolve({ lat:p.coords.latitude, lon:p.coords.longitude, acc:p.coords.accuracy });
      }, err=>reject(err), { enableHighAccuracy:true, timeout:8000, maximumAge:1000 });
    });
  }

  function buildAlertPayload(pos){
    return { timestamp: new Date().toISOString(), lat: pos?.lat||null, lon: pos?.lon||null, accuracy: pos?.acc||null, kind: 'panic', note: '' };
  }

  async function sendAlertNow(alert){
    // Si hay evidencia, se intenta multipart; si no, JSON
    try{
      if(evidenceQueue.length){
        const fd = new FormData();
        fd.append('payload', new Blob([JSON.stringify(alert)], {type:'application/json'}));
        evidenceQueue.forEach((f,i)=>fd.append('media', f, f.name||`media_${i}`));
        const r = await fetch(API_BASE + '/api/alerts', { method:'POST', body:fd });
        if(!r.ok) throw new Error('HTTP '+r.status);
      } else {
        const r = await fetch(API_BASE + '/api/alerts', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(alert) });
        if(!r.ok) throw new Error('HTTP '+r.status);
      }
      setStatus('alerta enviada', 'var(--ok)');
      evidenceQueue = []; renderEvidence();
      navigator.vibrate?.(100);
      return true;
    }catch(err){
      console.warn('Fallo envío, se encola', err);
      return false;
    }
  }

  function enqueueAlert(alert){
    const q = queueLoad('pending_alerts');
    // Evidencias se omiten por seguridad en localStorage; se marcan como no subidas
    q.push({ alert, hasMedia: evidenceQueue.length>0 });
    queueStore('pending_alerts', q);
    setStatus('en cola offline ('+q.length+')', 'var(--warn)');
    evidenceQueue = []; renderEvidence();
  }

  async function handlePanic(){
    setStatus('obteniendo ubicación...');
    try{
      const pos = await getPosition().catch(()=>({}));
      const alert = buildAlertPayload(pos);
      const ok = await sendAlertNow(alert);
      if(!ok) enqueueAlert(alert);
    }catch(err){
      enqueueAlert(buildAlertPayload(null));
    }
  }

  async function retryQueue(){
    const q = queueLoad('pending_alerts');
    if(!q.length){ setStatus('no hay elementos en cola'); return; }
    const remain=[];
    for(const item of q){
      const ok = await sendAlertNow(item.alert);
      if(!ok) remain.push(item);
    }
    queueStore('pending_alerts', remain);
    setStatus(remain.length? ('pendientes: '+remain.length) : 'todos enviados', remain.length? 'var(--warn)' : 'var(--ok)');
  }

  function connectSSE(){
    // Intentar SSE a /api/events (no disponible en modo file://)
    try{
      const ev = new EventSource(API_BASE + '/api/events');
      ev.onmessage = (e)=>{
        const data = JSON.parse(e.data||'{}');
        inbox.textContent = `[Aviso] ${data.message||JSON.stringify(data)}`;
      };
      ev.onerror = ()=>{ inbox.textContent = 'Sin conexión de avisos (demo)'; };
    }catch{ inbox.textContent = 'Sin conexión de avisos (demo)'; }
  }

  panicBtn.addEventListener('click', handlePanic);
  retryBtn.addEventListener('click', retryQueue);
  connectSSE();
})();

