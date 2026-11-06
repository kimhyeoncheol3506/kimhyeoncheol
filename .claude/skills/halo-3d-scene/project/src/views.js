// Reference camera matches. Authored in "ref frame" (origin ring centre, y=0 deck top, bridges on +/-X,
// camera front at +Z looking -Z toward the glow) in units of the ring outer radius, then mapped to world:
// world X = ref Z (west = -X is toward the sun), world Z = -ref X, world Y = DECK_Y + y*R.
import * as THREE from 'three';
import { DECK_Y, RING, ringYaw } from './config.js';

const R = RING.Ro;
export function refToWorld([x, y, z]) {
  const v = new THREE.Vector3(x * R, y * R, z * R).applyAxisAngle(new THREE.Vector3(0, 1, 0), ringYaw());
  v.y += DECK_Y;
  return v;
}

// The AI references are not perspective-consistent (ring ellipse says ~9-13 deg elevation, horizon says ~2-5).
// Hero cameras sit ~9-12 deg above the ring (so the void and inner terrace read as in the refs) and aim low enough
// to keep the ring in the upper third with the glow band still in frame.
export const VIEWS = {
  1: { pos: [-0.50, -0.10, 0.66], tgt: [-0.84, -0.28, -0.80], fov: 58 },
  // r6 camera pass: 2, 4-9, 11 refit (CPU Nelder-Mead on the ref ring outline: outer roof edge l/r/t/b, front-face
  // bottom, inner edge / void top; fov kept); dips re-solved so the far skyline stays where it was in m7
  2: { pos: [-0.777, 1.282, 5.792], tgt: [-0.063, -0.853, 0.111], fov: 36, dip: 0.122, sky: [1.1, 0.03, 4, 0] },
  3: { pos: [0.30, -0.31, 1.45], tgt: [0, -0.05, 0], fov: 57 },
  4: { pos: [0, 0.627, 6.62], tgt: [0.001, -0.271, -0.128], fov: 14, dip: 0.071, sky: [2.1, 0.03, -3, -0.004] },
  5: { pos: [-1.379, 0.606, 3.069], tgt: [-0.07, -0.394, -0.121], fov: 28, dip: 0.151, sky: [1.3, 0.03, 22, 0.003] },
  6: { pos: [0.83, 0.483, 3.047], tgt: [-0.059, -0.421, -0.312], fov: 28, dip: 0.125, sky: [1.3, 0.03, -11, 0] },
  7: { pos: [0.003, 0.885, 3.901], tgt: [-0.014, -0.333, 0.03], fov: 25, dip: 0.185, sky: [1.6, 0.03, -16, 0] },
  8: { pos: [-0.081, 2.031, 1.115], tgt: [-0.026, -0.006, 0.249], fov: 50 },
  9: { pos: [-0.115, -1.104, 2.176], tgt: [-0.018, -0.211, 0.152], fov: 43 },
  10: { pos: [-1.6, 0.18, 0.6], tgt: [-0.817, -0.1784, 0.0915], fov: 60 },
  11: { pos: [-0.702, 0.907, 3.74], tgt: [0.036, -0.456, -0.342], fov: 25, dip: 0.167, sky: [1.6, 0.03, 16, -0.006] },
};

export function applyView(camera, v) {
  camera.position.copy(refToWorld(v.pos));
  camera.up.set(0, 1, 0);
  camera.lookAt(refToWorld(v.tgt));
  camera.fov = v.fov;
  camera.updateProjectionMatrix();
}
