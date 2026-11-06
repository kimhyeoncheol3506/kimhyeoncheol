// Photographic material maps (CC0, Poly Haven, 2k) from data/tex/<id>/{diff,nor,rough,ao,disp}.jpg.
// diff is sRGB, the others linear data; all tile (RepeatWrapping) with trilinear mips + max anisotropy.
// Usage: const rock = await loadTex('marble_cliff_03'); material.uniforms.tRockDiff = { value: rock.diff };
// Available sets: marble_cliff_03, marble_cliff_05, cliff_side, dark_rock_02, rock_face, rock_face_03, rock_wall_02
// (rock), snow_01, snow_02, snow_field_aerial (snow), concrete_wall_006, concrete_slab_wall_02, concrete_panels.
import * as THREE from 'three';

const cache = new Map();
const loader = new THREE.TextureLoader();

export function loadTex(id, maps = ['diff', 'nor', 'rough', 'ao'], aniso = 8) {
  const key = id + ':' + maps.join(',');
  if (cache.has(key)) return cache.get(key);
  const p = Promise.all(maps.map(m => loader.loadAsync(`./data/tex/${id}/${m}.jpg`).then(t => {
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.colorSpace = m === 'diff' ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    t.anisotropy = aniso;
    t.minFilter = THREE.LinearMipmapLinearFilter;
    t.generateMipmaps = true;
    t.needsUpdate = true;
    return [m, t];
  }))).then(Object.fromEntries);
  cache.set(key, p);
  return p;
}
