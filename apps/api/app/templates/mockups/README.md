# Mockup Base Photos

Place base mockup photos in this directory. Each photo should be a high-resolution JPG
with a clean surface suitable for compositing a sticker design.

## Expected files

- `laptop_lid.jpg` — MacBook-style laptop lid, top-down or slight angle
- `water_bottle.jpg` — Reusable water bottle, clean background
- `mailer_box.jpg` — Cardboard mailer box, top-down
- `glass_jar.jpg` — Glass jar (candle, preserves), clean label area
- `journal_cover.jpg` — Notebook/journal cover, flat lay
- `phone_case.jpg` — Phone case, clean background
- `sticker_sheet.jpg` — Sticker sheet / backing paper, top-down

## Config format

Each mockup should have a corresponding `.json` file (e.g. `laptop_lid.json`):

```json
{
  "placement": {"x": 0.5, "y": 0.5},
  "scale": 0.3,
  "rotation": 0,
  "perspective": [[1,0,0],[0,1,0],[0,0,1]],
  "shadow_opacity": 0.2,
  "shadow_offset": {"x": 5, "y": 5}
}
```

These are sourced separately — do NOT generate them via Replicate.
