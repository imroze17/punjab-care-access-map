#!/usr/bin/env python3
"""Restore the attached reference design while retaining the latest mapped service data and exports."""
from pathlib import Path
import json
import re

reference = Path('/home/ubuntu/upload/index.html')
facilities_file = Path('data/facilities.updated.json')
out = Path('public/index.html')

s = reference.read_text(encoding='utf-8')
facilities = json.loads(facilities_file.read_text(encoding='utf-8'))
encoded_facilities = json.dumps(facilities, ensure_ascii=False, separators=(',', ':'))

# Preserve all reference geometry, routes, controls, and visual layout; only replace the old facility list.
s, count = re.subn(r'const facilities = .*?;\nconst districtGeo =', f'const facilities = {encoded_facilities};\nconst districtGeo =', s, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('The reference facility block could not be replaced.')

# Refresh text and metadata without altering the reference's white/green visual system.
replacements = {
    'Explore 58 listed de-addiction and rehabilitation services across Punjab, India, with searchable provider filters, district layers, cultural regions, and clearly labelled rivers.': 'Explore 112 listed treatment, recovery, rehabilitation, OOAT, methadone, and referral records across Punjab, India, with searchable filters, district layers, cultural regions, and labelled rivers.',
    'Punjab Care Access Map | De-addiction Services': 'Punjab Care Access Map | Treatment & Referral Services',
    'Explore listed de-addiction and rehabilitation services across Punjab, India.': 'Explore listed treatment, recovery, rehabilitation, and referral services across Punjab, India.',
    'Punjab Care Access Map</h1><p>Listed de-addiction &amp; rehabilitation services · Punjab, India': 'Punjab Care Access Map</h1><p>Listed treatment, recovery &amp; referral services · Punjab, India',
    '<span id="headerCount">58</span> supplied listings · 23 districts': '<span id="headerCount">112</span> indexed records · 23 districts',
    '<strong id="visibleCount">58</strong><span>visible listings</span>': '<strong id="visibleCount">112</strong><span>visible listings</span>',
    '<strong id="visibleDistricts">22</strong><span>districts reached</span>': '<strong id="visibleDistricts">24</strong><span>areas indexed</span>',
    '<div class="section-label">Listed facilities <span id="resultCount"></span></div>': '<div class="section-label">Index entries <span id="resultCount"></span></div>',
    'Marker locations use district/town anchors and small visual offsets to separate co-located listings. Check the supplied address before travel.': 'Marks are display anchors, not rooftop geocodes. Consult the listed address or contact before travel.',
    '<strong>Map notes:</strong> District geometry:': '<strong>Map notes:</strong> The supplied updated CSV contributes 112 entries. District geometry:',
    "const palette = { 'Government':'#1d64b2', 'NGO / Trust':'#cd6b20', 'Private':'#7c3fb5' };": "const palette = { 'Government':'#1d64b2', 'NGO / Trust':'#cd6b20', 'Private':'#7c3fb5', 'Helpline / Office':'#167d8a' };",
    "const contact=f['Contact (if available)'];": 'const contact=f.Contact;',
    "const cols=['Name','District','mapDistrict','region','category','Type','Address','Contact (if available)','Remarks'];": "const cols=['Name','District','mapDistrict','region','category','serviceGroup','Type','Address','Contact','Remarks'];",
    "function categoryClass(c){return c==='Government'?'gov':c==='Private'?'private':'ngo';}": "function categoryClass(c){return c==='Government'?'gov':c==='Private'?'private':c==='Helpline / Office'?'helpline':'ngo';}",
    "document.getElementById('visibleDistricts').textContent=Object.keys(byDistrict).length; document.getElementById('visibleRegions').textContent=new Set(active.map(f=>f.region)).size;": "document.getElementById('visibleDistricts').textContent=Object.keys(byDistrict).length; document.getElementById('visibleRegions').textContent=new Set(active.filter(f=>f.region!=='Punjab-wide').map(f=>f.region)).size;",
    "const totals={'Government':0,'NGO / Trust':0,'Private':0};": "const totals={'Government':0,'NGO / Trust':0,'Private':0,'Helpline / Office':0};",
    "document.getElementById('governmentTotal').textContent=totals['Government'];document.getElementById('ngoTotal').textContent=totals['NGO / Trust'];document.getElementById('privateTotal').textContent=totals['Private'];": "document.getElementById('governmentTotal').textContent=totals['Government'];document.getElementById('ngoTotal').textContent=totals['NGO / Trust'];document.getElementById('privateTotal').textContent=totals['Private'];document.getElementById('helplineTotal').textContent=totals['Helpline / Office'];",
}
for old, new in replacements.items():
    if old not in s:
        raise RuntimeError(f'Expected reference text was not found: {old[:90]!r}')
    s = s.replace(old, new, 1)
s = s.replace('Punjab Care Access Map | De-addiction Services', 'Punjab Care Access Map | Treatment & Referral Services')

# Reference-style fourth category control and legend entry for the source-derived helpline/office records.
category_grid = '''<div class="category-grid" role="group" aria-label="Provider category filters">
        <button class="filter-button active" data-category="Government" aria-pressed="true"><span class="swatch" style="background:var(--gov)"></span>Government <span class="filter-count" id="governmentTotal"></span></button>
        <button class="filter-button active" data-category="NGO / Trust" aria-pressed="true"><span class="swatch" style="background:var(--ngo)"></span>NGO / Trust <span class="filter-count" id="ngoTotal"></span></button>
        <button class="filter-button active" data-category="Private" aria-pressed="true"><span class="swatch" style="background:var(--private)"></span>Private <span class="filter-count" id="privateTotal"></span></button>
        <button class="filter-button active" data-category="Helpline / Office" aria-pressed="true"><span class="swatch" style="background:var(--helpline)"></span>Helpline / Office <span class="filter-count" id="helplineTotal"></span></button>
      </div>'''
s, count = re.subn(r'<div class="category-grid" role="group" aria-label="Provider category filters">.*?</div>\n      <div class="section-label">Service type</div>', category_grid + '\n      <div class="section-label">Service type</div>', s, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('The reference category controls could not be updated.')

old_legend = '<div class="legend"><div class="legend-title">Provider category</div><div class="legend-row"><span class="legend-dot" style="background:var(--gov)"></span>Government</div><div class="legend-row"><span class="legend-dot" style="background:var(--ngo)"></span>NGO / Trust</div><div class="legend-row"><span class="legend-dot" style="background:var(--private)"></span>Private</div><div class="legend-row" style="margin-top:6px;border-top:1px solid #e3ece7;padding-top:6px"><span style="width:13px;height:0;border-top:2px solid #4a9fcb"></span>Clearly labelled rivers</div></div>'
new_legend = '<div class="legend"><div class="legend-title">Provider category</div><div class="legend-row"><span class="legend-dot" style="background:var(--gov)"></span>Government</div><div class="legend-row"><span class="legend-dot" style="background:var(--ngo)"></span>NGO / Trust</div><div class="legend-row"><span class="legend-dot" style="background:var(--private)"></span>Private</div><div class="legend-row"><span class="legend-dot" style="background:var(--helpline)"></span>Helpline / Office</div><div class="legend-row" style="margin-top:6px;border-top:1px solid #e3ece7;padding-top:6px"><span style="width:13px;height:0;border-top:2px solid #4a9fcb"></span>Clearly labelled rivers</div></div>'
if old_legend not in s:
    raise RuntimeError('The reference legend could not be updated.')
s = s.replace(old_legend, new_legend, 1)

# Restore the reference map sheet but retain compact, client-side PNG/PDF downloads above it.
export_controls = '''      <div class="map-export" role="group" aria-label="Download the map"><span>Map export</span><button id="exportPng" type="button">PNG</button><button id="exportPdf" type="button">PDF</button></div>
      <div class="map-shell">'''
s = s.replace('      <div class="map-shell">', export_controls, 1)

# Add the only small CSS extension needed for reference-styled export buttons and the new category pill.
reference_extensions = '''
  /* Reference design additions: current data category and current map export controls. */
  :root { --helpline:#167d8a; }
  .pill.helpline { color:#0f6570; background:#e1f4f5; }
  .map-export { display:flex; justify-content:flex-end; align-items:center; gap:6px; margin-top:-5px; }
  .map-export span { color:#6f8178; text-transform:uppercase; letter-spacing:.09em; font-size:.63rem; font-weight:800; margin-right:2px; }
  .map-export button { border:1px solid #c9d9d0; background:#fff; color:#2d6848; border-radius:7px; padding:5px 8px; font-size:.71rem; font-weight:700; }
  .map-export button:hover:not(:disabled) { background:#eff8f2; }.map-export button:disabled { opacity:.65; cursor:wait; }
  @media (max-width:720px) { .map-export { justify-content:flex-start; margin-top:-2px; } }
'''
s = s.replace('</style>', reference_extensions + '\n</style>', 1)

# Client-side map export: serialize the current map state, then emit a transparent-quality PNG or one-page raster PDF.
export_js = r'''function downloadBlob(blob, filename) { const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),500); }
function exportStyleText() { return Array.from(document.querySelectorAll('style')).map(style=>style.textContent).join('\n'); }
function makeExportSvg() {
  const copy=document.getElementById('map').cloneNode(true);copy.setAttribute('xmlns',NS);copy.setAttribute('width','1040');copy.setAttribute('height','850');copy.setAttribute('style','background:#eaf2ed');
  const style=document.createElementNS(NS,'style');style.textContent=exportStyleText();copy.insertBefore(style,copy.firstChild);
  const key=svg('g',{id:'exportKey','aria-hidden':'true'});key.append(svg('rect',{x:817,y:651,width:200,height:174,fill:'#ffffff','fill-opacity':'.94',stroke:'#dce9e1','stroke-width':'1'}));
  const title=svg('text',{x:832,y:676,fill:'#718077','font-family':'Inter, Arial, sans-serif','font-size':'12','font-weight':'800','letter-spacing':'.9'});title.textContent='PROVIDER CATEGORY';key.append(title);
  const rows=[['Government','#1d64b2'],['NGO / Trust','#cd6b20'],['Private','#7c3fb5'],['Helpline / Office','#167d8a']];rows.forEach(([label,color],i)=>{const y=699+i*22;key.append(svg('circle',{cx:838,cy:y-4,r:5,fill:color}));const text=svg('text',{x:852,y:y,fill:'#50655b','font-family':'Inter, Arial, sans-serif','font-size':'13'});text.textContent=label;key.append(text);});
  key.append(svg('line',{x1:832,y1:790,x2:847,y2:790,stroke:'#4a9fcb','stroke-width':'2'}));const river=svg('text',{x:852,y:794,fill:'#50655b','font-family':'Inter, Arial, sans-serif','font-size':'13'});river.textContent='Clearly labelled rivers';key.append(river);copy.append(key);return copy;
}
async function exportMapCanvas() { const copy=makeExportSvg();const serialized=new XMLSerializer().serializeToString(copy);const url=URL.createObjectURL(new Blob([serialized],{type:'image/svg+xml;charset=utf-8'}));const image=new Image();await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=reject;image.src=url;});const scale=2;const canvas=document.createElement('canvas');canvas.width=1040*scale;canvas.height=850*scale;const context=canvas.getContext('2d');context.fillStyle='#eaf2ed';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);return canvas; }
async function downloadMapPng() { const button=document.getElementById('exportPng');button.disabled=true;button.textContent='Working…';try{const canvas=await exportMapCanvas();const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));downloadBlob(blob,'punjab-care-access-map.png');}catch(error){console.error(error);alert('The PNG map could not be created. Please try again.');}finally{button.disabled=false;button.textContent='PNG';} }
function bytesFromDataUrl(dataUrl) { const bytes=atob(dataUrl.split(',')[1]);return Uint8Array.from(bytes,char=>char.charCodeAt(0)); }
function pdfBlobFromJpeg(jpeg,width,height) { const encoder=new TextEncoder(),parts=[],offsets=[0];let length=0;const add=value=>{const bytes=typeof value==='string'?encoder.encode(value):value;parts.push(bytes);length+=bytes.length;};const object=(number,body)=>{offsets[number]=length;add(`${number} 0 obj\n${body}\nendobj\n`);};add('%PDF-1.4\n');const pageWidth=792,pageHeight=Math.round(pageWidth*height/width);const content=`q\n${pageWidth} 0 0 ${pageHeight} 0 0 cm\n/Im0 Do\nQ\n`;object(1,'<< /Type /Catalog /Pages 2 0 R >>');object(2,'<< /Type /Pages /Kids [3 0 R] /Count 1 >>');object(3,`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>`);object(4,`<< /Length ${encoder.encode(content).length} >>\nstream\n${content}endstream`);offsets[5]=length;add(`5 0 obj\n<< /Type /XObject /Subtype /Image /Width ${width} /Height ${height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>\nstream\n`);add(jpeg);add('\nendstream\nendobj\n');const xref=length;add('xref\n0 6\n0000000000 65535 f \n');for(let i=1;i<=5;i++)add(`${String(offsets[i]).padStart(10,'0')} 00000 n \n`);add(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`);return new Blob(parts,{type:'application/pdf'}); }
async function downloadMapPdf() { const button=document.getElementById('exportPdf');button.disabled=true;button.textContent='Working…';try{const canvas=await exportMapCanvas();const jpeg=bytesFromDataUrl(canvas.toDataURL('image/jpeg',.92));downloadBlob(pdfBlobFromJpeg(jpeg,canvas.width,canvas.height),'punjab-care-access-map.pdf');}catch(error){console.error(error);alert('The PDF map could not be created. Please try again.');}finally{button.disabled=false;button.textContent='PDF';} }
'''
if 'function downloadMapPng()' in s:
    raise RuntimeError('The reference page unexpectedly contains existing map export handlers.')
s = s.replace('function setupControls(){', export_js + 'function setupControls(){', 1)
s = s.replace("document.getElementById('download').addEventListener('click',exportVisible);", "document.getElementById('download').addEventListener('click',exportVisible);document.getElementById('exportPng').addEventListener('click',downloadMapPng);document.getElementById('exportPdf').addEventListener('click',downloadMapPdf);", 1)

out.write_text(s, encoding='utf-8')
Path('public/manus-routes.json').write_text(json.dumps({'routes':[{'path':'/','title':'Punjab Care Access Map | Treatment & Referral Services'}]}, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'Restored reference design with {len(facilities)} current records and map exports.')
