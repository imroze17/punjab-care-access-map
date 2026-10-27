# Punjab Care Access Map — Project Overview

## What this project is

Punjab Care Access Map is a browser-based, interactive directory and map of supplied treatment, recovery, rehabilitation, opioid agonist treatment (OOAT), methadone maintenance, de-addiction, and referral records in Punjab, India. It is a **static, client-side website**: it has no account system, server, database, payment flow, or third-party map API requirement.

The delivered map uses a user-supplied reference HTML page for the visual design and structure. The reference was retained as the design base, while its earlier facility list was replaced with the refreshed facility data. The finished site offers a searchable listing index, clickable map markers and districts, provider and service filters, cultural-region and river overlays, CSV export, and client-side PNG/PDF map downloads.

The website’s primary runtime output is [`public/index.html`](public/index.html). It is self-contained: the facility records, district geometry, cultural-region definitions, river traces, styling, and interactive JavaScript are embedded in that document.

## Delivered scope

The current map includes all 112 records from the updated supplied CSV-like file. It supports:

- Full-text search across the listing information.
- Provider-category filters for **Government**, **NGO / Trust**, **Private**, and **Helpline / Office**.
- A detailed service-type selector generated from the source `Type` values.
- A scrollable, filtered listing index whose entries focus the corresponding map marker.
- Clickable district areas that focus the map view and related listings.
- Toggleable district boundaries and district labels.
- Toggleable cultural-region wash and labels for **Majha**, **Doaba**, **Malwa**, and **Puadh**.
- Toggleable major-river lines and labels for **Ravi**, **Beas**, **Sutlej**, **Ghaggar**, and **Kali Bein**.
- Map zoom, zoom-out, and reset controls.
- CSV export of the currently visible results.
- Client-side PNG and one-page PDF exports of the map’s current visible state, including a provider-category key.

The user-facing page title is **Punjab Care Access Map | Treatment & Referral Services**. The map’s visual system is the restored reference design: a dark-green header, a white-and-green interface, rounded utility panels, a left-side filter/listing column, and a main map card. The previously introduced decorative grid and degree-boundary annotations were removed.

## The updated source data

### Source supplied by the user

The active data source was the user-provided file:

```text
deepseek_csv_20261027_e08391.txt
```

Although the filename uses `.txt`, its contents are a comma-separated dataset. It contains a header and **112 source records** (source rows 2 through 113). The six logical source columns are:

| Source column | How the map uses it |
| --- | --- |
| `Name` | Displayed as the listing/facility name and in search results. |
| `District` | Preserved as supplied and used to derive a normalized map district. |
| `Address` | Shown in the selected-listing panel and retained as the original source location. |
| `Type` | Used in the detailed type filter and to derive provider category and service group. |
| `Contact` | Shown in the selected-listing panel when present; rendered as a telephone link. |
| `Remarks` | Included in the selected-listing detail panel and CSV export. |

The raw upload resides outside the Git repository, so it is **not committed**. The reproducible browser-ready output generated from it is committed as [`data/facilities.updated.json`](data/facilities.updated.json).

### Why the parser is custom

The supplied file has commas inside names and free-text remarks. In addition, the address is the reliably quoted field. A generic split-on-comma parser would shift values into the wrong columns for affected records.

[`scripts/prepare_updated_facilities.R`](scripts/prepare_updated_facilities.R) therefore uses a small quote-aware parser. For every source line, it:

1. Walks characters and separates commas only when outside quoted text.
2. Locates the quoted address field.
3. Reconstructs the name from all fields before the district/address boundary.
4. Preserves free-text remarks after the contact field, including their internal commas.
5. Produces six aligned logical values: `Name`, `District`, `Address`, `Type`, `Contact`, and `Remarks`.

This approach was specifically implemented to avoid corrupting facility names or remarks during the CSV refresh.

### Derived record model

Each source row becomes one JSON record. The map-ready JSON retains the original content and adds mapping, classification, and traceability fields.

| Field | Meaning |
| --- | --- |
| `id` | Stable display identifier generated as `F001` through `F112`. |
| `Name`, `District`, `Address`, `Type`, `Contact`, `Remarks` | Preserved logical source values. |
| `sourceDistrict` | Original unnormalized district text from the CSV. |
| `sourceLocation` | Original address from the CSV. |
| `sourceRow` | One-based original file row number, including the header row. |
| `mapDistrict` | Normalized locality used for the display anchor and map grouping. |
| `region` | Derived cultural-region label. |
| `category` | Derived primary provider category. |
| `serviceGroup` | Derived broad service classification. |
| `lat`, `lon` | Display coordinates for the marker; these are not claimed as rooftop coordinates. |

## How the CSV is transformed for the map

### 1. District normalization

The CSV uses several local, historical, abbreviated, or multi-location district labels. The R script preserves the supplied `District` field and creates a distinct `mapDistrict` for reliable grouping and display anchoring.

Current normalization rules include:

| Supplied district label | `mapDistrict` used on the map |
| --- | --- |
| `Ropar` | `Rupnagar` |
| `Shaheed Bhagat Singh Nagar (Nawanshahr)` | `Shaheed Bhagat Singh Nagar` |
| `Nawanshahr` | `Shaheed Bhagat Singh Nagar` |
| `Mohali` | `Sahibzada Ajit Singh Nagar` |
| `Derabassi (Mohali)` | `Sahibzada Ajit Singh Nagar` |
| `Khanpur (Patiala)` | `Patiala` |
| `Ropar/Ludhiana` | `Ludhiana` |
| `Punjab (multiple)` | `Punjab-wide` |
| `Statewide` | `Statewide` |

There are **24 display anchors** in the current data. These consist of district/locality anchors plus `Punjab-wide` and `Statewide` anchors for records that do not belong to one map district. The site header describes Punjab’s **23 districts**; the additional display anchors are service coverage scopes, not administrative districts.

### 2. Cultural-region assignment

Each normalized district is assigned to one of the four cultural wayfinding regions or to `Punjab-wide`:

- **Majha:** Pathankot, Gurdaspur, Amritsar, Tarn Taran.
- **Doaba:** Hoshiarpur, Jalandhar, Kapurthala, Shaheed Bhagat Singh Nagar.
- **Malwa:** Ferozepur, Fazilka, Sri Muktsar Sahib, Faridkot, Moga, Ludhiana, Malerkotla, Barnala, Sangrur, Bathinda, and Mansa.
- **Puadh:** Patiala, Fatehgarh Sahib, Sahibzada Ajit Singh Nagar, and Rupnagar.
- **Punjab-wide:** statewide/multi-district entries that should not be represented as one cultural region.

These overlays are a geographic wayfinding aid. They are not presented as official administrative boundaries.

### 3. Primary category assignment

The script derives a primary category from the source `Type` field using transparent keyword rules:

1. If `Type` contains `Helpline` or `District Office`, the record is **Helpline / Office**.
2. Otherwise, if it starts with `Government` or `District`, it is **Government**.
3. Otherwise, if it starts with `Private`, it is **Private**.
4. All remaining records are **NGO / Trust**.

The resulting category totals are:

| Provider category | Records |
| --- | ---: |
| Government | 75 |
| Private | 17 |
| NGO / Trust | 14 |
| Helpline / Office | 6 |
| **Total** | **112** |

The fourth category, **Helpline / Office**, was added during the refresh so referral and information records would not be misleadingly grouped with facility providers.

### 4. Service-group assignment

A broader `serviceGroup` is also derived from the `Type` text for analysis and export. The current results are:

| Service group | Records |
| --- | ---: |
| OOAT service | 30 |
| District coordination | 19 |
| Private provider | 17 |
| NGO / Trust | 14 |
| DDTC | 12 |
| Helpline / information | 6 |
| Methadone maintenance | 6 |
| Model centre | 5 |
| Government service | 3 |
| **Total** | **112** |

### 5. Marker placement and overlap handling

The CSV provides locations, not verified rooftop coordinates. The project therefore uses named display anchors rather than representing every facility as an exact latitude/longitude claim.

For each `mapDistrict`, the R script assigns an anchor latitude/longitude. Records sharing an anchor are then spread in a deterministic sunflower-style pattern. The offset uses a fixed angular increment and radius progression, so overlapping records remain separately clickable while the results stay reproducible on every build.

This is why the map note says that marks are display anchors, not rooftop geocodes. The original address and contact information remain visible in the listing detail for checking before travel.

### 6. Output files

Running the R script creates:

- [`data/facilities.updated.json`](data/facilities.updated.json): the 112 browser-ready JSON records.
- [`data/facility-refresh-summary.txt`](data/facility-refresh-summary.txt): a concise record, category, and service-group count summary.

## Map geography and contextual layers

### District boundaries and labels

The map embeds a filtered Punjab district geometry layer in `public/index.html`. The site’s map note attributes the district geometry to the **LGD Districts (2024)** layer filtered to Punjab through Bharat Atlas, under the stated CC0-1.0 / CC-BY-4.0 attribution. District outlines and labels each have their own on/off controls.

### Cultural-region overlays

Majha, Doaba, Malwa, and Puadh are rendered as separately toggled color washes and labels. These do not replace district boundaries; they sit alongside them as a cultural orientation layer.

### River overlays

The map includes schematic orientation lines for five water features: Ravi, Beas, Sutlej, Ghaggar, and Kali Bein. Major rivers and river labels can be toggled independently. River traces are an orientation layer, not a hydrological survey product.

## Interaction model

The website runs entirely in the browser. The interactive logic is embedded in the final HTML and maintains a client-side state for text search, selected provider categories, selected service type, selected district, selected facility, and layer visibility.

### Search and filters

The search field filters listings by source-derived listing content. Category buttons can be independently activated or deactivated. The detailed service selector filters by the original `Type` value. The index count and visible-listing metric update to reflect the active filters.

### Browsing records

The listing index and map are connected in both directions:

- Selecting a listing highlights/focuses its marker.
- Selecting a marker opens a detail panel with category, district/region, source `Type`, address, contact link when available, and remarks.
- Selecting a district focuses the district context and works with the active filters.
- A reset control returns the map interaction to its default state.

### Exports

**CSV export** produces the currently visible listings, including mapping/classification fields and original source fields.

**PNG and PDF map exports** are fully client-side. The code clones the current SVG map, adds an export key, serializes it, renders it to an in-memory canvas, and downloads either:

- `punjab-care-access-map.png`, or
- `punjab-care-access-map.pdf`.

The PDF exporter builds a one-page raster PDF in browser JavaScript. The export controls were live-tested: the PNG has a valid PNG signature, and the PDF has a valid `%PDF-1.4` header and one page.

## Technical architecture

The current site intentionally avoids a framework, server, database, client credentials, and map tile dependency.

- **Presentation and behaviour:** a single standalone HTML document with inline CSS, SVG, and JavaScript.
- **Data:** an embedded `const facilities = [...]` JSON array.
- **Map:** embedded SVG geometry and custom client-side map drawing/interaction logic; it does not use Leaflet, MapLibre, OpenLayers, or a third-party live map tile service.
- **Export:** browser-standard `XMLSerializer`, `Canvas`, Blob URLs, and a small custom PDF assembler.
- **Development preview:** a simple static server can serve `public/` on port 3000.
- **Manus static-build configuration:** `command: true` with `public` as output directory.

## File guide

| Path | Purpose |
| --- | --- |
| [`public/index.html`](public/index.html) | Canonical standalone map website used by the static build and CDN fallback. |
| [`public/logo.svg`](public/logo.svg) | Site/project marker logo and favicon asset. |
| [`public/manus-routes.json`](public/manus-routes.json) | Route manifest declaring the single home route. |
| [`data/facilities.updated.json`](data/facilities.updated.json) | Reproducible, normalized browser-ready output from the updated CSV. |
| [`data/facility-refresh-summary.txt`](data/facility-refresh-summary.txt) | Counts by category and service group. |
| [`scripts/prepare_updated_facilities.R`](scripts/prepare_updated_facilities.R) | CSV-aware parser, normalizer, classifier, anchor generator, and JSON/summary writer. |
| [`scripts/restore_reference_design.py`](scripts/restore_reference_design.py) | Rebuilds the final public map from the attached reference design and current JSON data; preserves the requested reference visual language while adding current record totals, Helpline/Office support, and map exports. |
| [`scripts/sync_github_pages.py`](scripts/sync_github_pages.py) | Copies the static site into `docs/` for GitHub Pages and changes the favicon to a repository-subpath-safe relative link. |
| [`docs/index.html`](docs/index.html) | GitHub Pages-ready copy of the static site. It is generated from `public/index.html`; do not treat it as an independent source of truth. |
| [`docs/logo.svg`](docs/logo.svg) | GitHub Pages copy of the favicon/logo. |
| [`docs/.nojekyll`](docs/.nojekyll) | Prevents Jekyll processing for the GitHub Pages source. |
| [`app.config.ts`](app.config.ts) | Project-level durable logo metadata. |
| [`TODO.md`](TODO.md) | Confirmed delivery requirements and their status. |
| [`scripts/build_atlas_page.py`](scripts/build_atlas_page.py) | Historical intermediate generator from the temporary antique-atlas design pass. Not the current final-design build path. |
| [`scripts/refine_atlas_exports.py`](scripts/refine_atlas_exports.py) | Historical refinement script from the antique-atlas pass. Its export-related changes are retained in the current restored output. |

## Rebuilding after a future CSV update

The source-data build is reproducible. The normal update sequence is:

```bash
cd /path/to/punjab-care-access-map

# 1. Point source_path in scripts/prepare_updated_facilities.R to the new supplied file,
#    or place the new CSV at the path the script expects.
Rscript scripts/prepare_updated_facilities.R

# 2. Rebuild public/index.html from the approved reference design plus the fresh JSON.
#    The script expects the reference design file at its configured reference path.
python3 scripts/restore_reference_design.py

# 3. Refresh the GitHub Pages source copy after public/ has changed.
python3 scripts/sync_github_pages.py
```

After rebuilding, validate the counts in `data/facility-refresh-summary.txt`, check that `public/index.html` contains the expected number of embedded facility records, and review the map in a browser. Then commit and push `data/`, `public/`, `docs/`, and any intentionally changed scripts together.

Important maintenance notes:

- Do not edit the generated facility JSON by hand; update the supplied data and rerun the R script.
- Keep the raw user-supplied CSV in a controlled location. It is intentionally not committed by default.
- Preserve the distinction between `District` (source text) and `mapDistrict` (normalized display location).
- Add a normalization rule and an anchor before accepting a new district/locality value that lacks one.
- Treat the cultural-region mapping as an explicit editorial choice. Revise it only deliberately.
- Regenerate `docs/` whenever `public/` changes, otherwise GitHub Pages will serve an older copy.

## Validation completed

The project was checked at several levels:

- The updated CSV was parsed and transformed into exactly 112 JSON records.
- The generated counts match the category and service-group summary.
- Every normalized location received a display anchor; the R script stops if any anchor is missing.
- The public HTML was checked for the current data count, filters, river-label controls, and export handlers.
- Desktop and mobile screenshots were reviewed during the implementation iterations.
- The PNG and PDF export controls were exercised in a browser. The downloaded PNG and PDF signatures were validated, and the PDF was verified as a one-page non-encrypted document.
- The static page and route manifest were served successfully from the project preview server.
- The GitHub repository contains a Pages-ready `docs/` folder with the map, logo, and `.nojekyll` file.

## Repository and hosting status

The canonical source repository is:

- <https://github.com/imroze17/punjab-care-access-map>

The repository is public. The `main` branch contains a GitHub Pages-ready `docs/` folder, so GitHub Pages should be configured to deploy from **branch `main`** and **folder `/docs`**. Once enabled and built by GitHub, the intended website address is:

- <https://imroze17.github.io/punjab-care-access-map/>

At the time this overview was written, GitHub’s Pages API still reported no active Pages configuration and the address returned HTTP 404. The site files are present; the remaining hosting action is to enable **Settings → Pages → Deploy from a branch → `main` / `/docs` → Save** in the repository.

A separate public self-contained HTML fallback was uploaded during the work. It is useful for immediate sharing, but GitHub Pages is the repository-backed route prepared for ongoing hosting.

## Important limitations and interpretation guidance

- The data is derived exclusively from the supplied CSV; this project does not independently verify that a listed service is currently open, accredited, funded, or clinically appropriate.
- Facility markers are **display anchors**, not verified rooftop geocodes. They help users orient themselves by district/locality but should not be used as turn-by-turn directions.
- Source district text is preserved. The normalized district is only a display and grouping field.
- Majha, Doaba, Malwa, and Puadh are editorial cultural-region overlays, not official administrative boundaries.
- River traces are schematic orientation lines rather than a hydrographic reference dataset.
- Search, filtering, and exports happen in the browser. There is no central database, user analytics store, or automatic source-data refresh.
- A CSV update requires a deliberate rebuild and redeployment. The data does not update automatically.
- Since the GitHub repository is public, its code, embedded public facility data, and commit history are visible to the public. The GitHub Pages link is a website link, but technically minded visitors can still inspect delivered browser assets as they can with any public static website.

## Implementation history

| Commit | Summary |
| --- | --- |
| `9333a24` | Initial Punjab care access map publication. |
| `62980e6` | Updated the map with the refreshed data and an interim antique-atlas style pass. |
| `77626fb` | Added tested PNG/PDF exports and related map refinements. |
| `912700b` | Restored the user-supplied reference design while preserving current data and export functionality. |
| `1d6465f` | Added the GitHub Pages-ready `docs/` copy and sync helper. |

## Practical handoff summary

For most content changes, the only files that need attention are the supplied CSV, [`scripts/prepare_updated_facilities.R`](scripts/prepare_updated_facilities.R), [`scripts/restore_reference_design.py`](scripts/restore_reference_design.py), and then [`scripts/sync_github_pages.py`](scripts/sync_github_pages.py). The map interface itself is intentionally delivered as a portable static HTML file, making it easy to share, archive, or host on any ordinary static web host.
