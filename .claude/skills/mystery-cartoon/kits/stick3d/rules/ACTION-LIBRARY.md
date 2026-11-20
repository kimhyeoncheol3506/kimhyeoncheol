# ACTION LIBRARY (what exists; extend and log new entries)
## Implemented in engine/src/style/puppet.ts
- Pose params: mood (smile, grin, laugh, shock, worry, gulp, angry, deadpan), arms (down, up, hold, point, head, chest, box, shrug) + armK blend, nerv (tremble > 0.5, blush, brow twitch), sweat (sliding + flung drops), squash (+stretch/-squash), tilt, lookX, flip, hunch, air, walk phase + speed.
- Outfits: suit(+tie), blazer, leather, hoodie, shirt; hair: short, swept, bob, grey; glasses, badge, hat, shoe colour.
## Implemented patterns in examples/NvidiaDemo.tsx (copy, then adapt)
- Jump-back shock (anticipation squash -> stretch air -> landing squash), analytic stair hops + tumble + slide, walk-to-door-reach-open-walk-through, carrying a box (box follows hand with bob), crowd cheering behind a door with camera flashes, quake (throne shake with decay), counters, calendar circle draw, chart line draw.
## To build the first time they are needed (recipe)
- Throw: wind-up (arm back, squash) -> release at hand position -> projectile parabola p = p0 + v t + g t^2/2, spin, impact reaction.
- Pick up / put down: reach (arms: point to object height), grasp frame, object parented to hand with offset, release with settle.
- Eat / drink: object to mouth along arc, mouth opens (laugh/gulp mouth), chew bob 6 Hz small, swallow = throat dip + eyes close.
- Fight: stance, wind-up, strike with extended arm + stretch, hit-stop 3 frames, target knock-back with squash and tilt, cartoon-safe.
- Farm work: dig (arm arc + tool prop), sow (hand scatter + seed sprites), water (can tilt + droplet particles), growth (scale spring on sprout meshes timed to words), harvest (pull + carry basket).
- Fear / cry / celebrate: cower (hunch + tremble + arms head), tears particles, jump with arms up + confetti.
- Sit / stand: pose with chair contact, hips lower, legs bent (add `sit` leg mode to puppet.ts).
- Day->night: sun/moon on arc meshes + sky gradient plane + directional light colour + window glow; stars as small additive Glow sprites with twinkle; lamp glow turns on at dusk.
Add every new pose/prop here with its pose-param names and the scene where first used.
## Added in nvidia-v4 (engine/src/style/extra.tsx + puppet.ts)
- puppet.ts: `armR` / `armL` IK hand targets ([x, y] in puppet-height units, x from body centre, y from feet) + `armRK` / `armLK` blend. Used for: sipping a mug, lifting a crown off the head, carrying it, pushing a domino, holding press cameras / phones.
- extra.tsx helpers: `Cam` (Catmull-Rom camera path, micro handheld <=0.004, impact shake decaying < 0.5 s, FOV kicks), `camAt`, `FaceGroup` + `hand()` (props that stay glued to a puppet's hand).
- extra.tsx props: Arrow3D, Extrude (any outlined polygon), Domino (pivots on its leading edge; chain rule: next starts when angle = asin(gap/h), rest angle = acos(th/spacing)), Globe, Crown, Throne, SpotCone, Curtain, Lectern, Building (lit windows), StreetLamp, StreetSign, Taxi, Hydrant, Bench, Bin, Barrier, PressCam, ChipStack, Card, Dice, HangLamp, Mug, Stars.
- Patterns in videos/NvidiaV4.tsx: cable snap + falling arrow spearing the floor (parabolic drop + rotation + crack decal + debris arcs); mug released into a ballistic arc then a puddle; crown lift -> carry -> place with settle bounce; domino chain + winding small chain + hinged sign flipping up; 240 Hz crown physics sliding off a shaking throne and bouncing on a sphere; whip transition (translateX + blur).
