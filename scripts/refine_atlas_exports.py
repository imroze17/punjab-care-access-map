#!/usr/bin/env python3
from pathlib import Path
import re

page = Path("public/index.html")
s = page.read_text(encoding="utf-8")

# Remove the decorative grid, frame and degree coordinates while retaining the map groups and interaction layers.
s = s.replace('<defs><pattern id="atlasGrid" width="72" height="72" patternUnits="userSpaceOnUse"><path d="M 72 0 L 0 0 0 72" fill="none" stroke="#806e58" stroke-width="0.8" opacity="0.36"/></pattern></defs><g id="atlasFrame" aria-hidden="true"></g><g id="viewport"><g id="gridGroup"></g><g id="regionGroup"></g>', '<g id="viewport"><g id="regionGroup"></g>')
s = re.sub(r"function createAtlasFrame\(\) \{.*?\n\}\nfunction createMap\(\) \{", "function createMap() {", s, count=1, flags=re.S)
s = s.replace("  const gg=document.getElementById('gridGroup'); gg.append(svg('rect',{x:27,y:27,width:W-54,height:H-54,class:'atlas-grid'}));\n  const dg=document.getElementById('districtGroup'), rg=document.getElementById('regionGroup');", "  const dg=document.getElementById('districtGroup'), rg=document.getElementById('regionGroup');")
s = s.replace('createAtlasFrame();\ncreateMap();', 'createMap();')
s = s.replace('NOTE · Marks are display anchors, not rooftop geocodes. Consult the listed address before travel. The reference grid is ornamental, not a survey coordinate system.', 'NOTE · Marks are display anchors, not rooftop geocodes. Consult the listed address or contact before travel.')
s = s.replace('NOTE · Marks are display anchors, not rooftop geocodes. Consult the listed address or contact before travel. Map layers are designed for orientation; confirm the listed address or contact before travel.', 'NOTE · Marks are display anchors, not rooftop geocodes. Consult the listed address or contact before travel.')
s = re.sub(r'\s*\.atlas-grid\s*\{.*?\}\s*\.atlas-outer-frame\s*\{.*?\}\.atlas-inner-frame\s*\{.*?\}\.atlas-tick\s*\{.*?\}\.atlas-coordinate\s*\{.*?\}', '', s, count=1, flags=re.S)
s = s.replace('.atlas-coordinate { font-size:7px; }', '')

# Use a Garamond-first stack wherever the antique map design calls for a serif face.
s = s.replace("Georgia, 'Times New Roman', serif", "Garamond, 'EB Garamond', 'Cormorant Garamond', 'Times New Roman', serif")

# Add a compact export control between the map title/metrics and the map sheet.
export_controls = '''      <div class="map-export" role="group" aria-label="Download the map"><span>MAP EXPORT</span><button id="exportPng" type="button">PNG</button><button id="exportPdf" type="button">PDF</button></div>
      <div class="map-shell">'''
if 'id="exportPng"' not in s:
    s = s.replace('      <div class="map-shell">', export_controls, 1)

# Inject a browser-only export implementation before setupControls. It serializes the current SVG state,
# so marker filtering and selected layer visibility are accurately represented in the downloaded file.
insert_point = 'function setupControls(){'
if 'function downloadMapPng()' not in s:
    export_js = r'''function downloadBlob(blob, filename) { const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),500); }
function exportStyleText() { return Array.from(document.querySelectorAll('style')).map(style=>style.textContent).join('\n'); }
function makeExportSvg() {
  const copy=document.getElementById('map').cloneNode(true); copy.setAttribute('xmlns',NS);copy.setAttribute('width','1040');copy.setAttribute('height','850');copy.setAttribute('style','background:#efe3c6');
  const style=document.createElementNS(NS,'style');style.textContent=exportStyleText();copy.insertBefore(style,copy.firstChild);
  const key=svg('g',{id:'exportKey','aria-hidden':'true'});key.append(svg('rect',{x:816,y:34,width:190,height:164,fill:'#f8efd9',stroke:'#6b5846','stroke-width':'1'}));
  const title=svg('text',{x:829,y:56,fill:'#443527','font-family':"Garamond, 'EB Garamond', serif",'font-size':'14','font-weight':'700','letter-spacing':'.9'});title.textContent='CARE ACCESS KEY';key.append(title);
  const marks=[['Government','#9b4838','square'],['NGO / Trust','#c47736','circle'],['Private','#765c6a','diamond'],['Helpline / Office','#3d6670','triangle']];
  marks.forEach(([label,color,shape],i)=>{const y=78+i*22;if(shape==='square')key.append(svg('rect',{x:832,y:y-6,width:10,height:10,fill:color,stroke:'#332a20'}));else if(shape==='circle')key.append(svg('circle',{cx:837,cy:y-1,r:5,fill:color,stroke:'#332a20'}));else if(shape==='diamond')key.append(svg('rect',{x:833,y:y-5,width:9,height:9,fill:color,stroke:'#332a20',transform:`rotate(45 837.5 ${y-.5})`}));else key.append(svg('path',{d:`M 837 ${y-7} L 843 ${y+4} L 831 ${y+4} Z`,fill:color,stroke:'#332a20'}));const text=svg('text',{x:852,y:y+3,fill:'#49382a','font-family':"Garamond, 'EB Garamond', serif",'font-size':'13'});text.textContent=label;key.append(text);});
  key.append(svg('line',{x1:830,y1:169,x2:845,y2:169,stroke:'#657f8c','stroke-width':'2'}));const river=svg('text',{x:852,y:173,fill:'#49382a','font-family':"Garamond, 'EB Garamond', serif",'font-size':'13'});river.textContent='Major river';key.append(river);copy.append(key);return copy;
}
async function exportMapCanvas() { const svg=makeExportSvg();const text=new XMLSerializer().serializeToString(svg);const url=URL.createObjectURL(new Blob([text],{type:'image/svg+xml;charset=utf-8'}));const image=new Image();await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=reject;image.src=url;});const scale=2;const canvas=document.createElement('canvas');canvas.width=1040*scale;canvas.height=850*scale;const context=canvas.getContext('2d');context.fillStyle='#efe3c6';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);return canvas; }
async function downloadMapPng() { const button=document.getElementById('exportPng');button.disabled=true;button.textContent='WORKING…';try{const canvas=await exportMapCanvas();const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));downloadBlob(blob,'punjab-care-access-atlas.png');}catch(error){console.error(error);alert('The PNG map could not be created. Please try again.');}finally{button.disabled=false;button.textContent='PNG';} }
function bytesFromDataUrl(dataUrl) { const bytes=atob(dataUrl.split(',')[1]);return Uint8Array.from(bytes,char=>char.charCodeAt(0)); }
function pdfBlobFromJpeg(jpeg,width,height) { const encoder=new TextEncoder(),parts=[],offsets=[0];let length=0;const add=value=>{const bytes=typeof value==='string'?encoder.encode(value):value;parts.push(bytes);length+=bytes.length;};const object=(number,body)=>{offsets[number]=length;add(`${number} 0 obj\n${body}\nendobj\n`);};add('%PDF-1.4\n');const pageWidth=792,pageHeight=Math.round(pageWidth*height/width);const content=`q\n${pageWidth} 0 0 ${pageHeight} 0 0 cm\n/Im0 Do\nQ\n`;object(1,'<< /Type /Catalog /Pages 2 0 R >>');object(2,'<< /Type /Pages /Kids [3 0 R] /Count 1 >>');object(3,`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>`);object(4,`<< /Length ${encoder.encode(content).length} >>\nstream\n${content}endstream`);offsets[5]=length;add(`5 0 obj\n<< /Type /XObject /Subtype /Image /Width ${width} /Height ${height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>\nstream\n`);add(jpeg);add('\nendstream\nendobj\n');const xref=length;add('xref\n0 6\n0000000000 65535 f \n');for(let i=1;i<=5;i++)add(`${String(offsets[i]).padStart(10,'0')} 00000 n \n`);add(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`);return new Blob(parts,{type:'application/pdf'}); }
async function downloadMapPdf() { const button=document.getElementById('exportPdf');button.disabled=true;button.textContent='WORKING…';try{const canvas=await exportMapCanvas();const jpeg=bytesFromDataUrl(canvas.toDataURL('image/jpeg',.92));downloadBlob(pdfBlobFromJpeg(jpeg,canvas.width,canvas.height),'punjab-care-access-atlas.pdf');}catch(error){console.error(error);alert('The PDF map could not be created. Please try again.');}finally{button.disabled=false;button.textContent='PDF';} }
'''
    s = s.replace(insert_point, export_js + insert_point, 1)

# Wire the download buttons once alongside the existing controls.
s = s.replace("document.getElementById('download').addEventListener('click',exportVisible);", "document.getElementById('download').addEventListener('click',exportVisible);document.getElementById('exportPng').addEventListener('click',downloadMapPng);document.getElementById('exportPdf').addEventListener('click',downloadMapPdf);", 1)

refinement_css = r'''
  /* EXPORT_REFINEMENT_START */
  .map-export { display:flex; align-items:center; justify-content:flex-end; gap:6px; margin-top:-5px; }
  .map-export span { font-family:Garamond, 'EB Garamond', 'Cormorant Garamond', 'Times New Roman', serif; color:#5b4736; font-size:.72rem; letter-spacing:.11em; font-weight:700; margin-right:3px; }
  .map-export button { border:1px solid #7d6048; border-radius:1px; background:#f7ecd5; color:#493426; padding:5px 9px; font-family:Garamond, 'EB Garamond', 'Cormorant Garamond', 'Times New Roman', serif; font-size:.78rem; font-weight:700; letter-spacing:.06em; }
  .map-export button:hover:not(:disabled) { background:#ead4ad; }.map-export button:disabled { opacity:.65; cursor:wait; }
  @media (max-width:720px) { .map-export { justify-content:flex-start; margin-top:-2px; } }
  /* EXPORT_REFINEMENT_END */'''
if '/* EXPORT_REFINEMENT_START */' in s:
    s = re.sub(r'\s*/\* EXPORT_REFINEMENT_START \*/.*?/\* EXPORT_REFINEMENT_END \*/', '\n' + refinement_css, s, count=1, flags=re.S)
else:
    s = s.replace('</style>', refinement_css + '\n</style>', 1)

page.write_text(s, encoding="utf-8")
print('Applied Garamond, removed grid/degree annotations, and added PNG/PDF map export.')
