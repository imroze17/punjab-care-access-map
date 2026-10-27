#!/usr/bin/env python3
"""Embed the refreshed facility JSON and apply the antique-atlas visual system."""
from pathlib import Path
import json
import re

page = Path("public/index.html")
facilities_path = Path("data/facilities.updated.json")
routes = Path("public/manus-routes.json")
s = page.read_text(encoding="utf-8")
facilities = json.loads(facilities_path.read_text(encoding="utf-8"))
facility_json = json.dumps(facilities, ensure_ascii=False, separators=(",", ":"))

# Replace the embedded list; geo boundaries remain unchanged.
s, count = re.subn(r"const facilities = .*?;\nconst districtGeo =", f"const facilities = {facility_json};\nconst districtGeo =", s, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Could not replace the embedded facilities list")

replacements = {
    "<title>Punjab Care Access Map | De-addiction Services</title>": "<title>Punjab Care Access Atlas | Service Index</title>",
    'content="Explore 58 listed de-addiction and rehabilitation services across Punjab, India, with searchable provider filters, district layers, cultural regions, and clearly labelled rivers."': 'content="Explore 112 listed de-addiction, treatment, rehabilitation, OOAT, methadone, and referral services across Punjab, India in an interactive care access atlas."',
    'content="Punjab Care Access Map | De-addiction Services"': 'content="Punjab Care Access Atlas | Service Index"',
    'content="Explore listed de-addiction and rehabilitation services across Punjab, India."': 'content="Explore listed de-addiction, treatment, rehabilitation, and referral services across Punjab, India."',
    '<h1>Punjab Care Access Map</h1><p>Listed de-addiction &amp; rehabilitation services · Punjab, India</p>': '<h1>Punjab Care Access Atlas</h1><p>A field index of treatment, recovery, and referral services · Punjab, India</p>',
    '<div class="header-stat"><span id="headerCount">58</span> supplied listings · 23 districts</div>': '<div class="header-stat"><span id="headerCount">112</span> indexed records · 23 districts</div>',
    '<div class="section-label">Find a listing</div>': '<div class="section-label">Search the index</div>',
    '<div class="section-label">Provider category</div>': '<div class="section-label">Service mark</div>',
    '<div class="section-label">Service type</div>': '<div class="section-label">Listing type</div>',
    '<div class="section-label">Map layers</div>': '<div class="section-label">Map sheets</div>',
    '<div class="map-title"><h2>Explore the service landscape</h2><p>Click a district to focus it, select a marker for the supplied listing, or use the filters at left.</p></div>': '<div class="map-title"><h2>Punjab care &amp; recovery index</h2><p>Use the service marks, district boundaries, and river lines to navigate the supplied listings.</p></div>',
    '<span>districts reached</span>': '<span>areas indexed</span>',
    '<span>regions represented</span>': '<span>cultural regions</span>',
    '<div class="section-label">Listed facilities <span id="resultCount"></span></div>': '<div class="section-label">Index entries <span id="resultCount"></span></div>',
    'Marker locations use district/town anchors and small visual offsets to separate co-located listings. Check the supplied address before travel.': 'NOTE · Marks are display anchors, not rooftop geocodes. Consult the listed address or contact before travel. The reference grid is ornamental, not a survey coordinate system.',
    '<strong>Map notes:</strong> District geometry: LGD Districts (2024), filtered to Punjab, via': '<strong>Atlas notes:</strong> The supplied updated CSV contributes 112 entries. District geometry: LGD Districts (2024), filtered to Punjab, via',
    "const palette = { 'Government':'#1d64b2', 'NGO / Trust':'#cd6b20', 'Private':'#7c3fb5' };": "const palette = { 'Government':'#9b4838', 'NGO / Trust':'#c47736', 'Private':'#765c6a', 'Helpline / Office':'#3d6670' };",
    "const regionColors = { Majha:'#f1b44c', Doaba:'#4ea0a8', Malwa:'#e07a5f', Puadh:'#8c74b9' };": "const regionColors = { Majha:'#c6a056', Doaba:'#7895a3', Malwa:'#bd7e66', Puadh:'#91809d' };",
    "const contact=f['Contact (if available)'];": "const contact=f.Contact;",
    "const cols=['Name','District','mapDistrict','region','category','Type','Address','Contact (if available)','Remarks'];": "const cols=['Name','District','mapDistrict','region','category','serviceGroup','Type','Address','Contact','Remarks'];",
    "function categoryClass(c){return c==='Government'?'gov':c==='Private'?'private':'ngo';}": "function categoryClass(c){return c==='Government'?'gov':c==='Private'?'private':c==='Helpline / Office'?'helpline':'ngo';}",
    "document.getElementById('governmentTotal').textContent=totals['Government'];document.getElementById('ngoTotal').textContent=totals['NGO / Trust'];document.getElementById('privateTotal').textContent=totals['Private'];": "document.getElementById('governmentTotal').textContent=totals['Government'];document.getElementById('ngoTotal').textContent=totals['NGO / Trust'];document.getElementById('privateTotal').textContent=totals['Private'];document.getElementById('helplineTotal').textContent=totals['Helpline / Office'];",
}
for old, new in replacements.items():
    if old not in s:
        raise RuntimeError(f"Expected production text not found: {old[:70]}")
    s = s.replace(old, new, 1)

# Add the fourth, source-derived primary category while retaining existing filter behavior.
category_markup = '''<div class="category-grid" role="group" aria-label="Provider category filters">
        <button class="filter-button active" data-category="Government" aria-pressed="true"><span class="swatch" style="background:var(--gov)"></span>Government <span class="filter-count" id="governmentTotal"></span></button>
        <button class="filter-button active" data-category="NGO / Trust" aria-pressed="true"><span class="swatch" style="background:var(--ngo)"></span>NGO / Trust <span class="filter-count" id="ngoTotal"></span></button>
        <button class="filter-button active" data-category="Private" aria-pressed="true"><span class="swatch" style="background:var(--private)"></span>Private <span class="filter-count" id="privateTotal"></span></button>
        <button class="filter-button active" data-category="Helpline / Office" aria-pressed="true"><span class="swatch" style="background:var(--helpline)"></span>Helpline / Office <span class="filter-count" id="helplineTotal"></span></button>
      </div>'''
s, count = re.subn(r'<div class="category-grid" role="group" aria-label="Provider category filters">.*?</div>\n      <div class="section-label">Listing type</div>', category_markup + '\n      <div class="section-label">Listing type</div>', s, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Could not replace category controls")

legend = '''<div class="legend" aria-label="Map key"><div class="legend-title">Care access key</div><div class="key-rule"></div><div class="legend-row"><span class="key-symbol key-government"></span>Government</div><div class="legend-row"><span class="key-symbol key-ngo"></span>NGO / Trust</div><div class="legend-row"><span class="key-symbol key-private"></span>Private</div><div class="legend-row"><span class="key-symbol key-helpline"></span>Helpline / Office</div><div class="key-rule"></div><div class="legend-row"><span class="key-line"></span>Major river</div><div class="legend-row"><span class="key-boundary"></span>District boundary</div></div>'''
s, count = re.subn(r'<div class="legend">.*?(?=\n      <div class="footer-note">)', legend, s, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Could not replace the map key")

# Insert a grid definition plus fixed atlas-frame group; the grid itself lives inside viewport and zooms with the geography.
old_svg = '<svg id="map" viewBox="0 0 1040 850" role="img" aria-label="Map of Punjab, India showing listed de-addiction and rehabilitation services, districts, cultural regions, and major rivers"><g id="viewport"><g id="regionGroup"></g>'
new_svg = '''<svg id="map" viewBox="0 0 1040 850" role="img" aria-label="Atlas map of Punjab, India showing treatment, recovery, OOAT, methadone, rehabilitation, and referral records with districts, cultural regions, and major rivers"><defs><pattern id="atlasGrid" width="72" height="72" patternUnits="userSpaceOnUse"><path d="M 72 0 L 0 0 0 72" fill="none" stroke="#806e58" stroke-width="0.8" opacity="0.36"/></pattern></defs><g id="atlasFrame" aria-hidden="true"></g><g id="viewport"><g id="gridGroup"></g><g id="regionGroup"></g>'''
if old_svg not in s:
    raise RuntimeError("Could not find the map SVG group structure")
s = s.replace(old_svg, new_svg, 1)

# Add cartographic frame/grid helpers before the existing map draw routine.
if 'function createAtlasFrame()' not in s:
    marker = 'function createMap() {'
    atlas_helpers = '''function createAtlasFrame() {
  const frame=document.getElementById('atlasFrame');
  frame.append(svg('rect',{x:12,y:12,width:W-24,height:H-24,class:'atlas-outer-frame'}));
  frame.append(svg('rect',{x:21,y:21,width:W-42,height:H-42,class:'atlas-inner-frame'}));
  const cols=5, rows=5;
  for(let i=0;i<=cols;i++){const x=42+i*(W-84)/cols;const lon=bounds.minLon+(bounds.maxLon-bounds.minLon)*i/cols;const tick=svg('line',{x1:x,y1:21,x2:x,y2:29,class:'atlas-tick'});frame.append(tick);const top=svg('text',{x,y:19,class:'atlas-coordinate','text-anchor':'middle'});top.textContent=`${lon.toFixed(1)}°E`;frame.append(top);const bottom=svg('text',{x,y:H-10,class:'atlas-coordinate','text-anchor':'middle'});bottom.textContent=`${lon.toFixed(1)}°E`;frame.append(bottom);}
  for(let i=0;i<=rows;i++){const y=42+i*(H-84)/rows;const lat=bounds.maxLat-(bounds.maxLat-bounds.minLat)*i/rows;frame.append(svg('line',{x1:21,y1:y,x2:29,y2:y,class:'atlas-tick'}));const left=svg('text',{x:18,y:y+3,class:'atlas-coordinate','text-anchor':'end'});left.textContent=`${lat.toFixed(1)}°N`;frame.append(left);const right=svg('text',{x:W-18,y:y+3,class:'atlas-coordinate','text-anchor':'start'});right.textContent=`${lat.toFixed(1)}°N`;frame.append(right);}
}
'''
    s = s.replace(marker, atlas_helpers + marker, 1)

# Grid is deliberately noninteractive and drawn before regions.
s = s.replace("  const dg=document.getElementById('districtGroup'), rg=document.getElementById('regionGroup');", "  const gg=document.getElementById('gridGroup'); gg.append(svg('rect',{x:27,y:27,width:W-54,height:H-54,class:'atlas-grid'}));\n  const dg=document.getElementById('districtGroup'), rg=document.getElementById('regionGroup');", 1)

marker_pattern = re.compile(r"\s+facilities\.forEach\(f=>\{ const \[x,y\]=project\(f\.lat,f\.lon\); const c=svg\('circle',\{cx:x,cy:y,r:5\.4,fill:palette\[f\.category\],class:'facility-marker','data-id':f\.id,tabindex:'0',role:'button','aria-label':`\$\{f\.Name\}, \$\{f\.mapDistrict\}`\}\); c\.addEventListener\('click',e=>\{e\.stopPropagation\(\); selectFacility\(f\.id\);\}\);c\.addEventListener\('keydown',e=>\{if\(e\.key==='Enter'\|\|e\.key===' '\)\{e\.preventDefault\(\);selectFacility\(f\.id\);\}\}\);document\.getElementById\('markerGroup'\)\.append\(c\); \}\);")
marker_replacement = '''
  facilities.forEach(f=>{
    const [x,y]=project(f.lat,f.lon); const common={fill:palette[f.category],class:`facility-marker symbol-${categoryClass(f.category)}`,'data-id':f.id,tabindex:'0',role:'button','aria-label':`${f.Name}, ${f.mapDistrict}`}; let c;
    if(f.category==='Government') c=svg('rect',{...common,x:x-4.2,y:y-4.2,width:8.4,height:8.4});
    else if(f.category==='NGO / Trust') c=svg('circle',{...common,cx:x,cy:y,r:4.35});
    else if(f.category==='Private') c=svg('rect',{...common,x:x-3.6,y:y-3.6,width:7.2,height:7.2,transform:`rotate(45 ${x} ${y})`});
    else c=svg('path',{...common,d:`M ${x} ${y-5.1} L ${x+5.1} ${y+4.0} L ${x-5.1} ${y+4.0} Z`});
    c.addEventListener('click',e=>{e.stopPropagation(); selectFacility(f.id);});c.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectFacility(f.id);}});document.getElementById('markerGroup').append(c);
  });'''
s, count = marker_pattern.subn(marker_replacement, s, count=1)
if count != 1:
    raise RuntimeError("Could not replace the map marker constructor")

s = s.replace("document.getElementById('visibleRegions').textContent=new Set(active.map(f=>f.region)).size;", "document.getElementById('visibleRegions').textContent=new Set(active.filter(f=>f.region!=='Punjab-wide').map(f=>f.region)).size;", 1)
s = s.replace("const totals={'Government':0,'NGO / Trust':0,'Private':0};", "const totals={'Government':0,'NGO / Trust':0,'Private':0,'Helpline / Office':0};", 1)
s = s.replace('createMap();\nconst totals=', 'createAtlasFrame();\ncreateMap();\nconst totals=', 1)

atlas_css = r'''
  /* ATLAS_RESTYLE_START */
  :root { --ink:#332a20; --muted:#746653; --paper:#eee3c8; --card:#f8f0dc; --line:#9a876d; --green:#9b4838; --green-soft:#ead7bc; --gov:#9b4838; --ngo:#c47736; --private:#765c6a; --helpline:#3d6670; --shadow:0 2px 10px rgba(62,43,22,.12); }
  html, body { background:var(--paper); color:var(--ink); }
  header { background:#3a2c21; border-bottom:4px double #c9b18a; box-shadow:none; padding:14px clamp(18px,3vw,42px); }
  .brand-mark { border-radius:0; border-color:#ddcaa6; color:#eadabc; background:transparent; }
  .brand h1, .map-title h2, .legend-title, .section-label { font-family:Georgia, 'Times New Roman', serif; }
  .brand h1 { font-size:1.2rem; letter-spacing:.02em; }
  .brand p { color:#dfcfad; }
  .header-stat { border-radius:0; border-color:#bba57f; color:#eadabc; font-family:Georgia, 'Times New Roman', serif; }
  .workspace { background:#eee3c8; }
  aside { background:#f5ecd6; border-right:1px solid #8f7d66; }
  .section-label { color:#594837; letter-spacing:.11em; font-weight:700; }
  input[type="search"], .type-select { border-radius:2px; border-color:#a79277; background:#fff8e8; color:#332a20; }
  input[type="search"]:focus, .type-select:focus { border-color:#754936; box-shadow:0 0 0 3px rgba(155,72,56,.16); }
  .filter-button { border-radius:2px; border-color:#b29d80; color:#443527; background:#fbf3e0; }
  .filter-button:hover { border-color:#72533d; background:#f6e5c8; }
  .filter-button.active { background:#ead6b6; border-color:#704934; color:#3f2b20; }
  .filter-button[data-category="Government"] .swatch { border-radius:0; }
  .filter-button[data-category="Private"] .swatch { border-radius:0; transform:rotate(45deg); }
  .filter-button[data-category="Helpline / Office"] .swatch { border-radius:0; clip-path:polygon(50% 0,100% 100%,0 100%); }
  .control-card, .selection { border-radius:2px; border-color:#b39e80; background:#fbf3e2; }
  .control-row { color:#503e2e; }
  .slider { border-radius:1px; background:#b9a688; }
  input:checked + .slider { background:#8a4a35; }
  .slider:before { border-radius:0; box-shadow:none; }
  .region-check { color:#594837; }
  .facility { border-radius:2px; border-color:#c5b293; background:#fff8e8; }
  .facility:hover, .facility.is-selected { border-color:#7d5039; background:#f5e4c8; box-shadow:none; }
  .facility-name { color:#3c2d21; }
  .facility-meta { color:#796a58; }
  .pill { border-radius:1px; border:1px solid currentColor; background:transparent!important; letter-spacing:.05em; }
  .pill.gov { color:#7d3f30; }.pill.ngo { color:#9f5928; }.pill.private { color:#624957; }.pill.helpline { color:#2c5862; }
  .small-action { border-radius:1px; border-color:#8e684d; color:#643c2b; background:#f9efdc; }
  .active-context { border-radius:1px; background:#ead6b6; color:#4a3627; }
  .active-context button { color:#6b3f2d; }
  main { background:#eee3c8; }
  .map-title h2 { color:#3b2a20; font-size:1.32rem; letter-spacing:.015em; }
  .map-title p, .footer-note { color:#695d4c; }
  .metric { background:#f8f0dc; border-radius:1px; border-color:#aa9679; box-shadow:none; }
  .metric strong { color:#853f30; font-family:Georgia, 'Times New Roman', serif; font-size:1.08rem; }.metric span { color:#746451; }
  .map-shell { border-radius:0; border:1px solid #403426; background:#eadfbe; box-shadow:0 2px 10px rgba(62,43,22,.12); }
  .map-shell::before { content:""; position:absolute; z-index:5; inset:7px; border:1px solid #806e58; pointer-events:none; }
  #map { background-color:#efe3c6; background-image:radial-gradient(ellipse at 20% 12%,rgba(255,252,235,.64),transparent 37%),radial-gradient(ellipse at 80% 85%,rgba(192,161,113,.14),transparent 43%),linear-gradient(118deg,rgba(255,255,255,.12),rgba(100,75,42,.04)); }
  .map-actions { right:19px; bottom:21px; top:auto; z-index:7; grid-auto-flow:column; }
  .map-actions button { border-radius:1px; border-color:#745d49; background:#f8efd9; color:#4b3527; box-shadow:none; }
  .map-actions button:hover { background:#ead4b0; }
  .map-note { left:20px; bottom:20px; border-radius:1px; border-color:#9d876a; background:rgba(250,242,220,.95); color:#594b3a; box-shadow:none; font-family:Georgia, 'Times New Roman', serif; }
  .legend { right:20px; top:20px; bottom:auto; border-radius:1px; border-color:#7e6a55; background:rgba(249,240,217,.95); color:#49382a; box-shadow:none; min-width:145px; z-index:6; }
  .legend-title { color:#49382a; font-size:.7rem; letter-spacing:.11em; }
  .key-rule { border-top:1px solid #a99071; margin:7px 0; }
  .key-symbol { width:10px; height:10px; display:inline-block; border:1px solid #332a20; }
  .key-government { background:#9b4838; }.key-ngo { background:#c47736; border-radius:50%; }.key-private { background:#765c6a; transform:rotate(45deg); margin:0 2px; }.key-helpline { background:#3d6670; clip-path:polygon(50% 0,100% 100%,0 100%); border:0; }
  .key-line { width:14px; height:0; border-top:2px solid #657f8c; }.key-boundary { width:14px; height:0; border-top:1px solid #514333; }
  .atlas-grid { fill:url(#atlasGrid); pointer-events:none; opacity:.34; }
  .atlas-outer-frame { fill:none; stroke:#403426; stroke-width:1.6; vector-effect:non-scaling-stroke; }.atlas-inner-frame { fill:none; stroke:#806e58; stroke-width:.8; vector-effect:non-scaling-stroke; }.atlas-tick { stroke:#675541; stroke-width:1; }.atlas-coordinate { fill:#554535; font-family:Georgia, 'Times New Roman', serif; font-size:8px; letter-spacing:.03em; }
  .district { fill:#f7eed9; fill-opacity:.73; stroke:#514333; stroke-width:1; }.district:hover { stroke:#6e3c2c; stroke-width:1.7; }.district.active-district { fill:#dfbd79; fill-opacity:.54; stroke:#4a2d22; stroke-width:2; }
  .region-wash { opacity:.12; }.river { stroke:#657f8c; stroke-width:1.65; opacity:.9; }.river-label, .region-label, .district-label { font-family:Georgia, 'Times New Roman', serif; stroke:#f4e8cc; }.river-label { fill:#466d7c; font-size:13px; font-style:italic; font-weight:700; stroke-width:4.5px; }.region-label { fill:#554436; font-size:15px; letter-spacing:.12em; stroke-width:5px; opacity:.7; }.district-label { fill:#44372b; font-size:10px; font-weight:700; stroke-width:3.5px; }
  .facility-marker { stroke:#332a20; stroke-width:1.15; vector-effect:non-scaling-stroke; filter:none; }.facility-marker:hover, .facility-marker.selected-marker, .facility-marker:focus-visible { stroke:#f6e7ca; stroke-width:3.2; outline:none; }.symbol-helpline { stroke:#efe0c2; stroke-width:1.1; }
  @media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior:auto!important; transition:none!important; } }
  @media (max-width:720px) { .map-shell::before { inset:5px; }.legend { top:auto; right:13px; bottom:13px; transform:scale(.85); transform-origin:bottom right; }.map-actions { right:13px; bottom:14px; grid-auto-flow:row; }.map-note { left:13px; bottom:13px; max-width:220px; }.atlas-coordinate { font-size:7px; } }
  /* ATLAS_RESTYLE_END */'''
if '/* ATLAS_RESTYLE_START */' in s:
    s = re.sub(r'\s*/\* ATLAS_RESTYLE_START \*/.*?/\* ATLAS_RESTYLE_END \*/', '\n' + atlas_css, s, count=1, flags=re.S)
else:
    s = s.replace('</style>', atlas_css + '\n</style>', 1)

page.write_text(s, encoding="utf-8")
routes.write_text(json.dumps({"routes":[{"path":"/","title":"Punjab Care Access Atlas | Service Index"}]}, separators=(",", ":")) + "\n", encoding="utf-8")
print(f"Embedded {len(facilities)} updated records into {page}")
