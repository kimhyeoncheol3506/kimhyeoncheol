import * as THREE from 'three';
import { NOISE, ATMOS } from './glsl/common.js';

// Round 8: the sky dome is a real photographic dusk sky (data/sky/sky.png + sky.json, baked by tools/skybake.mjs
// from a CC0 Poly Haven HDRI). createSky registers its texture as shared uniforms (uSkyTex, uSkyTexP) before the
// other materials are built, so glass and lake reflections and every other sky caller see the same sky. Until the
// texture is in (or if it fails to load) the analytic sky + procedural deck of common.js is drawn.
export function createSky(shared) {
  const blank = new THREE.DataTexture(new Uint8Array([128, 128, 128, 255]), 1, 1);
  blank.needsUpdate = true;
  shared.uniforms.uSkyTex = { value: blank };
  shared.uniforms.uSkyTexP = { value: new THREE.Vector4(0, 0, 1, -10 * Math.PI / 180) };
  shared.skyReady = loadSky(shared).catch(e => console.warn('sky: photographic sky not loaded, analytic fallback', e));
  // the capture tools await APP.ready (main.js, set synchronously after this call): fold the sky load into it
  queueMicrotask(() => {
    const A = typeof window !== 'undefined' && window.APP;
    if (A && A.ready) A.ready = Promise.all([A.ready, shared.skyReady]).then(() => true);
  });

  const geo = new THREE.SphereGeometry(1, 64, 32);
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms: { ...shared.uniforms },
    vertexShader: /* glsl */ `
      #include <common>
      #include <logdepthbuf_pars_vertex>
      varying vec3 vDir;
      void main(){
        vDir = position;
        vec4 wp = modelMatrix * vec4(position, 1.0);
        gl_Position = projectionMatrix * viewMatrix * wp;
        #include <logdepthbuf_vertex>
      }`,
    fragmentShader: /* glsl */ `
      #include <common>
      #include <logdepthbuf_pars_fragment>
      ${NOISE}
      ${ATMOS}
      varying vec3 vDir;
      void main(){
        #include <logdepthbuf_fragment>
        vec3 d = normalize(vDir);
        // pixel footprint in sky space (zoom included) for the cloud rows' anti-aliased edges / octave fades
        gSkyPx = max(0.6 * length(fwidth(skyView(farDipDir(d)))), 2e-5);
        // photographic sky: screen-space gradients of its lookup (the azimuth wraps at due south / north: take the
        // short way round), so the mip / anisotropic footprint follows the pixel (no shimmer, no seam line)
        vec2 uv = skyUV(cameraPosition, d);
        vec2 dx = dFdx(uv), dy = dFdy(uv);
        dx.x -= floor(dx.x + 0.5); dy.x -= floor(dy.x + 0.5);
        // (pass 2) at the zenith the azimuth gradient blows up and picked the coarsest mip, the whole sky's average:
        // a dark dot at the pole. The bake makes the top rows uniform in azimuth, so a capped footprint is exact there
        dx.x = clamp(dx.x, -0.02, 0.02); dy.x = clamp(dy.x, -0.02, 0.02);
        gSkyDx = dx; gSkyDy = dy; gSkyGrad = 1.0;
        vec3 c = skyFull(cameraPosition, d);
        // subtle dither against banding
        c += (hash12(gl_FragCoord.xy) - 0.5) / 512.0;
        gl_FragColor = vec4(c, 1.0);
      }`,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.scale.setScalar(450000);
  mesh.frustumCulled = false;
  mesh.renderOrder = -10;
  mesh.onBeforeRender = (r, s, cam) => mesh.position.copy(cam.position);
  mesh.name = 'sky';
  return mesh;
}

async function loadSky(shared) {
  const meta = await (await fetch('./data/sky/sky.json')).json();
  const tex = await new THREE.TextureLoader().loadAsync('./data/sky/sky.png');
  tex.colorSpace = THREE.NoColorSpace;          // log-encoded data, decoded in skyPhoto
  tex.wrapS = THREE.RepeatWrapping;             // azimuth
  tex.wrapT = THREE.ClampToEdgeWrapping;
  tex.magFilter = THREE.LinearFilter;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  tex.generateMipmaps = true;
  tex.anisotropy = 16;                          // (clamped to the device maximum) near the zenith the rows converge
  tex.needsUpdate = true;
  shared.uniforms.uSkyTex.value = tex;
  shared.uniforms.uSkyTexP.value.set(1, meta.lmin, meta.lrange, meta.elBot * Math.PI / 180);
  shared.skyMeta = meta;
  return meta;
}
