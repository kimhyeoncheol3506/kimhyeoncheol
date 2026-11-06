// Camera-projected reference matte (r7). Everything far from the camera (valley, lake + towns, cloud sea, far Alps,
// sky) shows reference image n itself, projected from view n's camera onto the scene depth; the near 3D content
// (ring, struts, bridges, the pinnacles / walls framing it) stays our render.
// Per sub-frame (post.accumulate / single render): reconstruct each pixel's point from the log depth buffer along the
// UNjittered pixel-centre ray (so the ref is sampled at pixel centres: sharp, and the identity at the exact ref
// camera), project it into the projector, weight w = farness x inside-ref-frame x strength, and accumulate
// (w * ref, w) in float like the colour: the 3D / matte joins are antialiased by the same K jittered sub-frames.
// Post.finish then composites ours * (1 - a) + ref * a in display space (after tone / grade), so the ref's sRGB
// values come through unchanged.
// Ref images: data/matte/bg_<n>.png, baked by tools/matte_bake.mjs (the ref with its own ring structure removed
// and inpainted, so no ghost ring appears beside ours).
import * as THREE from 'three';
import { VIEWS, applyView } from './views.js';
import { CLOUDS } from './config.js';

export const REF_W = 1672, REF_H = 941;
// farness ramp per view: distance from the camera (m) where the matte fades in [start, full]. Hero views: the
// near pinnacles / walls framing the ring sit within ~0.5 km, the gorge floor and the cloud sea beyond ~0.9 km.
export const MATTE_RAMP = {
  default: [700, 1100],
  8: [420, 620],        // top view: the void looks straight down at the cloud sea / gorge floor ~0.6 km below
};

const fsVert = /* glsl */ `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

export class Matte {
  // post: Post (sceneRT depth, size); camera: the render camera (read per sub-frame)
  static async create(renderer, post, camera, { showW = false } = {}) {
    const m = new Matte(renderer, post, camera, showW);
    await m.load();
    return m;
  }

  constructor(renderer, post, camera, showW) {
    this.renderer = renderer; this.post = post; this.camera = camera; this.showW = showW;
    this.tex = {};            // view -> ref texture
    this.proj = {};           // view -> { rot: Matrix3 (world -> projector view), pos, tan: Vector2 }
    this.view = 0; this.strength = 1; this.feather = 0; this.proxy = true; this.useForce = true; this.forceW = 1;
    this.valid = false;       // accumulation holds this frame's matte
    // float32 accumulation keeps the ref's 8-bit values exact through K additive sub-frames (needs float blending)
    const gl = renderer.getContext();
    this.type = gl.getExtension('EXT_float_blend') ? THREE.FloatType : THREE.HalfFloatType;
    this.accRT = new THREE.WebGLRenderTarget(post.w, post.h, { type: this.type, depthBuffer: false,
      minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
    this.subMat = new THREE.ShaderMaterial({
      uniforms: {
        tDepth: { value: null }, tRef: { value: null }, uRefSize: { value: new THREE.Vector2(REF_W, REF_H) },
        uLogF: { value: 1 }, uTan: { value: new THREE.Vector2(1, 1) }, uM: { value: new THREE.Matrix3() },
        uD: { value: new THREE.Vector3() }, uPTan: { value: new THREE.Vector2(1, 1) }, uRamp: { value: new THREE.Vector2(700, 1100) },
        uFeather: { value: 0 }, uW: { value: 1 }, uCamY: { value: 0 }, uUpV: { value: new THREE.Vector3(0, 1, 0) }, uProxyY: { value: CLOUDS.top },
        tForce: { value: null }, uForce: { value: 0 },
      },
      vertexShader: fsVert,
      fragmentShader: /* glsl */ `
        precision highp float;
        uniform sampler2D tDepth, tRef; uniform vec2 uRefSize, uTan, uPTan, uRamp; uniform float uLogF, uFeather, uW;
        uniform mat3 uM; uniform vec3 uD, uUpV; uniform float uCamY, uProxyY; varying vec2 vUv;
        uniform sampler2D tForce; uniform float uForce;
        // Catmull-Rom (16 texel fetches): sharp resampling for moving cameras, exact texel values at texel centres
        vec4 cr(float t){ float t2 = t * t, t3 = t2 * t;
          return vec4(-0.5 * t3 + t2 - 0.5 * t, 1.5 * t3 - 2.5 * t2 + 1.0, -1.5 * t3 + 2.0 * t2 + 0.5 * t, 0.5 * t3 - 0.5 * t2); }
        vec4 refAt(vec2 uv){
          vec2 p = uv * uRefSize - 0.5, i = floor(p), f = p - i;
          vec4 wx = cr(f.x), wy = cr(f.y);
          ivec2 mx = ivec2(uRefSize) - 1;
          vec4 c = vec4(0.0);
          for (int y = 0; y < 4; y++) {
            vec4 r = vec4(0.0);
            for (int x = 0; x < 4; x++) {
              ivec2 q = clamp(ivec2(i) + ivec2(x - 1, y - 1), ivec2(0), mx);
              r += texelFetch(tRef, q, 0) * wx[x];
            }
            c += r * wy[y];
          }
          return clamp(c, 0.0, 1.0);
        }
        void main(){
          float d = texelFetch(tDepth, ivec2(gl_FragCoord.xy), 0).r;
          float vz = exp2(d * uLogF) - 1.0;                 // log depth -> view depth (cleared: camera far = sky)
          vec3 vd = vec3((vUv * 2.0 - 1.0) * uTan, -1.0), vp = vd * vz;   // unjittered pixel-centre ray at that depth
          float far = smoothstep(uRamp.x, uRamp.y, length(vp));
          // project from the cloud-sea top where the ray crosses it before our geometry: the ref's cloud sea gets the
          // parallax of a cloud sea for moving cameras (at the exact ref camera any depth along the ray is the identity)
          float dy = dot(uUpV, vd);
          if (dy < -1e-4) { float tz = (uProxyY - uCamY) / dy; if (tz > 0.0 && tz < vz) vp = vd * tz; }
          vec3 q = uM * vp + uD;                            // projector view space
          float w = 0.0; vec3 c = vec3(0.0);
          if (q.z < -1.0) {
            vec2 uv = (q.xy / -q.z) / uPTan * 0.5 + 0.5;
            vec2 e = min(uv, 1.0 - uv) * uRefSize;            // px to the ref frame border
            float ed = min(e.x, e.y);
            float fr = uFeather > 0.0 ? smoothstep(0.0, uFeather, ed) : step(0.0, ed);
            // force-far mask (ref space): sky / far landscape of the ref where our near rock stands (stills)
            float fz = uForce > 0.0 ? textureLod(tForce, uv, 0.0).r * uForce : 0.0;
            w = max(far, fz) * fr;
            // bg alpha: ref-space keep mask (0 where the ref must never show, tools/matte_masks.json 'exclude')
            if (w > 0.0) { vec4 r = refAt(uv); c = r.rgb; w *= r.a; }
          }
          gl_FragColor = vec4(c * w, w) * uW;
        }`,
      depthTest: false, depthWrite: false, transparent: true,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor,
      blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneFactor,
    });
    // premultiplied over: out = ref * a + ours * (1 - a); '&mattew' shows a as grey instead
    this.compMat = new THREE.ShaderMaterial({
      uniforms: { tAcc: { value: null }, uFade: { value: 1 }, uShowW: { value: showW ? 1 : 0 } },
      vertexShader: fsVert,
      fragmentShader: /* glsl */ `
        uniform sampler2D tAcc; uniform float uFade, uShowW; varying vec2 vUv;
        void main(){
          vec4 m = texture2D(tAcc, vUv);
          gl_FragColor = uShowW > 0.5 ? vec4(vec3(m.a), 1.0) : vec4(clamp(m.rgb, 0.0, 1.0) * uFade, clamp(m.a, 0.0, 1.0));
        }`,
      depthTest: false, depthWrite: false, transparent: true,
      blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
      blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor,
    });
    this.compW = this.compMat.clone(); this.compW.blending = THREE.NoBlending;
    this.compW.uniforms = this.compMat.uniforms;
    // follow Post's render-target size
    const ps = post.setSize.bind(post);
    post.setSize = (w, h) => { ps(w, h); this.setSize(w, h); };
  }

  async load() {
    const loader = new THREE.TextureLoader();
    const cam = new THREE.PerspectiveCamera(40, REF_W / REF_H, 1, 1000);
    // force-far masks (data/matte/force_<n>.png, listed in force.json; tools/matte_bake.mjs 'force' polygons)
    this.force = {};
    let fv = [];
    try { fv = await (await fetch('data/matte/force.json')).json(); } catch (e) { fv = []; }
    await Promise.all(fv.map(async n => {
      try {
        const t = await loader.loadAsync(`data/matte/force_${n}.png`);
        t.colorSpace = THREE.NoColorSpace; t.generateMipmaps = false; t.minFilter = t.magFilter = THREE.LinearFilter;
        this.force[n] = t;
      } catch (e) { console.warn('matte: no force mask for view', n); }
    }));
    await Promise.all(Object.keys(VIEWS).map(async k => {
      const n = +k;
      try {
        const t = await loader.loadAsync(`data/matte/bg_${n}.png`);
        t.colorSpace = THREE.NoColorSpace;     // raw sRGB values in, raw out (composited after the grade)
        t.generateMipmaps = false; t.minFilter = t.magFilter = THREE.NearestFilter;
        this.tex[n] = t;
      } catch (e) { console.warn('matte: no bg for view', n); return; }
      applyView(cam, VIEWS[n]); cam.updateMatrixWorld();
      const ty = Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2);
      this.proj[n] = {
        rot: new THREE.Matrix3().setFromMatrix4(cam.matrixWorldInverse),
        pos: cam.position.clone(), tan: new THREE.Vector2(ty * REF_W / REF_H, ty),
        ramp: MATTE_RAMP[n] || MATTE_RAMP.default,
      };
    }));
  }

  // n = 0: off. feather: px of fade inside the ref frame border (0 for the exact ref camera; ~120 for moving cameras).
  // force: weight of the force-far mask (1 for the stills; 0 for moving cameras, where it would slide on our rock)
  set(n, strength = 1, feather = 0, force = 1) {
    this.view = this.tex[n] ? n : 0; this.strength = strength; this.feather = feather; this.forceW = force;
  }
  get on() { return this.view > 0 && this.strength > 0; }

  setSize(w, h) { this.accRT.setSize(w, h); }

  clear() {
    this.valid = false;
    const r = this.renderer;
    r.setRenderTarget(this.accRT); r.setClearColor(0x000000, 0); r.clear(); r.setClearColor(0x000000, 1);
  }

  // one sub-frame (camera as rendered, possibly jittered) with weight w; sceneRT's depth must be this sub-frame's
  sub(wt) {
    if (!this.on) return;
    const cam = this.camera, P = this.proj[this.view], u = this.subMat.uniforms;
    const ty = Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2) / cam.zoom;
    u.tDepth.value = this.post.sceneRT.depthTexture; u.tRef.value = this.tex[this.view];
    u.uLogF.value = Math.log2(cam.far + 1);
    u.uTan.value.set(ty * cam.aspect, ty);
    const camRot = new THREE.Matrix3().setFromMatrix4(cam.matrixWorld);
    u.uM.value.copy(P.rot).multiply(camRot);
    u.uD.value.setFromMatrixPosition(cam.matrixWorld).sub(P.pos).applyMatrix3(P.rot);
    u.uPTan.value.copy(P.tan);
    u.uRamp.value.set(P.ramp[0], P.ramp[1]);
    u.uFeather.value = this.feather;
    u.uW.value = wt * this.strength;
    const F = this.useForce ? this.force[this.view] : null;     // APP.matte.useForce = false: depth farness only
    u.tForce.value = F || this.tex[this.view]; u.uForce.value = F ? this.forceW : 0;
    u.uCamY.value = cam.matrixWorld.elements[13];
    u.uProxyY.value = this.proxy ? CLOUDS.top : -1e7;    // APP.matte.proxy = false: project onto our depth only
    u.uUpV.value.set(camRot.elements[1], camRot.elements[4], camRot.elements[7]);   // world-y row of the camera rotation
    this.post.pass(this.subMat, this.accRT);
    this.valid = true;
  }

  // before the composite: live single frames (render()) compute their matte now; snapshots (gradetune) get none
  prep(hdrRT) {
    const p = this.post;
    if (hdrRT === p.accumRT) return this.valid;
    if (hdrRT === p.sceneRT || hdrRT === p.cloudRT) { this.clear(); this.sub(1); return this.valid; }
    return false;
  }

  composite(target, fade) {
    const mat = this.showW ? this.compW : this.compMat;
    mat.uniforms.tAcc.value = this.accRT.texture; mat.uniforms.uFade.value = fade; mat.uniforms.uShowW.value = this.showW ? 1 : 0;
    this.post.pass(mat, target);
  }
}
