# UI/UX Redesign — Baseline Findings (§2.2 Developer Pre-work)

Captured: 27 October 2026
Build under test: commit `1b6bba8` ("Implement P1 and P2 map safeguards")
Method: `make build` → served `public/` at `http://127.0.0.1:4173/`, inspected in a real
Chromium session via CDP. Computed styles read from the live DOM; contrast ratios computed
from the **rendered** `color`/effective `background-color` pairs using the WCAG
relative-luminance formula.

Prior audit reference commit `5683f19` is 3 commits behind current `HEAD`. Several findings
in the handoff were written against that older state and are **already resolved** — those are
marked "already satisfied" below, per the §1.2 "Required: implement or demonstrate that the
current site already satisfies it" instruction.

---

## 1. Verified environment

| Item | Value |
|---|---|
| Pages source | `main` branch, `/docs` folder, `status: built`, HTTPS enforced |
| Build | `make check` → build + 2 unit tests + `validate_p0.py`, all pass |
| Build reproducibility | `git status` clean after `make build` — output is byte-reproducible from committed canonical data |
| Record count | 112 canonical, 112 runtime, 112 cards rendered in DOM |
| Districts | 22 district groups + 4 coverage records (1 multi-district, 3 statewide) |
| Node / Python | v22.22.3 / 3.9.6 local (CI uses 3.12) |

## 2. Typography — confirmed, and far wider than the handoff estimated

The handoff (§8.4) flagged only export text at `.63rem`/`.71rem` from the **retired**
`restore_reference_design.py`. The live build is worse: **17 of 17 probed text styles render
under 14px.** Measured in-browser at a 16px root:

| Selector | Rendered | Spec target (§8.3) |
|---|---:|---|
| `.legend-title` | 9.76px | 14–16px |
| `.pill` | 10.08px | compact but readable |
| `.map-export span` | 10.08px | 14–16px |
| `.metric span` | 10.40px | 14–15px |
| `.section-label` | 10.88px | 16px control label |
| `.legend-row` | 10.88px | 14–16px |
| `.facility-meta` | 11.04px | 14–15px |
| `.footer-note` | 11.20px | 14–15px |
| `.small-action` | 11.36px | 16px |
| `.map-export button` | 11.36px | 16px |
| `.active-context` | 11.68px | 14–15px |
| `.region-check` | 11.84px | 14–15px |
| `.p1-card-line` | 12.00px | 14–15px |
| `.p0-card-role` | 12.48px | 14–15px |
| `.coverage-button` | 12.48px | 16px |
| **`.facility-name`** | **12.64px** | **17–18px** |
| `.control-row` | 13.12px | 16px |

`.brand h1` renders 16.64px against a 26–30px target (§8.3).

**The single worst offender is `.facility-name` at 12.64px** — the service name is the primary
decision object in the whole directory and is currently smaller than this document's body text.

## 3. Contrast — 5 real AA failures on rendered pairs

Computed from live `color` / effective `background-color`. None of these qualify as WCAG
"large text" (all under 18.66px), so all need 4.5:1.

| Selector | Rendered pair | Ratio | Verdict |
|---|---|---:|---|
| `.metric span` | `#78867F` on `#FFFFFF` | **3.81:1** | FAIL |
| `.map-export span` | `#6F8178` on `#F8F7F2` | **3.85:1** | FAIL |
| `.section-label` | `#73847D` on `#FFFFFF` | **3.94:1** | FAIL |
| `.footer-note` | `#6D7C74` on `#F8F7F2` | **4.09:1** | FAIL |
| `.legend-title` | `#718077` on `rgba(255,255,255,.92)` | **4.15:1** | FAIL |

This **confirms UX-07 as an observed defect**, not just a source-level risk. The handoff
predicted `#6F8178`→4.13:1 and `#718077`→4.15:1 against opaque white; measured values are
3.85:1 and 4.15:1 because the real backgrounds are `--paper` and a translucent panel. The
legend panel is `rgba(255,255,255,.92)` over a map gradient, so its true ratio varies with map
content — §9.5's "use an opaque surface" is justified.

Passing pairs are comfortable (`.facility-name` 12.55:1, `.control-row` 8.00:1), so the fix is
narrow: darken five muted greys, don't rebuild the palette.

## 4. Legend is not state-aware — UX-09 confirmed

With river layers **off by default** (`#riverLayer.checked === false`), the legend still renders:

```
District-group record count
Individual facility locations are not mapped.
Clearly labelled rivers        ← claims a layer that is not drawn
```

Two defects in one row: it advertises a hidden layer, and the wording "Clearly labelled rivers"
asserts cartographic quality for what §12.4/§13.1 require to be called "Rivers — schematic".

## 5. Ownership filter ambiguity — UX-03 confirmed

All five ownership buttons render `aria-pressed="true"` simultaneously:

```
Government claim 78 | NGO / trust claim 11 | Private claim 16
Mixed / ambiguous claim 4 | Ownership not stated 3
```

"Everything pressed" is indistinguishable from "nothing filtered". The native `<button>` +
`aria-pressed` foundation is sound (§11.2), but the inclusion model is unclear to a visitor.

## 6. Mobile — partly already satisfied

Measured at 390×844:

| Check | Result |
|---|---|
| Defaults to list, not map | **Already satisfied** — `.app[data-view="list"]`, `.map-panel` is `display:none` |
| Horizontal overflow | **None** — `scrollWidth === clientWidth === 390` |
| Cultural-region / river layers off by default | **Already satisfied** (§12.3) |
| Results position | **Defect** — `#directory-results` starts at y≈1045px |
| Document height | 27,852px (all 112 cards, no pagination/virtualisation) |

The results list sits below district, search, five ownership buttons, coverage controls **and
the map-layer disclosure**. §5.3/§7.2 require map layers to be secondary and placed after the
List/Map switch and result summary. Currently `.map-layer-details` (y≈972) is rendered *above*
the results it does not filter.

## 7. Fonts

`document.fonts.size === 0` and no stylesheet or preload link for a webfont: **Inter is declared
but never shipped.** `document.fonts.check('1rem Inter')` returns `true` only because Inter is
installed on this review machine. A visitor without Inter silently gets `ui-sans-serif`.
§8.1's "self-host licensed font files" is therefore unimplemented, and the intended
"friendly rounded sans" character (REF-C) does not reach most visitors.

## 8. Contact data reality — bears directly on §11.6/§11.8

Only **13 of 112** records carry any contact string. One is masked in the source:

```
Lifeline Foundation → "+919****1178"
```

This is the exact "ambiguous number" §11.8 forbids wiring to an enabled Call action. A
"Entries with a listed telephone number" summary metric (§5.5) would honestly read **13**.

## 9. Available taxonomy for "Type of help" (§5.2 primary control #2)

No `serviceType` field exists. The closest honest sources already in the data:

```
recordKindLabel         Source site / provider record        76
                        Coordination / administrative record 19
                        Multi-site / coverage record         11
                        Helpline / information record         6

serviceMentionLabels    Rehabilitation (source term)         35
                        OOAT (source term)                   32
                        DDTC (source term)                   13
                        MMT / methadone (source term)         8
                        Model centre (source term)            6
                        Helpline (source term)                5
                        OST (source term)                     1
                        (no source term)                     18
```

`recordKindLabel` is a *role*, not a type of help. `serviceMentionLabels` is the only field
describing what the service does — but 18 records have none, and §11.4 forbids inferring
capability through unreviewed synonym matching. A "Type of help" control is therefore
**buildable but must be framed as source-term-derived**, with an explicit "not stated in source"
option for the 18. This is a §16.2 data-gated decision for the owner.

---

## 10. Handoff items already satisfied (no work required)

- Mobile defaults to a list-first view with an explicit Map switch (§4, §7.2)
- Cultural-region and river layers default to off (§12.3)
- Skip link, `visually-hidden`, `role="status"` live region, `prefers-reduced-motion` block,
  and a full `@media print` directory stylesheet all exist
- 44px minimum target sizing is already applied to map controls, view controls, switches,
  coverage buttons and `.map-layer-details summary`
- `alert()` is already gone — export failure uses the `#appStatus` live region, satisfying the
  §14.1 "accessible failure message" requirement
- No `localStorage`/`sessionStorage`/`navigator.geolocation`; CSP has no `unsafe-inline`
- Selection is already invalidated when it stops matching filters
  (`p1CurrentSelectionIsVisible`), satisfying the §18 "no stale details" checklist item

## 11. Conflicts between the handoff and enforced repo invariants

These cannot be resolved by implementation alone — they need an owner decision.

1. **`tel:` links are banned.** `validate_p0.py` asserts `"tel:" not in app_js`. §11.6 asks for
   a "Call" action. The ban and §11.8's caution point the same way for the masked number, but
   a Call button for the 12 clean numbers would require relaxing a deliberate privacy guard.
2. **"Source ownership claim" is asserted in the validator.** §13.1 renames it to "Who runs the
   service". The validator string must be updated in the same commit or the build fails.
3. **Spelling.** Every public string says "Punjab"; the owner's standing convention is "Panjab".
   The handoff uses "Punjab" throughout. Repo name and Pages URL cannot change without breaking
   the live link.
4. **Focus colour.** §9.1 proposes `--color-focus: #246B52` (green). The build currently uses
   `--focus:#073b9b` (blue) with a soft blue halo, which is *more* visible on green buttons.
   Overriding it with green would regress focus visibility on primary actions.
5. **Correction route stays unavailable.** `public-site-config.v1.json` has
   `correctionRoute: null` and the validator asserts it. §13.3 forbids inventing one, so the
   "report an issue" action remains correctly absent.
6. **Panjabi/Gurmukhi stays unpublished.** `publishedLocales: ["en"]` is validator-enforced and
   `locale-overlays.v1.json` must stay empty. §15.2's translation scaffold already exists; only
   the token/`--font-pa` groundwork can land now.
