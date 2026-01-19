// Pinball sencillo en canvas (sin librerías)
(function(){
  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  // Escalado por DPR para nitidez
  let CSS_W = canvas.width, CSS_H = canvas.height;
  let dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
  function setupDPR(){
    CSS_W = canvas.width; CSS_H = canvas.height;
    canvas.style.width = CSS_W + 'px';
    canvas.style.height = CSS_H + 'px';
    canvas.width = Math.round(CSS_W * dpr);
    canvas.height = Math.round(CSS_H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  setupDPR();
  window.addEventListener('resize', ()=>{ dpr = Math.max(1, Math.min(2, window.devicePixelRatio||1)); setupDPR(); });
  const W = () => CSS_W, Hc = () => CSS_H; // funciones para medidas

  // HUD
  const scoreEl = document.getElementById('score');
  const ballsEl = document.getElementById('balls');
  const resetBtn = document.getElementById('resetBtn');

  // Controles táctiles
  const leftBtn = document.getElementById('leftBtn');
  const rightBtn = document.getElementById('rightBtn');
  const launchBtn = document.getElementById('launchBtn');

  // Utilidades
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const dist2 = (ax, ay, bx, by) => (ax-bx)*(ax-bx) + (ay-by)*(ay-by);
  const len = (x,y) => Math.hypot(x,y);
  const dot = (ax,ay,bx,by) => ax*bx+ay*by;

  // Estado de juego
  const g = 1900; // gravedad px/s^2
  const restitution = 0.95;
  const friction = 0.997;
  let score = 0;
  let balls = 3;

  const ball = { x: W()-35, y: Hc()-120, vx: 0, vy: 0, r: 11, inPlay: false };
  const ballTrail = [];

  // Paredes como segmentos (x1,y1,x2,y2)
  const walls = [];
  function buildWalls(){
    walls.length = 0;
    // bordes
    walls.push([20, 20, W()-20, 20]); // arriba
    walls.push([20, 20, 20, Hc()-140]); // izquierda
    walls.push([W()-20, 20, W()-20, Hc()-20]); // derecha
    // rampa inferior izquierda
    walls.push([20, Hc()-180, 140, Hc()-120]);
    // rampa inferior derecha (antes del carril de lanzamiento)
    walls.push([W()-80, Hc()-120, W()-20, Hc()-160]);
    // base con hueco para drenaje (entre flippers)
    // la base se gestiona vía colisiones de flippers; si cae por debajo de H-30 => pérdida de bola
  }

  // Bumpers (círculos)
  const bumpers = [
    {x: 140, y: 180, r: 24, k: 1100, score: 80},
    {x: 340, y: 200, r: 24, k: 1100, score: 80},
    {x: 240, y: 120, r: 28, k: 1300, score: 120},
    {x: 240, y: 300, r: 20, k: 1000, score: 50},
  ];

  // Flippers (cápsulas: segmento con radio)
  const flippers = {
    left: {
      pivotX: 170, pivotY: Hc()-110, len: 100, radius: 14,
      minA: -25 * Math.PI/180, maxA: 25 * Math.PI/180, a: -25*Math.PI/180, av: 0,
      key: false, side: -1
    },
    right: {
      pivotX: W()-170, pivotY: Hc()-110, len: 100, radius: 14,
      minA: -25 * Math.PI/180, maxA: 25 * Math.PI/180, a: 25*Math.PI/180, av: 0,
      key: false, side: 1
    }
  };
  const flipperSpeed = 22; // rad/s (más rápido)
  const flipperDamp = 20;  // amortiguación
  const flipperKick = 1400; // impulso adicional al pulsar

  function flipperTip(f){
    return { x: f.pivotX + Math.cos(f.a)*f.len, y: f.pivotY + Math.sin(f.a)*f.len };
  }

  // Entrada
  const keys = { left:false, right:false, space:false };
  window.addEventListener('keydown', (e)=>{
    if(e.code==='ArrowLeft' || e.code==='KeyA') { keys.left = true; flippers.left.key = true; }
    if(e.code==='ArrowRight' || e.code==='KeyD') { keys.right = true; flippers.right.key = true; }
    if(e.code==='Space'){ keys.space=true; launch(); }
    if(e.code==='ArrowLeft' || e.code==='KeyA') onFlipperPress(flippers.left);
    if(e.code==='ArrowRight' || e.code==='KeyD') onFlipperPress(flippers.right);
  });
  window.addEventListener('keyup', (e)=>{
    if(e.code==='ArrowLeft' || e.code==='KeyA') { keys.left = false; flippers.left.key = false; }
    if(e.code==='ArrowRight' || e.code==='KeyD') { keys.right = false; flippers.right.key = false; }
    if(e.code==='Space'){ keys.space=false; }
  });
  leftBtn.addEventListener('pointerdown', ()=> flippers.left.key = true);
  leftBtn.addEventListener('pointerup', ()=> flippers.left.key = false);
  rightBtn.addEventListener('pointerdown', ()=> flippers.right.key = true);
  rightBtn.addEventListener('pointerup', ()=> flippers.right.key = false);
  launchBtn.addEventListener('click', launch);
  resetBtn.addEventListener('click', resetAll);

  function launch(){
    if(!ball.inPlay && balls>0){
      ball.vx = 0; ball.vy = -1100 - Math.random()*250;
      ball.inPlay = true;
    }
  }

  function resetBall(){
    ball.x = W()-35; ball.y = Hc()-120; ball.vx=0; ball.vy=0; ball.inPlay=false;
    ballTrail.length = 0;
  }
  function resetAll(){ score=0; balls=3; updateHUD(); resetBall(); }

  function updateHUD(){ scoreEl.textContent = `Puntaje: ${score}`; ballsEl.textContent = `Bolas: ${balls}`; }

  // Física
  function integrate(dt){
    // Flippers
    for(const f of [flippers.left, flippers.right]){
      const target = f.key ? (f.side>0 ? f.maxA : f.maxA) : (f.side>0 ? f.minA : f.minA);
      const err = target - f.a;
      const accel = flipperSpeed*err - flipperDamp*f.av;
      f.av += accel*dt;
      f.a += f.av*dt;
      // límites
      if(f.a > f.maxA){ f.a = f.maxA; if(f.av>0) f.av=0; }
      if(f.a < f.minA){ f.a = f.minA; if(f.av<0) f.av=0; }
    }

    if(ball.inPlay){
      ball.vy += g*dt;
      ball.x += ball.vx*dt;
      ball.y += ball.vy*dt;
      ball.vx *= friction; ball.vy *= friction;
      // guardar estela
      ballTrail.push({x:ball.x, y:ball.y});
      if(ballTrail.length>18) ballTrail.shift();
    } else {
      // bola estacionada en carril de lanzamiento
      ball.x = W()-35; ball.y = clamp(ball.y, Hc()-200, Hc()-120);
    }

    // Colisiones con paredes
    for(const w of walls){
      collideCircleSegment(ball, w, restitution);
    }

    // Colisiones con bumpers
    for(const b of bumpers){
      const rSum = ball.r + b.r;
      const d2 = dist2(ball.x, ball.y, b.x, b.y);
      if(d2 < rSum*rSum){
        const d = Math.sqrt(Math.max(1e-6, d2));
        const nx = (ball.x - b.x)/d;
        const ny = (ball.y - b.y)/d;
        // empuje
        const force = b.k;
        ball.vx += nx * force * dt;
        ball.vy += ny * force * dt;
        // separa
        const overlap = rSum - d;
        ball.x += nx * overlap;
        ball.y += ny * overlap;
        // puntuación
        score += b.score;
        updateHUD();
      }
    }

    // Colisión con flippers (cápsulas)
    collideFlipper(ball, flippers.left);
    collideFlipper(ball, flippers.right);

    // Pérdida de bola
    if(ball.y - ball.r > Hc()-20){
      if(ball.inPlay){
        balls -= 1; updateHUD();
      }
      resetBall();
    }
  }

  // Impulso rápido al presionar flipper (para mejor respuesta)
  function onFlipperPress(f){
    // segment and nearest point
    const tip = flipperTip(f);
    const seg = [f.pivotX, f.pivotY, tip.x, tip.y];
    const [x1,y1,x2,y2] = seg;
    const vx = x2-x1, vy=y2-y1;
    const wx = ball.x - x1, wy = ball.y - y1;
    const vv = vx*vx+vy*vy || 1;
    let t = (wx*vx + wy*vy)/vv; t = clamp(t, 0, 1);
    const px = x1 + t*vx, py = y1 + t*vy;
    const dx = ball.x - px, dy = ball.y - py;
    const R = ball.r + f.radius + 16; // zona de ayuda
    if(dx*dx+dy*dy < R*R){
      const d = Math.max(1e-4, Math.hypot(dx,dy));
      const nx = dx/d, ny = dy/d;
      ball.vx += nx * flipperKick;
      ball.vy += ny * flipperKick;
      ball.inPlay = true;
      score += 2; updateHUD();
    }
  }

  function collideCircleSegment(c, seg, e){
    // seg: [x1,y1,x2,y2]
    const [x1,y1,x2,y2] = seg;
    const vx = x2-x1, vy=y2-y1;
    const wx = c.x - x1, wy = c.y - y1;
    const vv = vx*vx+vy*vy || 1;
    let t = (wx*vx + wy*vy)/vv; t = clamp(t, 0, 1);
    const px = x1 + t*vx, py = y1 + t*vy; // punto más cercano
    const dx = c.x - px, dy = c.y - py;
    const d2 = dx*dx+dy*dy; const r = c.r;
    if(d2 < r*r){
      const d = Math.sqrt(Math.max(1e-6,d2));
      const nx = dx/d, ny = dy/d; // normal desde pared hacia bola
      // separar
      const overlap = r - d;
      c.x += nx*overlap; c.y += ny*overlap;
      // reflejar velocidad
      const vn = c.vx*nx + c.vy*ny;
      if(vn < 0){
        c.vx -= (1+e)*vn*nx;
        c.vy -= (1+e)*vn*ny;
      }
    }
  }

  function collideFlipper(c, f){
    // segmento del flipper + radio
    const tip = flipperTip(f);
    const seg = [f.pivotX, f.pivotY, tip.x, tip.y];
    // expandimos el radio del segmento con el del flipper
    const R = c.r + f.radius;
    const [x1,y1,x2,y2] = seg;
    const vx = x2-x1, vy=y2-y1;
    const wx = c.x - x1, wy = c.y - y1;
    const vv = vx*vx+vy*vy || 1;
    let t = (wx*vx + wy*vy)/vv; t = clamp(t, 0, 1);
    const px = x1 + t*vx, py = y1 + t*vy;
    const dx = c.x - px, dy = c.y - py;
    const d2 = dx*dx+dy*dy;
    if(d2 < R*R){
      const d = Math.sqrt(Math.max(1e-6,d2));
      const nx = dx/d, ny = dy/d; // normal
      const overlap = R - d;
      c.x += nx*overlap; c.y += ny*overlap;
      // velocidad relativa (agrega efecto del flipper)
      // velocidad del punto de contacto por rotación: v = ω × r
      const rx = px - f.pivotX, ry = py - f.pivotY;
      // rotación CCW: perpendicular (-ry, rx) * ω
      const vfx = -ry * f.av; const vfy = rx * f.av;
      const rvx = c.vx - vfx; const rvy = c.vy - vfy;
      const vn = rvx*nx + rvy*ny;
      if(vn < 0){
        const e = 1.05; // un poco de energía extra
        const j = -(1+e)*vn;
        c.vx = rvx + j*nx + vfx; // devolver velocidad absoluta
        c.vy = rvy + j*ny + vfy;
        score += 1; updateHUD();
      }
    }
  }

  // Render
  function draw(){
    ctx.clearRect(0,0,W(),Hc());
    // mesa con gradiente y viñeta
    const grad = ctx.createRadialGradient(W()/2, 220, 60, W()/2, Hc()/2, Math.max(W(),Hc()));
    grad.addColorStop(0, '#0b1730');
    grad.addColorStop(1, '#070b16');
    ctx.fillStyle = grad; ctx.fillRect(0,0,W(),Hc());
    // paredes
    ctx.strokeStyle = '#37547a'; ctx.lineWidth = 6; ctx.lineCap='round';
    ctx.beginPath();
    for(const [x1,y1,x2,y2] of walls){
      ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
    }
    ctx.stroke();

    // carril de lanzamiento
    ctx.strokeStyle = '#203348'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(W()-60, 20); ctx.lineTo(W()-60, Hc()-20); ctx.stroke();

    // bumpers
    for(const b of bumpers){
      // halo
      const g2 = ctx.createRadialGradient(b.x,b.y,4,b.x,b.y,b.r+12);
      g2.addColorStop(0,'rgba(43,212,198,0.7)');
      g2.addColorStop(1,'rgba(43,212,198,0.0)');
      ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(b.x,b.y,b.r+12,0,Math.PI*2); ctx.fill();
      // cuerpo
      const g3 = ctx.createRadialGradient(b.x,b.y,2,b.x,b.y,b.r);
      g3.addColorStop(0,'#e7fdfb'); g3.addColorStop(1,'#1aa399');
      ctx.fillStyle = g3; ctx.beginPath(); ctx.arc(b.x,b.y,b.r,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle = '#0c7e76'; ctx.lineWidth=2; ctx.stroke();
    }

    // flippers
    drawFlipper(flippers.left, '#c9f27a');
    drawFlipper(flippers.right, '#f2a27a');

    // estela de bola
    for(let i=0;i<ballTrail.length;i++){
      const t = i/ballTrail.length; const a = t*0.5;
      ctx.beginPath(); ctx.fillStyle = `rgba(232,237,247,${a})`;
      ctx.arc(ballTrail[i].x, ballTrail[i].y, ball.r*(0.7+t*0.3), 0, Math.PI*2); ctx.fill();
    }
    // bola
    const shine = ctx.createRadialGradient(ball.x-3, ball.y-3, 1, ball.x, ball.y, ball.r);
    shine.addColorStop(0,'#ffffff'); shine.addColorStop(1,'#c8d2e3');
    ctx.beginPath(); ctx.fillStyle = shine;
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.6)'; ctx.lineWidth=1; ctx.stroke();

    // zona de pérdida
    ctx.fillStyle = 'rgba(230, 80, 80, 0.15)';
    ctx.fillRect(20, Hc()-20, W()-80, 20);
  }

  function drawFlipper(f, color){
    const tip = flipperTip(f);
    ctx.strokeStyle = color; ctx.lineWidth = f.radius*2; ctx.lineCap='round';
    ctx.beginPath(); ctx.moveTo(f.pivotX, f.pivotY); ctx.lineTo(tip.x, tip.y); ctx.stroke();
    // pivote
    ctx.beginPath(); ctx.fillStyle = '#556'; ctx.arc(f.pivotX, f.pivotY, f.radius+2, 0, Math.PI*2); ctx.fill();
  }

  // Bucle
  let last = performance.now();
  function loop(t){
    const dt = Math.min(1/30, (t-last)/1000); last = t;
    integrate(dt);
    draw();
    requestAnimationFrame(loop);
  }

  // Init
  function init(){
    buildWalls();
    updateHUD();
    resetBall();
    requestAnimationFrame(loop);
  }
  init();
})();
