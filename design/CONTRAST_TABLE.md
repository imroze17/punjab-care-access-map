# Measured Contrast Table — Phase 1

All ratios below were computed with the WCAG relative-luminance formula from
**rendered** `color` / effective `background-color` pairs read out of a live
Chromium session (`getComputedStyle`), not from the stylesheet source. Effective
background was resolved by walking up the ancestor chain past transparent values.

Measurement conditions: Chromium, 1440×900, 16px root, no page zoom, default
system font settings. Re-measure after any token change — `validate_p0.py` pins
the token values listed in `PINNED_TOKENS` precisely so this table cannot
silently go stale.

WCAG AA thresholds applied: **4.5:1** for normal text, **3:1** for large text
(≥24px, or ≥18.66px when bold) and for non-text UI boundaries.

## Interface text — after Phase 1

| Selector | Size | Weight | Pair | Ratio | AA |
|---|---:|---:|---|---:|---|
| `.brand h1` | 30px | 500 | `#FFFFFF` on `#173C2D` | 12.20:1 | PASS |
| `.brand p` | 15px | 400 | `#D5E8DC` on `#173C2D` | 9.53:1 | PASS |
| `.header-stat` | 14px | 400 | `#D5E8DC` on `#173C2D` | 9.53:1 | PASS |
| `.section-label` | 16px | 600 | `#59645F` on `#FFFFFF` | 6.15:1 | PASS |
| `.facility-name` | 18px | 500 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.facility-meta` | 15px | 400 | `#59645F` on `#FFFFFF` | 6.15:1 | PASS |
| `.p1-card-line` | 15px | 400 | `#59645F` on `#FFFFFF` | 6.15:1 | PASS |
| `.pill.private` | 14px | 600 | `#5F258E` on `#F1E6FB` | 8.15:1 | PASS |
| `.small-action` | 14px | 600 | `#246B52` on `#FFFFFF` | 6.36:1 | PASS |
| `.map-export span` | 14px | 600 | `#59645F` on `#F3F4F8` | 5.60:1 | PASS |
| `.map-export button` | 14px | 600 | `#246B52` on `#FFFFFF` | 6.36:1 | PASS |
| `.legend-title` | 14px | 600 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.legend-row` | 14px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.legend-explanation` | 14px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.metric span` | 14px | 400 | `#59645F` on `#FFFFFF` | 6.15:1 | PASS |
| `.metric strong` | 18px | 600 | `#246B52` on `#FFFFFF` | 6.36:1 | PASS |
| `.footer-note` | 14px | 400 | `#59645F` on `#F3F4F8` | 5.60:1 | PASS |
| `.region-check` | 15px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.control-row` | 16px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.active-context` | 15px | 400 | `#202522` on `#EBECF1` | 13.19:1 | PASS |
| `.p0-card-role` | 15px | 400 | `#59645F` on `#FFFFFF` | 6.15:1 | PASS |
| `.coverage-button` | 16px | 700 | `#2F5E49` on `#F8FBF9` | 7.15:1 | PASS |
| `.map-note` | 14px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.map-title h2` | 22px | 500 | `#202522` on `#F3F4F8` | 14.16:1 | PASS |
| `.filter-button.active` | 16px | 600 | `#246B52` on `#E3F2EC` | 5.51:1 | PASS |
| `.type-select` | 16px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `input[type=search]` | 16px | 400 | `#202522` on `#FFFFFF` | 15.57:1 | PASS |
| `.map-layer-details summary` | 16px | 800 | `#246B52` on `#FFFFFF` | 6.36:1 | PASS |
| `.p0-map-notice` | 16px | 700 | `#202522` on `#E3F2EC` | 13.47:1 | PASS |

**29 of 29 probed styles pass. Smallest rendered interface text: 14px.
Lowest passing ratio: 5.51:1.**

## The five failures this phase fixed

Measured on the pre-redesign build at commit `1b6bba8`:

| Selector | Before | After | Change made |
|---|---:|---:|---|
| `.metric span` | 3.81:1 @ 10.4px | 6.15:1 @ 14px | `#78867F` → `--color-text-secondary` |
| `.map-export span` | 3.85:1 @ 10.08px | 5.60:1 @ 14px | `#6F8178` → `--color-text-secondary` |
| `.section-label` | 3.94:1 @ 10.88px | 6.15:1 @ 16px | `#73847D` → `--color-text-secondary` |
| `.footer-note` | 4.09:1 @ 11.2px | 5.60:1 @ 14px | `#6D7C74` → `--color-text-secondary` |
| `.legend-title` | 4.15:1 @ 9.76px | 15.57:1 @ 14px | `#718077` → `--color-text`, opaque panel |

## Focus indicator — why blue was kept

Handoff §9.1 proposed a green focus ring. Measured against the surfaces it
actually touches:

| Adjacency | Pair | Ratio | Verdict |
|---|---|---:|---|
| Green ring on green button face | `#246B52` on `#246B52` | 1.00:1 | unusable |
| Proposed green ring vs button | `#246B52` on `#246B52` | 1.57:1 (vs page) | **FAIL 3:1** |
| Retained blue ring on white | `#073B9B` on `#FFFFFF` | 9.96:1 | PASS |
| Retained blue ring on page | `#073B9B` on `#F3F4F8` | 9.06:1 | PASS |
| Retained blue ring on its halo | `#073B9B` on `#DCEAFF` | 8.19:1 | PASS |
| Halo against green button | `#DCEAFF` on `#246B52` | 5.23:1 | PASS |

The indicator is `outline: 3px solid` at `outline-offset: 3px` plus a 5px
`box-shadow` halo, so the blue ring never sits on the green button face. Owner
approved retaining blue on 27 Oct 2026; recorded as an approved deviation in
`src/tokens.css`.

## Non-text boundaries

| Element | Pair | Ratio | Needs | Verdict |
|---|---|---:|---:|---|
| Control border | `#738078` on `#FFFFFF` | 4.13:1 | 3:1 | PASS |
| Switch off-state track | `#6D7A73` on `#FFFFFF` | 3.06:1 | 3:1 | PASS |

The previous input border `#CCD9D2` measured roughly 1.4:1 — §9.2 forbids a pale
divider being the only boundary of an actionable control, so all interactive
borders moved to `--color-control-border`.

## Data-encoding colours

Ownership tints are checked against their own backgrounds. Each is always paired
with a text label, so colour is never the sole carrier of meaning (§9.4).

| Claim | Pair | Ratio |
|---|---|---:|
| Government | `#164B85` on `#E5F0FC` | 7.65:1 |
| NGO / trust | `#91440C` on `#FFF0E3` | 6.20:1 |
| Private | `#5F258E` on `#F1E6FB` | 8.15:1 |
| Helpline | `#0F6570` on `#E1F4F5` | 5.92:1 |

## Not covered by this table

- Hover, pressed and disabled states beyond those listed
- SVG map geometry (district fills, region washes, river strokes, marker labels)
- Export PNG/PDF raster output
- Print stylesheet rendering
- Any Gurmukhi text (none is published)

These remain open for Phase 3 per the handoff's §15.1 testing requirements. No
WCAG certification is claimed from this table.
