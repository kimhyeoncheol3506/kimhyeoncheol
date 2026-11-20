# Library reference

Preview sheets: `library_characters.jpg`, `library_sets.jpg`.

## Moods (`"mood"`)
`day`, `interior`, `night`, `dream`, `golden`, `sunset`, `dawn`. Every set works in every mood. Practicals
(lamps, lit windows, screens) glow automatically in `night`.

## Sets (`"set"`): placement hints in set pixels (frame 1080x1920 = `h` 1920)

| set | what | actors stand at | notes |
|---|---|---|---|
| `street` | suburban street, houses both sides, lamps, fences, hydrants, wires | y 1550-1800, z 1.0 | night = lit windows + wet-cobble lamp reflections |
| `kitchen` | farmhouse kitchen: sage plaster + white tile, wood floor, centred window over the sink, terracotta cabinets, black range with copper hood, plate dresser on the left wall, copper pans, rattan pendant, striped runner | y 1500-1700, z 1.0 | near plane = table corner |
| `office` | brick office, blinds (noir stripes), sales bar chart, cork board with notes, desk, monitor, brass desk bell, rubber stamp | behind desk y 1300 z 1.2; in front y 1700 z 0.95 | |
| `shop_counter` | general store shelves (blurred), counter with a glowing brass balance scale (coins vs a loaf, "LOT 8" tag), coins | behind counter y 1330, z 1.6 | explanation close-ups |
| `planet_shop` | space shop: planet shelves with price tags, "PLANETS" sign, counter, register, Earth with "99¢" tag | seller x 640 y 1290 z 1.04; customer y 1720 z 0.95 | `earth`=(300,1160), tag=(450,1255) |
| `ship_deck` | wooden deck in perspective, rails, mast and sails, barrels, crate, wheel, sea + island | y 1500-1800, z 1.0 | |
| `desert_rails` | railway to the horizon, hoodoo rock towers, low mesas, grey stone ballast, cacti, wooden water tower | y 1600-2000, z 0.98 | low wide close-ups work best |
| `castle_hall` | stone hall, three lancet windows with god-rays, arch, green key pennants, oak chair of state, green runner, torches, chandelier | y 1450-1700, z 1.0 | chair=(540,1150) |
| `field` | meadow with a dirt road bending away left, lone oak with a rope swing, hay bales, farmhouse + silo, hot-air balloon, low sun right | y 1900-2100 z 0.9 (further up the road the ground hides the feet) | good for calm `dawn`/`sunset` scenes |
| `town_top` | top-down tilted view of a river town: street grid, winding river with plank bridges, gabled houses, off-centre market square with striped stalls, trees | small figures in the square (~(300, 1300)), scale 0.28, z 0.92 | layouts, "the whole town" |
| `prehistoric` | valley with a smoking volcano, long-necked dinosaur on the horizon, two flying reptiles, giant ferns and cycads, river, tar pit, boulders, rock outcrop with a cave mouth and cave paintings, campfire (glows in sunset/night/dawn) | y 1600-1750, z 1.0 (horizon is low, y 1230) | fire=(3.6 m, 12 m) world |

To add a set: write `def myset(mood): return [(name, plane_z, painter(cv), opts), ...], meta` in a module and add
it to a registry (`sets.REGISTRY`, `outdoor.py` or `interiors.REGISTRY`). Paint with the helpers in
`setkit.py`, `textures.py` and `props.py`. Put the subject plane at z = 1.0, far planes at 2-14, the sky at ~30
(`grade=False`), and a blurred near plane at 0.55-0.65 (`blur=8-14`). Register light sources in an `E` list and
re-draw them in `lights=` so they glow after the mood grade. Outdoor sets use `Ground` (a pinhole floor in metres)
and depth bands (see `outdoor.py`).

## Characters (`"type"`)
`worker` (hard hat, rust shirt, overalls, blue bandana, wrench), `boss` (slick grey hair, moustache, bottle-green double-breasted suit, mustard tie, watch
chain, mug), `cop` (light-blue shirt, peaked cap with silver shield, pockets, belt, silver badge, radio, baton), `cook` (toque, double-breasted
jacket, neckerchief, apron, ladle), `knight` (open-face brimmed kettle hat, plate, red tabard with white cross, sword),
`king` (crown with gems, ermine collar, robe, medal chain, beard, sceptre), `scientist` (wild white hair, round
glasses, lab coat, pens, flask), `cashier` (mustard visor, blue polo, mustard apron, name tag, scanner), `sailor` (round cap with
ribbons, striped shirt, sailor collar, telescope), `caveman` (messy black hair, one-shoulder spotted fur tunic, wooden club), `kid` (propeller cap, star tee, shorts, balloon, smaller),
`alien` (green head, bobbing antennae).

Overrides per actor: `torso`, `accent`, `skin`, `hat`, `hair`.

**Poses:** `stand`, `walk`, `run`, `point`, `shrug`, `arms_crossed`, `hips`, `hold`, `think`, `wave`, `cheer`, `sit`.
**Expressions:** `neutral`, `smug`, `angry` (red face + steam), `shocked`, `laughing`, `scared` (sweat drop), `sad`,
`sly`, `happy`, `deadpan`.
Always on: blinks, breathing, hat/plume/antenna/ribbon sway, scarf flutter. `talk: true` flaps the mouth.
`look: [x, y]` moves the pupils (-1..1).

## Hold props (`"hold"`)
`earth`, `planet:gas|red|ringed|shiny|moon|purple|earth`, `sign:TEXT`, `tag:TEXT`, `newspaper:LINE1|LINE2`.

## In-world explanation props (`props.py`, for sets)
`planet`, `price_tag`, `register`, `newspaper`, `sign_board`, `counter_display` (chalk number slate),
`cross_section` (ground cut-away), `calendar_page`; in `setkit.py`: `calendar`, `wall_clock`, `frame_pic`,
`crate`, `plant_pot`, `window`, `door`, `house`, `lamp_post`, `tree`, `foliage`, `cactus`, `rock`, `mesa`, `cloud`.

## Frame shorthand (`"frame"`)
`[cx, cy, h]`, `"wide"`, `"two"`/`"all"` (fits the cast), `"<id>"` (medium), `"<id>:face"`, `"<id>:full"`.
Camera roll per key: `"roll": 2.0` (degrees; costs ~0.2 s per frame, use sparingly).

### Non-human cast

`"type": "dino"`: a small friendly two-legged dinosaur (round body, cream belly, orange back plates, big eye). Cast fields: `x`, `y`, `scale` (0.6-0.9 next to a character), `z`, `dir`, `expr` (`happy` or `shocked`), `torso` (body colour). No poses; it breathes, blinks and wags its tail on its own.

### Captions-only Shorts

No voice-over: `python t2d.py silent PROJECT --script script.txt --duration 15` writes a silent `voice.wav`, reading-pace timings (~2.3 words/s, 0.35 s after sentences) and `words.json`. `join` skips loudness normalisation when the track peaks below -70 dBFS; `check` prints "silent track, loudness not applicable".
