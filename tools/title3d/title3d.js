// ================================================================== 3D title and select (Version 43)
// three.js draws the title street and the select screens on their own canvas over the game.
// It reads the game's own input (keys, touch, the portrait pad) and starts the run with newRun.
// If three.js or WebGL is missing, it never takes over and the 2D title and select carry on as before.
const T3 = (() => {
  const PW = 480, PH = 270;
  const root = document.getElementById('t3'), cv = document.getElementById('t3cv');
  const q = id => document.getElementById('t3-' + id);
  const api = { live: () => false, input() {}, back: () => false };
  if (!root || !cv) return api;

  // ---------------------------------------------------------------- data from the game
  const ORDER = ['marc', 'sam', 'seb', 'tim', 'byron', 'pearcy', 'kelly'];
  const BOSS = { frequency: 'The Parkie', soundz: 'Master Control', airport: 'No boss. Make the taxi rank.', road: 'No boss. Wreck the Espace.',
    divebar: 'Il Carabiniere, then I Fratelli', beach: 'Don Vito', club: 'Big Tony and Little Nicky', arrival: 'The Far Bank (two of them)',
    naval: 'No boss. Survive the night.', social: 'Nozzer, then Denise', pegnine: 'Big Gary', ramsden: 'Big Gaz, then Lady Addict' };
  const iE = ROUTE.indexOf('airport'), iC = ROUTE.indexOf('arrival');
  // each chapter tints the street while you browse it: world, sky, fog and lamp light
  const CHAPS = [
    { id: '1999', name: '1999', keys: ROUTE.slice(0, iE), mood: { world: [1, 1, 1], sky: [1, 1, 1], fog: 0x160b70, light: [1, 1, 1] } },
    { id: 'elba', name: 'ELBA 2002', keys: ROUTE.slice(iE, iC), mood: { world: [1.22, 0.98, 0.82], sky: [1.18, 0.9, 0.72], fog: 0x34115e, light: [1.1, 1, 0.85] } },
    { id: 'carpdiem', name: 'CARP DIEM', keys: ROUTE.slice(iC), mood: { world: [0.86, 1.08, 1.02], sky: [0.78, 1.04, 1.12], fog: 0x0f2c55, light: [0.85, 1.05, 1] } },
    { id: 'ramsden', name: 'RAMSDEN', keys: ['ramsden'], hidden: true, mood: { world: [1.3, 0.68, 0.62], sky: [1.35, 0.58, 0.55], fog: 0x3a0620, light: [1.3, 0.55, 0.4] } },
  ];
  const FLAT = CHAPS.flatMap((c, ci) => c.keys.map(k => ({ k, ci })));
  const DIFF_NOTE = { easy: 'Softer hits, more food.', normal: 'The way the lads played it.', hard: 'More of them. They hit harder.' };
  // a chapter's first stage starts the chapter (so the lobby and labels read as before); any other stage starts there
  const startFor = k => { const c = CHAPS.find(ch => ch.keys[0] === k); return c ? c.id : k; };
  const keyFor = s => { const c = CHAPS.find(ch => ch.id === s); return c ? c.keys[0] : ROUTE.includes(s) || s === 'ramsden' ? s : 'frequency'; };

  // ---------------------------------------------------------------- state
  let THREE = null, renderer = null, scene = null, camera = null, ready = false, failed = false, claimed = false;
  let view = 'title', viewT = 0, t = 0, intro = true, last = 0, lastMode = null, fadeTarget = 1;
  let li = 3, stageSel = 0, diffSel = 1, sendT = 0, sent = false, carry = false, picking = null;
  const lads = [], billboards = [], glows = [], pools = [];
  let backdrop, logo, logoW = 1, logoH = 1, spot, shaft, FOG, shared, V3;
  const cam = {}, tgt = {}, moodCur = {};
  const lg = { x: 0, y: 0, s: 1, ry: 0, rx: 0 };
  const T_FLY = 4.6, T_LOGO = 4.7, T_READY = 6.0;
  const ROAD = 150, KERB = 4, FRONT = 212, Z_NEAR = 3700, Z_FAR = -3200;
  const damp = (k, dt) => 1 - Math.exp(-k * dt);
  const easeInOut = k => k < .5 ? 4 * k ** 3 : 1 - (-2 * k + 2) ** 3 / 2;
  const easeBack = k => { const c = 1.6; return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2; };
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

  const live = () => ready && claimed && !failed;
  const showing = () => live() && (mode === 'title' || mode === 'select');
  const chosen = () => lads[li];
  const chap = () => CHAPS[FLAT[stageSel].ci];

  // ---------------------------------------------------------------- loading
  // the module script beside the layer starts the import; wait for it (module scripts run after this one)
  async function loadThree() {
    for (let i = 0; i < 200 && !window.__threeLoad; i++) await new Promise(r => setTimeout(r, 50));
    if (!window.__threeLoad) throw new Error('three.js did not start loading');
    return await window.__threeLoad;
  }
  const loadImg = src => new Promise((ok, bad) => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => bad(new Error(src)); im.src = src; });
  function prep(tx, mips) {
    tx.colorSpace = THREE.NoColorSpace; tx.magFilter = THREE.NearestFilter;
    tx.minFilter = mips ? THREE.NearestMipmapNearestFilter : THREE.NearestFilter; tx.generateMipmaps = !!mips;
    tx.needsUpdate = true; return tx;
  }
  function canvasTex(w, h, draw, mips) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.imageSmoothingEnabled = false; draw(g, w, h);
    return prep(new THREE.CanvasTexture(c), mips);
  }
  // the idle and run frames from a lad's sheet, packed into two rows
  // the idle, run, mini special and special frames from a lad's sheet, packed into four rows
  // (the last two play when he's chosen and when he's picked, Version 46)
  const ROWS = 4, ROW = { idle: 0, run: 1, mini: 2, special: 3 };
  // each lad's select-screen pose (Version 48): his own animation, drawn three-quarter on (south-east), a view the
  // fights never show. A strip of frames in sprites/pose_<id>.png at his sheet's cell size, feet on the sheet's anchor.
  // Frame 0 is him standing facing you (shown while he's chosen), the rest play when he's picked.
  const POSES = { tim: 1, seb: 1, byron: 1, pearcy: 1, kelly: 1, marc: 1, sam: 1 };
  function ladAtlas(id, img, pose) {
    const m = SPRITE_META[id], c = m.cell, idle = m.rows.idle, runR = m.rows.run;
    const all = r => r ? [...Array(r[1]).keys()] : [];
    const runF = (LAD_FRAMES[id] && LAD_FRAMES[id].run) || all(runR);
    const miniF = all(m.rows.mini), spF = pose ? [...Array(Math.floor(pose.width / c)).keys()] : (LAD_FRAMES[id] && LAD_FRAMES[id].special) || all(m.rows.special);
    const cols = Math.max(idle[1], runF.length, miniF.length, spF.length);
    const g = document.createElement('canvas'); g.width = cols * c; g.height = ROWS * c;
    const x = g.getContext('2d');
    for (let f = 0; f < idle[1]; f++) x.drawImage(img, f * c, idle[0] * c, c, c, f * c, 0, c, c);
    runF.forEach((fi, f) => x.drawImage(img, fi * c, runR[0] * c, c, c, f * c, c, c, c));
    if (m.rows.mini) miniF.forEach((fi, f) => x.drawImage(img, fi * c, m.rows.mini[0] * c, c, c, f * c, 2 * c, c, c));
    if (pose) spF.forEach((fi, f) => x.drawImage(pose, fi * c, 0, c, c, f * c, 3 * c, c, c));
    else if (m.rows.special) spF.forEach((fi, f) => x.drawImage(img, fi * c, m.rows.special[0] * c, c, c, f * c, 3 * c, c, c));
    return { tex: prep(new THREE.CanvasTexture(g)), cols, c, idleN: idle[1], runN: runF.length, miniN: miniF.length, spN: spF.length, ax: m.ax, ay: m.ay, pose: !!pose };
  }
  // what each lad shouts and sounds like when he's picked
  const PICK = { tim: ['RIGHT, LADS!', 'airhorn'], seb: ['SIR, YES SIR!', 'incoming'], byron: ['REF\u2019S DECISION!', 'whistle'],
    pearcy: ['CARP DIEM!', 'thud'], kelly: ['MASS HEAD!', 'ready'], marc: ['G\u2019DAY, LADS!', 'cooee'], sam: ['I\u2019M UP, I\u2019M UP!', 'yawn'] };
  // an action on the lad sprite: the frames of one row, forward, held, then back to standing
  function act(L, kind) {
    const n = kind === 'pick' ? L.a.spN : L.a.miniN; if (!n) return;
    const own = kind === 'pick' && L.a.pose;   // his own pose plays once and holds its last frame
    const fps = own ? 10 : kind === 'pick' ? 11 : 15, hold = own ? 0.75 : kind === 'pick' ? 0.55 : 0.12, back = own ? 0 : kind === 'pick' ? 18 : 22;
    L.act = { kind, row: kind === 'pick' ? ROW.special : ROW.mini, n, t: 0, fwd: n / fps, hold, back: back ? n / back : 0 };
    L.act.len = L.act.fwd + hold + L.act.back;
  }
  function actFrame(A) {
    if (A.t < A.fwd) return Math.min(A.n - 1, Math.floor(A.t / A.fwd * A.n));
    if (A.t < A.fwd + A.hold || !A.back) return A.n - 1;
    return Math.max(0, A.n - 1 - Math.floor((A.t - A.fwd - A.hold) / A.back * A.n));
  }

  const VERT = `
    uniform vec4 uvRect; varying vec2 vUv; varying float vDepth;
    void main() { vUv = uvRect.xy + uv * uvRect.zw; vec4 mv = modelViewMatrix * vec4(position, 1.0); vDepth = -mv.z; gl_Position = projectionMatrix * mv; }`;
  // dusk: tint everything blue-violet, but let warm bright pixels (lit windows, signs, lamps) keep their colour
  const FRAG = `
    uniform sampler2D map; uniform vec3 tint; uniform float glow; uniform vec3 fogColor; uniform vec2 fogRange; uniform float fade; uniform vec3 mood;
    varying vec2 vUv; varying float vDepth;
    void main() {
      vec4 c = texture2D(map, vUv); if (c.a < 0.5) discard;
      float lum = dot(c.rgb, vec3(0.299, 0.587, 0.114));
      float g = smoothstep(0.5, 0.78, lum) * step(c.b + 0.06, c.r) * glow;
      vec3 col = mix(c.rgb * tint * mood, c.rgb * 1.08, g);
      col = mix(col, fogColor, smoothstep(fogRange.x, fogRange.y, vDepth));
      gl_FragColor = vec4(col * fade, 1.0);
    }`;
  function mat(tex, { tint = [0.5, 0.44, 0.8], glow = 1, rect = [0, 0, 1, 1] } = {}) {
    return new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide,
      uniforms: { map: { value: tex }, tint: { value: new THREE.Vector3(...tint) }, glow: { value: glow }, uvRect: { value: new THREE.Vector4(...rect) }, ...shared } });
  }
  let haloTex, ellipseTex;
  function addPool(x, z, w, d, color, op) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map: ellipseTex, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, KERB + 0.6, z); m.userData.base = op; m.userData.color = new THREE.Color(color); m.renderOrder = 1;
    scene.add(m); pools.push(m); return m;
  }
  function addShadow(x, z, w) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w * 2, w * 0.6), new THREE.MeshBasicMaterial({ map: ellipseTex, color: 0x000000, transparent: true, opacity: 0.5, depthWrite: false }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, KERB + 0.8, z); m.renderOrder = 2; scene.add(m); return m;
  }
  function addBillboard(tex, x, z, ax, o) {
    const w = tex.image.width, h = tex.image.height;
    const g = new THREE.PlaneGeometry(w, h); g.translate(w / 2 - ax, h / 2, 0);
    const m = new THREE.Mesh(g, mat(tex, o)); m.position.set(x, KERB, z);
    scene.add(m); billboards.push(m); return m;
  }
  function logoTexture() {
    const font = '700 34px "Pixelify Sans", Impact, sans-serif', text = 'MBC LEGACIES';
    const c = document.createElement('canvas'), g = c.getContext('2d');
    g.font = font; const tw = Math.ceil(g.measureText(text).width);
    c.width = tw + 24; c.height = 52;
    const cx = c.width / 2, cy = 26;
    g.font = font; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round';
    g.fillStyle = 'rgba(0,0,0,.55)'; g.fillText(text, cx + 3, cy + 3);
    g.strokeStyle = OUT; g.lineWidth = 7; g.strokeText(text, cx, cy);
    g.fillStyle = '#f2a23a'; g.fillText(text, cx, cy);
    g.save(); g.beginPath(); g.rect(0, 0, c.width, cy - 6); g.clip(); g.fillStyle = '#ffd27a'; g.fillText(text, cx, cy); g.restore();
    // every pixel fully on or off, so the edges stay hard on the pixel grid
    const id = g.getImageData(0, 0, c.width, c.height), p = id.data;
    for (let i = 3; i < p.length; i += 4) p[i] = p[i] > 110 ? 255 : 0;
    g.putImageData(id, 0, 0);
    return prep(new THREE.CanvasTexture(c));
  }

  async function build() {
    THREE = await loadThree();
    V3 = (x, y, z) => new THREE.Vector3(x, y, z);
    renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: false, powerPreference: 'high-performance' });
    renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // the art's colours pass straight through
    renderer.setPixelRatio(1); renderer.setSize(PW, PH, false);
    cv.addEventListener('webglcontextlost', e => { e.preventDefault(); failed = true; root.hidden = true; });
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, PW / PH, 4, 6000); scene.add(camera);
    FOG = { color: new THREE.Color(0x160b70), near: 900, far: 2500 };
    shared = { fogColor: { value: FOG.color }, fogRange: { value: new THREE.Vector2(FOG.near, FOG.far) }, fade: { value: 0 },
      mood: { value: V3(1, 1, 1) }, sky: { value: V3(1, 1, 1) } };
    Object.assign(cam, { pos: V3(0, 118, 3300), look: V3(0, 110, 2600), fov: 58 });
    Object.assign(tgt, { pos: V3(), look: V3(), fov: 50 });
    Object.assign(moodCur, { world: V3(1, 1, 1), sky: V3(1, 1, 1), fog: new THREE.Color(0x160b70), light: V3(1, 1, 1) });
    haloTex = canvasTex(32, 32, g => {
      for (const [r, a] of [[15, 0.10], [11, 0.2], [7, 0.42], [4, 0.85]]) { g.fillStyle = `rgba(255,180,90,${a})`; for (let y = 0; y < 32; y++) for (let x = 0; x < 32; x++) if ((x - 15.5) ** 2 + (y - 15.5) ** 2 < r * r) g.fillRect(x, y, 1, 1); }
    });
    ellipseTex = canvasTex(32, 16, g => {
      for (let y = 0; y < 16; y++) for (let x = 0; x < 32; x++) { const v = ((x - 15.5) / 16) ** 2 + ((y - 7.5) / 8) ** 2; if (v < 1) { g.fillStyle = v < 0.45 ? '#fff' : 'rgba(255,255,255,.55)'; g.fillRect(x, y, 1, 1); } }
    });

    const SHOPS = ['chippy', 'kebab', 'pub', 'video', 'bookies', 'phones'];
    const paths = { street: 'bg/title/street.png', lamp: 'bg/orpington/lamp.png', phonebox: 'bg/orpington/phonebox.png', bench: 'bg/orpington/bench.png', bin: 'bg/props/bin.png' };
    SHOPS.forEach(s => { paths[s] = 'bg/orpington/' + s + '.png'; });
    ORDER.forEach(id => { paths['lad_' + id] = 'sprites/' + id + '.png'; });
    const img = {}; await Promise.all(Object.keys(paths).map(async k => { img[k] = await loadImg(paths[k]); }));
    // a lad can have his own pick pose: a strip of frames in his sheet's cell size, sprites/pose_<id>.png (Version 47)
    await Promise.all(Object.keys(POSES).map(async id => { try { img['pose_' + id] = await loadImg('sprites/pose_' + id + '.png'); } catch (e) { /* use his special */ } }));
    const T = {}; for (const k in img) if (!k.startsWith('lad_')) T[k] = prep(new THREE.Texture(img[k]));

    // backdrop: the title painting, hung far away on the camera's horizon
    backdrop = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: T.street, depthWrite: false, depthTest: false }));
    backdrop.renderOrder = -10;
    backdrop.material.onBeforeCompile = s => { s.uniforms.fade = shared.fade; s.uniforms.sky = shared.sky;
      s.fragmentShader = 'uniform float fade; uniform vec3 sky;\n' + s.fragmentShader.replace('#include <opaque_fragment>', 'diffuseColor.rgb *= sky * fade;\n#include <opaque_fragment>'); };
    scene.add(backdrop);

    const road = canvasTex(120, 120, (g, w, h) => {
      const sh = ['#120d52', '#150f5b', '#181262', '#130e55'];
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { g.fillStyle = sh[(rnd() * sh.length) | 0]; g.fillRect(x, y, 1, 1); }
      g.fillStyle = '#7d73cc'; g.fillRect(59, 0, 2, 54);
      g.fillStyle = '#3c3290'; g.fillRect(4, 0, 1, h); g.fillRect(w - 5, 0, 1, h);
    }, true);
    road.wrapS = road.wrapT = THREE.RepeatWrapping;
    const len = Z_NEAR - Z_FAR, mid = (Z_NEAR + Z_FAR) / 2, pw = FRONT - ROAD;
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(ROAD * 2, len), mat(road, { tint: [1, 1, 1], glow: 0, rect: [0, 0, 1, len / 240] }));
    ground.rotation.x = -Math.PI / 2; ground.position.z = mid; scene.add(ground);
    const pave = canvasTex(64, 40, (g, w, h) => {
      g.fillStyle = '#2b2276'; g.fillRect(0, 0, w, h);
      for (let i = 0; i < 260; i++) { g.fillStyle = rnd() < .5 ? '#271f6c' : '#30277e'; g.fillRect((rnd() * w) | 0, (rnd() * h) | 0, 1, 1); }
      g.fillStyle = '#1d1660'; g.fillRect(0, 0, w, 1); g.fillRect(0, 20, w, 1); g.fillRect(0, 0, 1, h); g.fillRect(32, 0, 1, h);
    }, true);
    pave.wrapS = pave.wrapT = THREE.RepeatWrapping;
    const kerbTex = canvasTex(4, 4, g => { g.fillStyle = '#5c52b4'; g.fillRect(0, 0, 4, 4); g.fillStyle = '#4a419e'; g.fillRect(0, 3, 4, 1); });
    for (const side of [-1, 1]) {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(pw + 30, len), mat(pave, { tint: [1, 1, 1], glow: 0, rect: [0, 0, pw / 64, len / 40] }));
      p.rotation.x = -Math.PI / 2; p.position.set(side * (ROAD + (pw + 30) / 2), KERB, mid); scene.add(p);
      const kerb = new THREE.Mesh(new THREE.PlaneGeometry(len, KERB), mat(kerbTex, { tint: [1, 1, 1], glow: 0 }));
      kerb.rotation.y = side * -Math.PI / 2; kerb.position.set(side * ROAD, KERB / 2, mid); scene.add(kerb);
    }
    // the Stage 1 shop fronts down both sides
    for (const side of [-1, 1]) {
      let z = Z_NEAR, k = side > 0 ? 3 : 0;
      while (z > Z_FAR) {
        const n = SHOPS[k % SHOPS.length]; k += 1 + (rnd() < 0.3 ? 1 : 0);
        const w = T[n].image.width, h = T[n].image.height;
        const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat(T[n]));
        m.rotation.y = side * -Math.PI / 2; m.position.set(side * FRONT, KERB + h / 2, z - w / 2); scene.add(m);
        addPool(side * (FRONT - 16), z - w / 2, w * 0.7, 26, 0xffa24a, 0.16);
        z -= w;
      }
    }
    for (let z = Z_NEAR - 60, i = 0; z > Z_FAR; z -= 150, i++) {
      const side = i % 2 ? 1 : -1, x = side * (ROAD + 12);
      addBillboard(T.lamp, x, z, 16, { tint: [0.62, 0.58, 0.86] });
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, fog: false }));
      halo.scale.set(34, 34, 1); halo.position.set(x - side, KERB + 90, z); halo.userData.flicker = rnd() < 0.12;
      scene.add(halo); glows.push(halo);
      addPool(x - side * 14, z, 96, 70, 0xffb060, 0.34);
    }
    const props = [['phonebox', 16], ['bin', 16], ['bench', 32], ['bin', 16]];
    for (let z = Z_NEAR - 140, i = 0; z > Z_FAR; z -= 230 + rnd() * 220, i++) {
      const [n, ax] = props[i % props.length], side = rnd() < 0.5 ? -1 : 1;
      if (z > -260 && z < 280) continue;   // keep the kerb clear round the lads' line-up (a bin was hiding Kelly)
      addBillboard(T[n], side * (FRONT - 26), z, ax, { tint: [0.56, 0.5, 0.84] });
      addShadow(side * (FRONT - 26), z, T[n].image.width * 0.5);
    }
    spot = addPool(0, 0, 120, 60, 0xffc070, 0);
    const shaftTex = canvasTex(32, 64, g => {
      for (let y = 0; y < 64; y++) { const half = 5 + y * 0.14, a = 0.22 * (y / 64) ** 1.5;
        g.fillStyle = `rgba(255,214,150,${a.toFixed(3)})`; g.fillRect(Math.round(16 - half), y, Math.round(half * 2), 1); }
    });
    shaft = new THREE.Mesh(new THREE.PlaneGeometry(56, 170), new THREE.MeshBasicMaterial({ map: shaftTex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    shaft.geometry.translate(0, 85, 0); shaft.renderOrder = 3; scene.add(shaft);

    // the seven lads, in a shallow V with the middle nearest
    ORDER.forEach((id, i) => {
      const a = ladAtlas(id, img['lad_' + id], img['pose_' + id]), depth = Math.abs(i - 3);
      const g = new THREE.PlaneGeometry(a.c, a.c); g.translate(a.c / 2 - a.ax, a.ay - a.c / 2, 0);
      const m = new THREE.Mesh(g, mat(a.tex, { tint: [0.86, 0.8, 0.98], glow: 0.6, rect: [0, 1 - 1 / ROWS, 1 / a.cols, 1 / ROWS] }));
      m.position.set(-330, KERB - 1, 0); m.visible = false; scene.add(m);
      lads.push({ id, a, m, sh: addShadow(0, 0, 24), i, tx: (i - 3) * 50, tz: 24 - depth * 18, delay: (6 - i) * 0.13,
        frame: 0, ft: 0, state: 'off', gx: 0, gz: 0, face: 1, wait: 0, moving: false, act: null, tint: V3(0.86, 0.8, 0.98) });
    });

    if (document.fonts && document.fonts.load) await Promise.race([document.fonts.load('700 34px "Pixelify Sans"').catch(() => {}), new Promise(r => setTimeout(r, 2500))]);
    const lt = logoTexture(); logoW = lt.image.width; logoH = lt.image.height;
    logo = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: lt, alphaTest: 0.5, side: THREE.DoubleSide, depthTest: false, depthWrite: false }));
    logo.renderOrder = 20; logo.visible = false; camera.add(logo);
    ready = true;
  }

  // ---------------------------------------------------------------- views
  function restart(skip) {
    view = 'title'; viewT = 0; t = skip ? T_READY : 0; intro = !skip; fadeTarget = 1; sent = false;
    if (!skip && shared) shared.fade.value = 0;
    for (const L of lads) {
      if (skip) { L.state = 'idle'; L.m.position.set(L.tx, KERB - 1, L.tz); L.gx = L.tx; L.gz = L.tz; }
      else { L.state = 'off'; L.m.position.x = -330; }
    }
    if (!skip) Object.assign(lg, { s: 3.2, ry: -Math.PI * 2.5 });
    sync();
  }
  // arriving at the select screens from elsewhere (back from a run, the board, the lobby)
  function enterSelect() {
    const c = PLAYABLE[sel]; li = Math.max(0, ORDER.indexOf(c && c.id));
    const k = keyFor(startAt); stageSel = Math.max(0, FLAT.findIndex(f => f.k === k));
    if (CHAPS[FLAT[stageSel].ci].hidden && !settings.unlocked) stageSel = 0;
    diffSel = Math.max(0, DIFF_ORDER.indexOf(settings.diff));
    intro = false; sent = false; shared.fade.value = 0; fadeTarget = 1;
    for (const L of lads) { L.state = 'idle'; L.wait = 0; L.m.position.set(L.tx, KERB - 1, L.tz); }
    setView('lad');
    selectPose(); cam.pos.copy(tgt.pos); cam.look.copy(tgt.look); cam.fov = tgt.fov;
    Object.assign(lg, { x: -PW / 2 + 60, y: PH / 2 - 13, s: 0.4, ry: 0, rx: 0 });
  }
  function setView(v) {
    view = v; viewT = 0;
    const L = chosen();
    if (v !== 'lad') picking = null;
    if (v === 'lad' || v === 'cont') for (const o of lads) { o.gx = o.tx; o.gz = o.tz + (o === L ? 30 : 0); }
    if (v === 'lad') flex(L);
    else if (v === 'stage') {
      const spots = [[-124, -40], [124, -60], [-140, -130], [140, -150], [-118, -220], [118, -240]];
      let k = 0; for (const o of lads) { if (o === L) { o.gx = 0; o.gz = 40; } else [o.gx, o.gz] = spots[k++]; }
    } else if (v === 'diff') {
      const spots = [[44, -26], [-40, -38], [88, -56], [-82, -70], [130, -86], [-124, -102]];
      let k = 0; for (const o of lads) { if (o === L) { o.gx = 0; o.gz = 40; } else [o.gx, o.gz] = spots[k++]; }
    } else if (v === 'go') {
      let k = 0; for (const o of lads) { o.gx = 900; o.wait = o === L ? 0 : 0.12 + 0.09 * k++; }
    }
    sync();
  }
  function next() {
    audioInit();
    if (view === 'title') {
      if (t < T_READY) { restart(true); return; }
      sfx('start'); mode = 'select'; modeT = 0; lastMode = 'select';
      // a run saved when the app closed: offer to carry on with it first (Version 45)
      const sr = savedRun();
      if (sr) { li = Math.max(0, ORDER.indexOf(PLAYABLE[sr.ci].id)); setView('cont'); } else setView('lad');
    } else if (view === 'cont') carryOn();
    else if (view === 'lad') {
      if (picking) { picking = null; sfx('page'); setView('stage'); return; }   // pressed again: skip the show
      pick();
    }
    else if (view === 'stage') { if (stageLocked()) { sfx('nope'); return; } sfx('page'); setView('diff'); }
    else if (view === 'diff') { sfx('start'); commit(); setView('go'); }
  }
  function carryOn() { if (!savedRun()) { setView('lad'); return; } sfx('start'); carry = true; setView('go'); }
  function newInstead() { sfx('page'); setView('lad'); }
  function pick() {
    const L = chosen(), id = L.id, P = PICK[id] || ['', 'start'];
    act(L, 'pick'); L.tint.set(2.4, 2.3, 2.1);
    picking = { t: 0, len: L.act ? L.act.len + 0.15 : 0.4 };
    sfx('special'); sfx(P[1]); if (P[0]) toast(P[0], 'shout');
    q('pick').textContent = CHAR_BY_ID[id].name + '!'; q('pick').disabled = true;
  }
  function flex(L) { if (!L.act && !L.a.pose) act(L, 'mini'); }   // lads with a pose turn to face you instead
  function back() {
    if (picking) { picking = null; const L = chosen(); L.act = null; sfx('page'); renderLad(); return true; }
    if (view === 'cont') { sfx('page'); mode = 'title'; modeT = 0; lastMode = 'title'; restart(true); return true; }
    if (view === 'lad') { sfx('page'); mode = 'title'; modeT = 0; lastMode = 'title'; restart(true); }
    else if (view === 'stage') { sfx('page'); setView('lad'); }
    else if (view === 'diff') { sfx('page'); setView('stage'); }
    return true;
  }
  // hand the choices to the game
  function commit() {
    const id = ORDER[li];
    sel = Math.max(0, PLAYABLE.findIndex(c => c.id === id));
    startAt = startFor(FLAT[stageSel].k);
    settings.diff = DIFF_ORDER[diffSel]; saveSettings();
  }
  const stageLocked = () => chap().hidden && !settings.unlocked;
  function chooseLad(i) {
    if (i === li || picking) return;
    for (const o of lads) if (o.act && o.act.kind === 'mini') o.act = null;
    li = i; sfx('swing'); renderLad(); for (const o of lads) { o.gx = o.tx; o.gz = o.tz + (o === chosen() ? 30 : 0); }
    flex(chosen());   // a quick flourish from his mini special once he's stepped forward
  }
  function moveStage(d) { stageSel = (stageSel + d + FLAT.length) % FLAT.length; sfx('swing'); renderStage(); }
  function moveChap(d) { const ci = (FLAT[stageSel].ci + d + CHAPS.length) % CHAPS.length; stageSel = FLAT.findIndex(f => f.ci === ci); sfx('swing'); renderStage(); }
  function setDiff(d) { if (d === diffSel) return; diffSel = d; sfx('swing'); renderDiff(); }
  function toggleSound() { settings.sound = !settings.sound; saveSettings(); applySound(); sfx('page'); renderFoot(); }
  function toast(msg, cls) { const el = q('toast'); el.textContent = msg; el.className = ''; void el.offsetWidth; el.classList.add('on'); if (cls) el.classList.add(cls); }

  // ---------------------------------------------------------------- menus
  function sync() {
    const on = (id, v) => { const el = q(id); el.classList.toggle('on', v); el.inert = !v; if (!v && el.contains(document.activeElement)) document.activeElement.blur(); };
    const menu = view === 'lad' || view === 'stage' || view === 'diff';
    on('crumbs', menu); on('foot', menu || view === 'cont'); on('cont', view === 'cont');
    on('lad', view === 'lad'); on('roster', view === 'lad');
    on('stages', view === 'stage'); on('info', view === 'stage'); on('diff', view === 'diff');
    if (view !== 'title') ['sub', 'start', 'tag'].forEach(id => q(id).classList.remove('on', 'blink'));
    root.querySelectorAll('#t3-crumbs span').forEach(s => {
      const steps = ['lad', 'stage', 'diff'], i = steps.indexOf(s.dataset.step), cur = steps.indexOf(view);
      s.className = i === cur ? 'now' : i < cur ? 'done' : '';
    });
    q('start').textContent = padOn() ? 'HIT TO START' : touchUI ? 'TAP TO START' : 'PRESS START';
    q('hint').textContent = hint();
    renderFoot();
    if (view === 'lad') renderLad();
    if (view === 'stage') renderStage();
    if (view === 'diff') renderDiff();
    if (view === 'cont') renderCont();
  }
  function renderCont() {
    const r = savedRun(); if (!r) return;
    const st = STAGES[r.route[r.idx]], c = PLAYABLE[r.ci], d = DIFFS[r.diff] || DIFFS.normal;
    q('cstage').textContent = (st.hidden ? 'Hidden stage' : 'Stage ' + st.n) + ' \u00B7 ' + st.title;
    q('cline').textContent = c.name + ' \u00B7 ' + r.lives + (r.lives === 1 ? ' life' : ' lives') + ' \u00B7 ' + (r.score || 0).toLocaleString('en-GB') + ' points \u00B7 ' + d.label;
  }
  function hint() {
    const pad = padOn(), tch = touchUI && !pad;
    return ({
      lad: pad ? 'Stick to choose · HIT to pick · BACK' : tch ? 'Tap a lad. Tap again to pick.' : '← → choose · J pick · Esc back',
      stage: pad ? 'Stick for chapter · HIT to start here' : tch ? 'Tap a chapter, then a stage.' : '← → chapter · ↑ ↓ stage · J start here',
      diff: pad ? 'Stick for difficulty · HIT to go' : tch ? 'Pick a difficulty, then go.' : '← → difficulty · F language · J go',
      cont: pad ? 'HIT to carry on · JUMP for a new run' : tch ? 'Carry on, or start a new run.' : 'J carry on · K new run · Esc back',
    })[view] || '';
  }
  function renderFoot() {
    q('sound').textContent = 'Sound ' + (settings.sound ? 'on' : 'off');
    q('sound').setAttribute('aria-pressed', String(!!settings.sound)); q('sound').classList.toggle('off', !settings.sound);
    q('online').hidden = !netAvailable();
    q('hint').textContent = hint();
  }
  function renderLad() {
    const c = CHAR_BY_ID[chosen().id], mm = MINI[c.id];
    q('name').textContent = c.name; q('name').style.color = c.color;
    q('ltag').textContent = c.tag;
    q('stats').innerHTML = ['Speed', 'Power', 'Grit'].map((l, j) =>
      `<span class="t3cap">${l}</span><span class="t3bar" role="img" aria-label="${l} ${c.stats[j]} of 5">${[0, 1, 2, 3, 4].map(k => `<b class="${k < c.stats[j] ? 'f' : ''}"></b>`).join('')}</span>`).join('');
    q('special').textContent = c.special; q('blurb').textContent = c.blurb;
    q('mini').textContent = mm ? mm.name : '';
    q('minicap').textContent = 'Mini special · ' + (touchUI ? 'hold HIT, let go' : 'hold J, let go');
    q('pick').textContent = 'PICK ' + c.name; q('pick').disabled = false;
    q('roster').innerHTML = ORDER.map((id, i) => `<button type="button" data-i="${i}" aria-pressed="${i === li}" style="--c:${CHAR_BY_ID[id].color}">${CHAR_BY_ID[id].name}</button>`).join('');
  }
  function stageNo(k) { return STAGES[k].hidden ? 'Hidden stage' : 'Stage ' + STAGES[k].n + ' of ' + ROUTE.length; }
  function renderStage() {
    const f = FLAT[stageSel], ch = CHAPS[f.ci], locked = stageLocked(), st = STAGES[f.k];
    q('tabs').innerHTML = CHAPS.map((c, i) => `<button type="button" role="tab" data-c="${i}" aria-selected="${i === f.ci}">${c.name}</button>`).join('');
    const RK = typeof stageRanks === 'function' ? stageRanks() : {};   // best rank per stage (Version 49)
    q('list').innerHTML = ch.keys.map(k => {
      const fi = FLAT.findIndex(x => x.k === k), s = STAGES[k];
      return `<li><button type="button" data-f="${fi}" aria-pressed="${fi === stageSel}"${locked ? ' disabled' : ''}><span class="n">${s.hidden ? '?' : String(s.n).padStart(2, '0')}</span>${locked ? 'LOCKED' : s.title}${!locked && RK[k] ? `<span class="rk r${RK[k]}" aria-label="Best rank ${RK[k]}">${RK[k]}</span>` : ''}</button></li>`;
    }).join('');
    q('snum').textContent = locked ? ch.name : stageNo(f.k) + ' · ' + ch.name;
    q('stitle').textContent = locked ? '? ? ?' : st.title;
    q('ssub').textContent = locked ? 'Hidden. Find the way in.' : st.sub;
    q('sboss').innerHTML = locked ? '' : '<span class="t3cap">Boss</span><br>' + BOSS[f.k];
    const r = routeFrom(startFor(f.k));
    q('snote').textContent = locked ? '' : r.length === 1 ? 'Just this stage.' : r.length + ' stages from here to the end of the run.';
    q('here').disabled = locked;
  }
  function renderDiff() {
    const k = FLAT[stageSel].k;
    q('runline').textContent = CHAR_BY_ID[chosen().id].name + ' · ' + (STAGES[k].hidden ? 'Hidden stage' : 'Stage ' + STAGES[k].n) + ' · ' + STAGES[k].title;
    q('cards').innerHTML = DIFF_ORDER.map((id, i) => { const d = DIFFS[id];
      return `<button type="button" data-d="${i}" aria-pressed="${i === diffSel}"><span class="t3h">${d.label}</span><span class="lives" role="img" aria-label="${d.lives} lives">${'<b></b>'.repeat(d.lives)}</span>
        <span class="t3cap" style="color:var(--t3cream)">${d.lives} lives · ${d.pts ? d.pts.toLowerCase().replace(/^./, s => s.toUpperCase()) : 'Full points'}</span><span class="t3txt" style="color:var(--t3grey)">${DIFF_NOTE[id]}</span></button>`; }).join('');
    q('lang').textContent = 'Language: ' + (settings.sweary ? 'Sweary' : 'Family');
    q('lang').setAttribute('aria-pressed', String(!!settings.sweary));
  }

  // ---------------------------------------------------------------- input from the game (keys, pad, touch buttons)
  function input() {
    if (!showing()) return;
    const P = a => pressed.has(a);
    if (typed.endsWith('RAMSDEN') && !settings.unlocked) {
      settings.unlocked = true; saveSettings(); typed = ''; sfx('jackpot'); toast('RAMSDEN UNLOCKED');
      if (view === 'stage') renderStage();
    }
    if (view === 'title') { if (P('punch') || P('start') || P('jump') || P('special')) next(); return; }
    if (view === 'go') return;
    if (P('mute')) toggleSound();
    if (P('board')) { sfx('page'); openBoard(null, 'select'); return; }
    if (P('online') && netAvailable()) { sfx('page'); openNetLobby(); return; }
    if (P('escape') || P('back')) { back(); return; }
    if (P('punch') || P('start')) { next(); return; }
    if (view === 'cont') { if (P('jump')) newInstead(); return; }
    if (view === 'lad' && !picking) { if (P('left')) chooseLad((li + 6) % 7); if (P('right')) chooseLad((li + 1) % 7); }
    else if (view === 'stage') { if (P('left')) moveChap(-1); if (P('right')) moveChap(1); if (P('up')) moveStage(-1); if (P('down')) moveStage(1); }
    else if (view === 'diff') {
      if (P('left')) setDiff(Math.max(0, diffSel - 1)); if (P('right')) setDiff(Math.min(2, diffSel + 1));
      if (P('diff')) setDiff((diffSel + 1) % 3);
      if (P('lang')) { settings.sweary = !settings.sweary; saveSettings(); sfx('page'); renderDiff(); }
    }
  }

  // tap a lad in the street: the one whose middle is nearest the tap
  function ladAt(cx, cy) {
    const r = cv.getBoundingClientRect(), v = V3(0, 0, 0);
    let best = -1, bd = 1e9;
    lads.forEach((o, i) => {
      v.set(o.m.position.x, 32, o.m.position.z).project(camera);
      const x = (v.x + 1) / 2 * r.width + r.left, y = (1 - v.y) / 2 * r.height + r.top;
      const d = Math.hypot(x - cx, (y - cy) * 0.6);
      if (d < bd) { bd = d; best = i; }
    });
    return bd < 40 * r.width / PW ? best : -1;
  }
  cv.addEventListener('pointerdown', e => {
    if (!showing()) return;
    audioInit(); if (e.pointerType === 'touch' || e.pointerType === 'pen') touchUI = true;
    if (view === 'title') { next(); return; }
    if (view === 'lad') { const i = ladAt(e.clientX, e.clientY); if (i < 0) return; if (i === li) next(); else chooseLad(i); }
  });
  const click = (id, fn) => q(id).addEventListener('click', e => { audioInit(); fn(e); });
  click('roster', e => { const b = e.target.closest('button'); if (b) chooseLad(+b.dataset.i); });
  click('pick', next);
  click('tabs', e => { const b = e.target.closest('button'); if (b) { stageSel = FLAT.findIndex(f => f.ci === +b.dataset.c); sfx('swing'); renderStage(); } });
  click('list', e => { const b = e.target.closest('button'); if (!b) return; const f = +b.dataset.f; if (f === stageSel) next(); else { stageSel = f; sfx('swing'); renderStage(); } });
  click('here', next);
  click('cards', e => { const b = e.target.closest('button'); if (!b) return; const d = +b.dataset.d; if (d === diffSel) next(); else setDiff(d); });
  click('lang', () => { settings.sweary = !settings.sweary; saveSettings(); sfx('page'); renderDiff(); });
  click('go', next);
  click('back', back);
  click('carry', carryOn);
  click('new', newInstead);
  click('sound', toggleSound);
  click('board', () => { sfx('page'); openBoard(null, 'select'); });
  click('online', () => { if (netAvailable()) { sfx('page'); openNetLobby(); } });

  // ---------------------------------------------------------------- camera poses
  function titlePose() {
    const k = clamp(t / T_FLY, 0, 1), e = 1 - (1 - k) ** 3, idle = reduceMotion ? 0 : 1;
    const sw = Math.max(0, t - T_FLY), settle = clamp(sw / 2, 0, 1) * idle;
    tgt.pos.set(Math.sin(t * 1.25) * 34 * (1 - e) + settle * Math.sin(sw * 0.23) * 28, 118 - 40 * e + settle * Math.sin(sw * 0.31) * 3, 3300 - 3050 * e + settle * Math.sin(sw * 0.17) * 14);
    tgt.fov = 58 - 8 * e;
    tgt.look.set(tgt.pos.x * 0.3, tgt.pos.y - 8, tgt.pos.z - 700);
  }
  function selectPose() {
    const L = chosen();
    if (view === 'lad' || view === 'cont') {
      // picking: the camera leans in on him and swings round to centre him
      const k = picking && !reduceMotion ? easeInOut(clamp(picking.t / 0.5, 0, 1)) : 0;
      // the camera sits behind and to the right of him; for the lads at the right-hand end (Kelly is on the kerb)
      // that would put it inside the shop fronts, so it stays on the pavement and turns to frame him instead
      const off = 72 - 34 * k, back = 165 - 32 * k, cx = Math.min(L.gx + off, FRONT - 46);
      const yaw = Math.atan2(L.gx - cx, back) - Math.atan2(-off, back);
      tgt.pos.set(cx, 46 - 4 * k, L.gz + back); tgt.look.set(cx + Math.sin(yaw) * 665, 40 - 3 * k, L.gz + back - Math.cos(yaw) * 665); tgt.fov = 50 - 4 * k;
    }
    else if (view === 'stage') { tgt.pos.set(Math.sin(t * 0.2) * 10 * (reduceMotion ? 0 : 1), 118, 330); tgt.look.set(0, 44, -420); tgt.fov = 50; }
    else if (view === 'diff') { tgt.pos.set(-118, 22, 186); tgt.look.set(-20, 50, -150); tgt.fov = 46; }
    else { const k = easeInOut(clamp(viewT / 1.6, 0, 1)); tgt.pos.set(-118 + 260 * k, 22 + 24 * k, 186 - 40 * k); tgt.look.set(-20 + 300 * k, 50, -150); tgt.fov = 46 + 6 * k; }
  }

  // ---------------------------------------------------------------- per frame
  function step(dt) {
    t += dt; viewT += dt;
    if (picking) { picking.t += dt; if (picking.t >= picking.len) { picking = null; sfx('page'); setView('stage'); } }
    if (view === 'title') {
      titlePose();
      if (intro && t < T_FLY + 0.05) { cam.pos.copy(tgt.pos); cam.look.copy(tgt.look); cam.fov = tgt.fov; }
      else { intro = false; cam.pos.lerp(tgt.pos, damp(3, dt)); cam.look.lerp(tgt.look, damp(3.5, dt)); cam.fov += (tgt.fov - cam.fov) * damp(3, dt); }
    } else {
      selectPose();
      const kp = view === 'go' ? 4 : 2.6;
      cam.pos.lerp(tgt.pos, damp(kp, dt)); cam.look.lerp(tgt.look, damp(kp + 0.6, dt)); cam.fov += (tgt.fov - cam.fov) * damp(2.6, dt);
    }
    camera.position.copy(cam.pos); camera.lookAt(cam.look); camera.fov = cam.fov; camera.updateProjectionMatrix();

    // the send-off: everyone runs off, fade to black, then the run starts
    if (view === 'go' && viewT > 1.15) fadeTarget = 0;
    if (view === 'go' && viewT > 1.75 && !sent) { sent = true; if (carry) { carry = false; if (!continueRun()) newRun(sel, startAt); } else newRun(sel, startAt); }
    const into = view === 'title' && intro ? clamp(t / 0.6, 0, 1) : 1;
    shared.fade.value += (Math.min(fadeTarget, into) - shared.fade.value) * damp(view === 'title' && intro ? 30 : view === 'go' ? 6 : 4, dt);
    const fade = shared.fade.value;

    const md = view === 'title' ? CHAPS[0].mood : chap().mood, mk = damp(2.2, dt);
    moodCur.world.lerp(V3(...md.world), mk); moodCur.sky.lerp(V3(...md.sky), mk); moodCur.light.lerp(V3(...md.light), mk); moodCur.fog.lerp(new THREE.Color(md.fog), mk);
    shared.mood.value.copy(moodCur.world); shared.sky.value.copy(moodCur.sky); FOG.color.copy(moodCur.fog);
    const lc = new THREE.Color(moodCur.light.x, moodCur.light.y, moodCur.light.z);

    // the painted backdrop sits on the horizon; when the camera turns or tilts it grows around the vanishing point
    const dist = 2800, vh = THREE.MathUtils.degToRad(camera.fov / 2), hh = Math.atan(Math.tan(vh) * PW / PH);
    const dir = cam.look.clone().sub(cam.pos), yaw = Math.abs(Math.atan2(dir.x, -dir.z)), pitch = Math.abs(Math.atan2(dir.y, Math.hypot(dir.x, dir.z)));
    const needW = 2 * dist * Math.tan(Math.min(1.35, yaw + hh + 0.06)), needH = 2 * dist * Math.tan(Math.min(1.3, pitch + vh + 0.06)) * 1.2;
    const bh = Math.max(2 * dist * Math.tan(vh) * 1.35, needH, needW * 224 / 400), bw = bh * 400 / 224;
    backdrop.scale.set(bw, bh, 1); backdrop.position.set(cam.pos.x, cam.pos.y + bh * (11 / 224), cam.pos.z - dist);

    for (const b of billboards) b.rotation.y = Math.atan2(cam.pos.x - b.position.x, cam.pos.z - b.position.z);
    const away = z => { const d = cam.pos.z - z; return d < 0 ? 0 : 1 - clamp((d - FOG.near) / (FOG.far - FOG.near), 0, 1); };
    for (const g of glows) { g.material.opacity = away(g.position.z) * fade * (g.userData.flicker && Math.sin(t * 31) * Math.sin(t * 7.3) > 0.55 ? 0.25 : 1); g.material.color.copy(lc); }
    for (const p of pools) { if (p === spot) continue; p.material.opacity = p.userData.base * fade * away(p.position.z); p.material.color.copy(p.userData.color).multiply(lc); }

    for (const L of lads) {
      if (L.state === 'off' && view === 'title' && t >= 3.3 + L.delay) { L.state = 'enter'; L.m.position.set(-330 - L.i * 14, KERB - 1, L.tz); }
      let moving = false;
      if (L.state === 'enter') {
        L.m.position.x += 300 * dt; moving = true; L.face = 1;
        if (L.m.position.x >= L.tx) { L.m.position.x = L.tx; L.state = 'idle'; L.gx = L.tx; L.gz = L.tz; }
      } else if (L.state === 'idle') {
        if (L.wait > 0) L.wait -= dt;
        else {
          const p = L.m.position, dx = L.gx - p.x, dz = L.gz - p.z, d = Math.hypot(dx, dz), sp = view === 'go' ? 330 : 190;
          if (d > 1.5) { const s = Math.min(d, sp * dt); p.x += dx / d * s; p.z += dz / d * s; moving = true; if (Math.abs(dx) > 1) L.face = dx > 0 ? 1 : -1; }
          else { p.x = L.gx; p.z = L.gz; L.face = 1; }
        }
      }
      if (moving !== L.moving) { L.frame = 0; L.ft = 0; L.moving = moving; }
      const u = L.m.material.uniforms.uvRect.value;
      if (L.act && !moving) {
        L.act.t += dt;
        if (L.act.t >= L.act.len) { L.act = null; L.frame = 0; L.ft = 0; }
      }
      const facing = !moving && L.a.pose && L === chosen() && (view === 'lad' || view === 'cont');
      if (L.act && !moving) { u.x = actFrame(L.act) / L.a.cols; u.y = 1 - (L.act.row + 1) / ROWS; }
      else if (facing) { u.x = 0; u.y = 1 - (ROW.special + 1) / ROWS; }   // chosen: turned to face you
      else {
        const n = moving ? L.a.runN : L.a.idleN, fps = moving ? 14 : 7;
        L.ft += dt; if (L.ft > 1 / fps) { L.ft = 0; L.frame = (L.frame + 1) % n; }
        u.x = L.frame / L.a.cols; u.y = 1 - ((moving ? ROW.run : ROW.idle) + 1) / ROWS;
      }
      L.m.visible = L.state !== 'off';
      L.m.rotation.y = Math.atan2(cam.pos.x - L.m.position.x, cam.pos.z - L.m.position.z); L.m.scale.x = L.face;
      L.m.scale.y = facing && !L.act && !reduceMotion ? 1 + Math.sin(t * 3.1) * 0.012 : 1;   // breathing while he faces you
      L.sh.visible = L.m.visible; L.sh.position.set(L.m.position.x, KERB + 0.8, L.m.position.z);
      const pick = L === chosen() && view !== 'title';
      const tt = view === 'title' || view === 'go' ? [0.86, 0.8, 0.98] : pick ? [1, 0.95, 1.04] : view === 'lad' || view === 'cont' ? [0.42, 0.38, 0.6] : [0.62, 0.56, 0.78];
      L.tint.lerp(V3(...tt), damp(L.act && L.act.kind === 'pick' ? 3 : 5, dt)); L.m.material.uniforms.tint.value.copy(L.tint);
    }
    const L = chosen(), menu = view === 'lad' || view === 'diff' || view === 'stage' || view === 'cont';
    spot.position.set(L.m.position.x, KERB + 0.7, L.m.position.z);
    spot.material.opacity += ((picking ? 0.95 : menu ? 0.5 : 0) * fade - spot.material.opacity) * damp(picking ? 9 : 4, dt);
    shaft.position.set(L.m.position.x, KERB, L.m.position.z - 2);
    shaft.rotation.y = Math.atan2(cam.pos.x - shaft.position.x, cam.pos.z - shaft.position.z);
    shaft.material.opacity += ((picking ? 0.9 : view === 'lad' || view === 'diff' || view === 'cont' ? 0.45 : 0) * fade - shaft.material.opacity) * damp(4, dt);

    // logo: spins in edge-on and lands, rocks gently, and tucks into the corner for the menus
    const pxu = 2 * 200 * Math.tan(vh) / PH, wob = reduceMotion ? 0 : 1;
    if (view === 'title' && intro) {
      const k = clamp((t - T_LOGO) / 1.1, 0, 1);
      Object.assign(lg, { x: 0, y: PH / 2 - 47, s: 1 + 2.2 * (1 - (1 - (1 - k) ** 3)), ry: -Math.PI * 2.5 * (1 - easeBack(k)), rx: 0 });
      logo.visible = t > T_LOGO;
    } else {
      const g = view !== 'title' ? { x: -PW / 2 + 60, y: PH / 2 - 13, s: 0.4, ry: 0, rx: 0 } : { x: 0, y: PH / 2 - 47, s: 1, ry: Math.sin(t * 0.9) * 0.16 * wob, rx: Math.sin(t * 0.7) * 0.07 * wob };
      const k = damp(5, dt); for (const key in g) lg[key] += (g[key] - lg[key]) * k;
      logo.visible = true;
    }
    logo.scale.set(logoW * pxu * lg.s, logoH * pxu * lg.s, 1); logo.position.set(lg.x * pxu, lg.y * pxu, -200);
    logo.rotation.set(lg.rx, lg.ry, 0); logo.material.color.setScalar(fade);
    if (view === 'title') {
      if (t > T_LOGO + 1.0) q('sub').classList.add('on');
      if (t > T_READY) { q('start').classList.add('on', 'blink'); q('tag').classList.add('on'); }
    }
  }

  // keep the layer exactly over the game canvas (full screen letterboxes it)
  let box = '';
  function place() {
    const c = canvas, b = c.offsetLeft + ',' + c.offsetTop + ',' + c.offsetWidth + ',' + c.offsetHeight;
    if (b === box) return; box = b;
    Object.assign(root.style, { left: c.offsetLeft + 'px', top: c.offsetTop + 'px', width: c.offsetWidth + 'px', height: c.offsetHeight + 'px' });
    root.style.setProperty('--s', c.offsetWidth / PW);
    // on a small screen (a phone held upright) let the menus scale down with the picture rather than overflow it
    root.style.setProperty('--t3m', c.offsetWidth / PW < 1.15 ? 0 : 1);
  }
  function tick(now) {
    requestAnimationFrame(tick);
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    if (!ready || failed) return;
    // take over the title only if the player hasn't got far into the 2D one yet
    if (!claimed) {
      if (mode === 'title' && modeT < 4) { claimed = true; restart(false); }
      else if (mode !== 'title' && mode !== 'select') claimed = true;
      else return;
    }
    // arriving at the select screens from anywhere but our own title (after a run, the board, the lobby)
    if (mode === 'select' && lastMode !== 'select' && lastMode !== null) enterSelect();
    lastMode = mode;
    const vis = mode === 'title' || mode === 'select';
    if (root.hidden === vis) { root.hidden = !vis; box = ''; if (vis) sync(); }
    if (!vis) return;
    place();
    try { step(dt); renderer.render(scene, camera); }
    catch (e) { failed = true; root.hidden = true; glitch('title3d', e); }
  }
  build().then(() => { if (mode !== 'title' && mode !== 'select') claimed = true; }).catch(e => { failed = true; root.hidden = true; console.warn('3D title off:', e && e.message); });
  requestAnimationFrame(tick);

  api.live = live;
  api.input = input;
  api.back = back;
  if (window.__mbcTest) window.__mbcTest.t3 = { step: s => { for (let i = 0; i < s * 60; i++) step(1 / 60); renderer.render(scene, camera); }, next, back, chooseLad, moveChap, moveStage, setDiff,
    state: () => ({ view, li, stageSel, diffSel, ready, claimed, failed, picking: !!picking, act: lads[li] && lads[li].act && lads[li].act.kind }),
    toSelect: () => { mode = 'select'; modeT = 0; },
    game: () => ({ mode, startAt, sel, route: run && run.route, off: run && run.off, diff: settings.diff, D: run ? D() : null }) };
  return api;
})();
