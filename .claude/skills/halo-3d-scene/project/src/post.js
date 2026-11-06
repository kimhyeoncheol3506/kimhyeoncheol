// HDR post pipeline: scene RT (MSAA + depth) -> [clouds] -> bloom pyramid -> tone curve + grade.
import * as THREE from 'three';

const fsVert = /* glsl */ `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
// NaN / Inf test on the exponent bits (D3D compiles isnan() away under fast math)
const FINITE = /* glsl */ `vec3 finite3(vec3 c){ uvec3 e = floatBitsToUint(c) & 0x7f800000u; return any(equal(e, uvec3(0x7f800000u))) ? vec3(0.0) : c; }`;

function fsQuad(material) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
  m.frustumCulled = false;
  const s = new THREE.Scene(); s.add(m);
  return { scene: s, mesh: m, cam: new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1) };
}

export class Post {
  constructor(renderer, w, h) {
    this.renderer = renderer;
    this.params = {
      // bloom: only HDR above bloomThreshold (soft knee) glows, added on top; grain is dither-level (refs are clean)
      // grade: exposure / white balance / saturation from tools/gradetune.mjs on m8 (MASK=mw: the 3D part only, the
      // matte background is the reference itself); contrast and lift pushed past the percentile match (user: much
      // darker shadows, brighter lights)
      // (r9 film, matte off: the free-flight frames sat at L* p10 21 / p99 65 vs the refs' 15 / 72 - exposure 0.66 -> 0.69,
      // contrast 1.05, toe 0.06 pulls the dark-mid band (sRGB luma 0.1-0.4) down while the lift keeps the blacks at the
      // refs' p2 ~8, shoulder 0.5 -> 0.6 lets the glow and lamps reach higher)
      exposure: 0.69, bloomStrength: 0.08, bloomRadius: 0.6, bloomThreshold: 1.5, vignette: 0.12, grain: 0.005,
      saturation: 1.18, contrast: 1.05, lift: new THREE.Vector3(0.03, 0.036, 0.048), warmHi: 0.0,
      toe: 0.06, shoulder: 0.6, clarity: 0.22, wb: new THREE.Vector3(1.12, 1, 1.08),
    };
    this.setSize(w, h);
    this.downMat = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null }, uTexel: { value: new THREE.Vector2() }, uPrefilter: { value: 0 }, uThreshold: { value: 1.5 } },
      vertexShader: fsVert,
      fragmentShader: /* glsl */ `
        uniform sampler2D tSrc; uniform vec2 uTexel; uniform int uPrefilter; uniform float uThreshold; varying vec2 vUv;
        ${FINITE}
        vec3 s(vec2 o){ return max(finite3(texture2D(tSrc, vUv + o * uTexel).rgb), 0.0); }
        void main(){
          // 13-tap downsample (CoD AW)
          vec3 a = s(vec2(-2,-2)), b = s(vec2(0,-2)), c = s(vec2(2,-2));
          vec3 d = s(vec2(-1,-1)), e = s(vec2(1,-1));
          vec3 f = s(vec2(-2,0)), g = s(vec2(0,0)), h = s(vec2(2,0));
          vec3 i = s(vec2(-1,1)), j = s(vec2(1,1));
          vec3 k = s(vec2(-2,2)), l = s(vec2(0,2)), m = s(vec2(2,2));
          vec3 col = (d + e + i + j) * 0.125 + (a + c + k + m) * 0.03125 + (b + f + h + l) * 0.0625 + g * 0.125;
          if (uPrefilter == 1) {
            float lum = dot(col, vec3(0.2126,0.7152,0.0722)); col *= 1.0 / (1.0 + lum * 0.02); col = min(col, vec3(400.0));
            // soft-knee threshold: only emitters / hot speculars bloom
            float br = max(col.r, max(col.g, col.b)), kn = uThreshold * 0.5;
            float sq = clamp(br - uThreshold + kn, 0.0, 2.0 * kn); sq = sq * sq / (4.0 * kn + 1e-4);
            col *= max(sq, br - uThreshold) / max(br, 1e-4);
          }
          gl_FragColor = vec4(col, 1.0);
        }`,
      depthTest: false, depthWrite: false,
    });
    this.upMat = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null }, tPrev: { value: null }, uTexel: { value: new THREE.Vector2() }, uRadius: { value: 0.85 } },
      vertexShader: fsVert,
      fragmentShader: /* glsl */ `
        uniform sampler2D tSrc, tPrev; uniform vec2 uTexel; uniform float uRadius; varying vec2 vUv;
        void main(){
          vec2 t = uTexel;
          vec3 c = texture2D(tPrev, vUv + vec2(-t.x, -t.y)).rgb + texture2D(tPrev, vUv + vec2(0, -t.y)).rgb * 2.0 + texture2D(tPrev, vUv + vec2(t.x, -t.y)).rgb
                 + texture2D(tPrev, vUv + vec2(-t.x, 0)).rgb * 2.0 + texture2D(tPrev, vUv).rgb * 4.0 + texture2D(tPrev, vUv + vec2(t.x, 0)).rgb * 2.0
                 + texture2D(tPrev, vUv + vec2(-t.x, t.y)).rgb + texture2D(tPrev, vUv + vec2(0, t.y)).rgb * 2.0 + texture2D(tPrev, vUv + vec2(t.x, t.y)).rgb;
          c /= 16.0;
          gl_FragColor = vec4(texture2D(tSrc, vUv).rgb + c * uRadius, 1.0);
        }`,
      depthTest: false, depthWrite: false,
    });
    this.finalMat = new THREE.ShaderMaterial({
      uniforms: {
        tScene: { value: null }, tBloom: { value: null }, tBlur: { value: null }, uClarity: { value: 0.22 }, uTime: { value: 0 },
        uExposure: { value: 1 }, uBloom: { value: 0.05 }, uVignette: { value: 0.2 }, uGrain: { value: 0.03 },
        uSat: { value: 1 }, uContrast: { value: 1 }, uLift: { value: new THREE.Vector3() }, uWarmHi: { value: 0 },
        uShoulder: { value: 0.55 }, uToe: { value: 0 }, uRes: { value: new THREE.Vector2() }, uFade: { value: 1 }, uWB: { value: new THREE.Vector3(1, 1, 1) },
      },
      vertexShader: fsVert,
      fragmentShader: /* glsl */ `
        uniform sampler2D tScene, tBloom, tBlur; uniform float uClarity; uniform float uTime, uExposure, uBloom, uVignette, uGrain, uSat, uContrast, uWarmHi, uShoulder, uToe;
        uniform vec3 uLift, uWB; uniform vec2 uRes; uniform float uFade; varying vec2 vUv;
        ${FINITE}
        float h12(vec2 p){ vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
        float sh(float x){ float a = uShoulder; return x < a ? x : a + (1.0 - a) * (1.0 - exp(-(x - a) / (1.0 - a))); }
        vec3 tone(vec3 c){
          // per-channel shoulder, then blend toward luminance-preserving version to keep hue on bright lamps
          vec3 p = vec3(sh(c.r), sh(c.g), sh(c.b));
          float L = dot(c, vec3(0.2126, 0.7152, 0.0722));
          float Lt = sh(L);
          vec3 q = c * (Lt / max(L, 1e-5));
          q = q / max(1.0, max(q.r, max(q.g, q.b)));
          return mix(p, q, 0.65);   // mostly hue-preserving: hot lamps stay amber instead of clipping to cream
        }
        vec3 lin2srgb(vec3 c){ return mix(c * 12.92, 1.055 * pow(c, vec3(1.0/2.4)) - 0.055, step(0.0031308, c)); }
        void main(){
          vec3 c = texture2D(tScene, vUv).rgb;
          c = finite3(c);
          vec3 b = texture2D(tBloom, vUv).rgb;
          // clarity: boost luminance relative to a wide local average (HDR-photo look)
          float lc = dot(c, vec3(0.2126, 0.7152, 0.0722));
          float lb = dot(texture2D(tBlur, vUv).rgb, vec3(0.2126, 0.7152, 0.0722));
          float ratio = clamp(log2((lc + 0.004) / (lb + 0.004)), -2.5, 2.5);
          c *= exp2(ratio * uClarity * smoothstep(0.0, 0.03, lc) * (1.0 - smoothstep(1.5, 6.0, lc)));
          c += b * uBloom;
          c *= uExposure * uWB;   // white balance in linear HDR
          // vignette (in linear, before tone)
          vec2 q = vUv - 0.5; q.x *= uRes.x / uRes.y;
          float v = 1.0 - uVignette * smoothstep(0.25, 1.05, length(q) * 1.15);
          c *= v;
          c = tone(c);
          // grade: contrast around mid grey (in sRGB-ish space), saturation, lift, warm highlights
          vec3 s = lin2srgb(clamp(c, 0.0, 1.0));
          float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
          s = mix(vec3(l), s, uSat);
          s = (s - 0.5) * uContrast + 0.5;
          s += uLift * (1.0 - smoothstep(0.0, 0.5, l));
          s += vec3(1.0, 0.6, 0.2) * uWarmHi * smoothstep(0.6, 1.0, l);
          // toe: darken the dark-mid band (luma ~0.06-0.45, most at 0.2), hue-preserving; blacks and mids stay put
          float lt = dot(s, vec3(0.2126, 0.7152, 0.0722));
          s *= max(0.0, lt - uToe * smoothstep(0.06, 0.2, lt) * (1.0 - smoothstep(0.2, 0.45, lt))) / max(lt, 1e-5);
          // film grain
          float g = h12(gl_FragCoord.xy + fract(uTime * 7.13) * 917.0) - 0.5;
          s += g * uGrain * (0.6 + 0.4 * (1.0 - l));
          gl_FragColor = vec4(clamp(s * uFade, 0.0, 1.0), 1.0);
        }`,
      depthTest: false, depthWrite: false,
    });
    this.accMat = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null }, uW: { value: 1 } }, vertexShader: fsVert,
      // NaN / Inf from any material would bloom into a one-frame white disc: drop such samples
      fragmentShader: `uniform sampler2D tSrc; uniform float uW; varying vec2 vUv; ${FINITE}
        void main(){ vec3 c = max(finite3(texture2D(tSrc, vUv).rgb), 0.0);
          // firefly clamp per sub-frame (single-pixel glints on glass / steel), hue kept
          float l = dot(c, vec3(0.2126, 0.7152, 0.0722)); c *= min(1.0, 32.0 / max(l, 1e-4));
          gl_FragColor = vec4(c * uW, 1.0); }`,
      depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending, transparent: true,
    });
    this.quad = fsQuad(this.finalMat);
  }

  setSize(w, h) {
    this.w = w; this.h = h;
    const dt = new THREE.DepthTexture(w, h, THREE.FloatType);
    if (this.sceneRT) { this.sceneRT.dispose(); this.cloudRT.dispose(); this.mips.forEach(m => m.dispose()); this.ups.forEach(m => m.dispose()); }
    this.sceneRT = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: 4, depthTexture: dt, depthBuffer: true });
    this.sceneRT.texture.minFilter = this.sceneRT.texture.magFilter = THREE.LinearFilter;
    this.cloudRT = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, depthBuffer: false });
    if (this.accumRT) this.accumRT.dispose();
    this.accumRT = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, depthBuffer: false });
    this.mips = []; this.ups = [];
    let mw = w, mh = h;
    for (let i = 0; i < 7; i++) {
      mw = Math.max(1, mw >> 1); mh = Math.max(1, mh >> 1);
      const o = { type: THREE.HalfFloatType, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter };
      this.mips.push(new THREE.WebGLRenderTarget(mw, mh, o));
      this.ups.push(new THREE.WebGLRenderTarget(mw, mh, o));
    }
  }

  pass(mat, target) {
    this.quad.mesh.material = mat;
    this.renderer.setRenderTarget(target);
    this.renderer.render(this.quad.scene, this.quad.cam);
  }

  bloom(src) {
    let prev = src;
    for (let i = 0; i < this.mips.length; i++) {
      this.downMat.uniforms.tSrc.value = prev.texture;
      this.downMat.uniforms.uTexel.value.set(1 / prev.width, 1 / prev.height);
      this.downMat.uniforms.uPrefilter.value = i === 0 ? 1 : 0;
      this.downMat.uniforms.uThreshold.value = this.params.bloomThreshold;
      this.pass(this.downMat, this.mips[i]);
      prev = this.mips[i];
    }
    let up = this.mips[this.mips.length - 1];
    for (let i = this.mips.length - 2; i >= 0; i--) {
      this.upMat.uniforms.tSrc.value = this.mips[i].texture;
      this.upMat.uniforms.tPrev.value = up.texture;
      this.upMat.uniforms.uTexel.value.set(1 / up.width, 1 / up.height);
      this.upMat.uniforms.uRadius.value = this.params.bloomRadius;
      this.pass(this.upMat, this.ups[i]);
      up = this.ups[i];
    }
    return up;
  }

  clearAccum() {
    this.renderer.setRenderTarget(this.accumRT); this.renderer.setClearColor(0x000000, 1); this.renderer.clear();
    if (this.matte) this.matte.clear();   // MATTE: accumulates its weight per sub-frame like the colour (src/matte.js)
  }
  accumulate(src, w) {
    this.accMat.uniforms.tSrc.value = src.texture; this.accMat.uniforms.uW.value = w; this.pass(this.accMat, this.accumRT);
    if (this.matte) this.matte.sub(w);    // MATTE: this sub-frame's depth + (jittered) camera
  }

  // hdrRT: final HDR image (after clouds). target: null = screen
  finish(hdrRT, time, target = null, fade = 1) {
    const bl = this.bloom(hdrRT);
    const u = this.finalMat.uniforms, p = this.params;
    u.tScene.value = hdrRT.texture; u.tBloom.value = bl.texture; u.tBlur.value = this.mips[3].texture; u.uClarity.value = p.clarity; u.uTime.value = time;
    u.uExposure.value = p.exposure; u.uBloom.value = p.bloomStrength; u.uVignette.value = p.vignette; u.uGrain.value = p.grain;
    u.uSat.value = p.saturation; u.uContrast.value = p.contrast; u.uLift.value.copy(p.lift); u.uWarmHi.value = p.warmHi;
    u.uShoulder.value = p.shoulder; u.uToe.value = p.toe; u.uRes.value.set(this.w, this.h); u.uFade.value = fade; u.uWB.value.copy(p.wb);
    // MATTE: far regions = the camera-projected reference, composited over the graded image (src/matte.js)
    const matte = this.matte && this.matte.on && this.matte.prep(hdrRT);
    this.pass(this.finalMat, target);
    if (matte) this.matte.composite(target, fade);
  }
}
