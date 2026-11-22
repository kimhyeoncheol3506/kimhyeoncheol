# The look and the script

House rules for the toon2d look, written as target numbers. The checks in `checks.py` and `qa.py` test these numbers.

## Characters
1. Big round off-white head (~42 % of the figure), thick plum ink outline, no nose or ears.
2. Face = solid eyes + thick brows that act + small mouth, set low with a big clean forehead.
3. Thin ink limbs with bent knees, mitten hands, small shoes. Costume torso in flat colours with real detail
   (collar, buttons, pockets, belts, suspenders, scarves, aprons) and a shade side + mood-coloured rim light.
4. The hat or hair makes the silhouette. Each role must read as a black shape.
5. Comic extras (sweat drop, steam puffs, red face) carry the overacting.
6. Characters take the scene colour: lilac-blue at night, warm by a lamp, backlit at sunset.

## Sets
1. Every surface has a material: wood grain, bricks, tiles, gravel, shingles, siding, wallpaper, stone.
2. Real perspective (pinhole ground, receding walls) and a low, wide lens. Something passes close to the lens.
3. Dressed with 10-30 props. Skies always have clouds with form, a sun/moon halo or stars.
4. 4-6 depth planes: blurred near foreground, sharp subject, hazy far background.
5. Each location owns a hue. A monochrome Short looks cheap.

## Light = act structure
| Phase | Mood | Recipe |
|---|---|---|
| Hook / setup | `day`, `interior` | clean daylight or warm tungsten, cool sky fill |
| Tension / secret / waiting | `night` | deep ultramarine ambient (not black) + warm practicals with bloom |
| Memory / fantasy | `dream` | over-bright or magenta-pink |
| Explanation | `golden` | golden glowing close-up of the key object, shallow depth of field |
| Ending | `sunset`, `dawn` | backlight, long shadows toward camera |

Tone targets (checked by `checks.py`): L* mean ~49 (43-58), darkest 1 % at L* ~12 (lifted plum blacks
`#2f232e`, only ink is black), contrast L* std ~20, shadows magenta-violet, highlights warm, corners ~0.8 of
the centre brightness. Brightness dips in the middle (night act) and chroma rises toward the end.

## Camera
* About 56 framing beats per minute (one every ~0.86 s, ~4 spoken words), essentially no hard cuts.
* Moves of ~19 frames, symmetric ease-in-out, never fully still (a slow push between moves).
* Push-in about 2x as often as pull-out; small shakes on impacts; motion blur on fast moves.
* The first second shows an extreme close-up of the key object. Use top-down views for layouts and
  cross-sections for the hidden mechanism.
* Faster in the first 40 %, ~25 % slower after. The explanation and the payoff get the longest holds.
* Cross-dissolves only for time jumps and light/act changes.

## Captions
1-2 words, switched on each word onset with a quick small pop, lowercase as spoken with punctuation kept, white
heavy sans with a thin dark outline and a soft shadow, centred at 70 % height, inside the safe zone.

## Script (micro-fable, 30-70 s, ~220 words/min, voice from frame 0)
1. **Hook (first 3.5 s):** one concrete, strange sentence stated as fact: a strange act with stakes, a paradox,
   or "impossible, but worse". Avoid a plain question.
2. **Context:** "You see, ..." or straight into the scene.
3. **Escalation (10-60 %):** 3-5 beats with "But", "So,", "Then", time jumps; side characters mock or pressure.
4. **Turn (60-90 %):** "You see," + the mechanism in 1-3 sentences, ideally an everyday second-person analogy.
5. **Payoff:** the twist is the last sentence, short; a callback to the hook works well. ~0.7 s of picture after.
Devices: rule of three in short sentences, deadpan quoted dialogue, understatement, literalised figures of speech.
Audio: voice compressed, music bed ~14 dB under the voice, master -14 LUFS.
