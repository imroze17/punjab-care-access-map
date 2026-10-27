const P0_OWNERSHIP_CATEGORIES = [
  { value: 'government_claim', label: 'Government claim', color: '#1d64b2', className: 'gov' },
  { value: 'ngo_or_trust_claim', label: 'NGO / trust claim', color: '#cd6b20', className: 'ngo' },
  { value: 'private_claim', label: 'Private claim', color: '#7c3fb5', className: 'private' },
  { value: 'mixed_or_ambiguous_claim', label: 'Mixed / ambiguous claim', color: '#167d8a', className: 'helpline' },
  { value: 'not_stated', label: 'Ownership not stated', color: '#5f6f68', className: 'helpline' },
];
const P0_CATEGORY_BY_VALUE = new Map(P0_OWNERSHIP_CATEGORIES.map(item => [item.value, item]));
const P0_FILTER_CATEGORIES = ['government_claim', 'ngo_or_trust_claim', 'private_claim', 'mixed_or_ambiguous_claim', 'not_stated'];
const P0_RECORD_KINDS = [
  ['site_or_provider_record', 'Source site / provider record'],
  ['administrative_or_coordination_record', 'Coordination / administrative record'],
  ['helpline_or_information_record', 'Helpline / information record'],
  ['coverage_or_multi_site_record', 'Multi-site / coverage record'],
];

function esc(value = '') {
  return String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function p0Category(value) {
  return P0_CATEGORY_BY_VALUE.get(value) || P0_CATEGORY_BY_VALUE.get('not_stated');
}

function p0ScopeLabel(record) {
  if (record.coverageScope === 'statewide') return 'Statewide coverage';
  if (record.coverageScope === 'multi_district') return 'Punjab-wide / multi-district coverage';
  if (record.coverageScope === 'multiple_sites_within_district') return `Reported district: ${record.mapDistrict} (multiple sites noted)`;
  return `Reported district: ${record.mapDistrict}`;
}

function p0PrecisionLabel(record) {
  const values = {
    coverage_scope_no_single_place: 'Coverage scope only; no single place is mapped.',
    multiple_sites_no_single_place: 'Multiple sites are described; individual sites are not mapped.',
    district_or_city_text: 'District/city text supplied; no facility location is mapped.',
    named_institution_text_unverified: 'Named institution text supplied; location is not verified or mapped.',
    detailed_address_text_unverified: 'Address text supplied; location is not verified or mapped.',
    locality_text_unverified: 'Locality text supplied; location is not verified or mapped.',
  };
  return values[record.locationPrecision] || 'Location details are not confirmed.';
}

function p0PublicRemarks(value) {
  const cleaned = String(value || '').replace(/\[reference:[^\]]+\]/gi, '').replace(/\s{2,}/g, ' ').trim();
  return cleaned || 'No public source remarks supplied.';
}

function p0SafeTelephone(value) {
  const digits = String(value || '').replace(/[^+0-9]/g, '');
  return /^\+?[0-9]{7,15}$/.test(digits) ? digits : null;
}

function createMap() {
  const districtGroup = document.getElementById('districtGroup');
  const regionGroup = document.getElementById('regionGroup');
  const labelGroup = document.getElementById('districtLabelGroup');
  const riverGroup = document.getElementById('riverGroup');
  const riverLabelGroup = document.getElementById('riverLabelGroup');
  const regionLabelGroup = document.getElementById('regionLabelGroup');
  districtGroup.replaceChildren(); regionGroup.replaceChildren(); labelGroup.replaceChildren();
  riverGroup.replaceChildren(); riverLabelGroup.replaceChildren(); regionLabelGroup.replaceChildren();
  document.getElementById('markerGroup').replaceChildren();
  districtGeo.features.forEach(feature => {
    const path = pathFor(feature.geometry);
    const name = feature.properties.name;
    const region = feature.properties.region;
    const wash = svg('path', { d: path, class: 'region-wash', fill: regionColors[region], 'data-region': region });
    regionGroup.append(wash);
    const district = svg('path', { d: path, class: 'district', 'data-district': name, 'aria-label': `${name} district group` });
    district.addEventListener('click', () => focusDistrict(name));
    districtGroup.append(district);
    const anchor = labelAnchors[name] || geometryCenter(feature.geometry);
    const [x, y] = project(anchor[0], anchor[1]);
    const label = svg('text', { x, y: y - 2, class: 'district-label', 'data-district-label': name });
    label.textContent = p0DistrictShortName(name);
    labelGroup.append(label);
  });
  rivers.forEach(river => {
    const d = river.pts.map((point, index) => {
      const [x, y] = project(point[0], point[1]);
      return `${index ? 'L' : 'M'}${x},${y}`;
    }).join(' ');
    riverGroup.append(svg('path', { d, class: 'river' }));
    const [x, y] = project(river.label[0], river.label[1]);
    const text = svg('text', { x, y, class: 'river-label' });
    text.textContent = river.name === 'Kali Bein' ? river.name : `${river.name} River`;
    riverLabelGroup.append(text);
  });
  Object.entries(regionAnchors).forEach(([name, coordinate]) => {
    const [x, y] = project(coordinate[0], coordinate[1]);
    const label = svg('text', { x, y, class: 'region-label', 'data-region-label': name, 'text-anchor': 'middle' });
    label.textContent = name.toUpperCase();
    regionLabelGroup.append(label);
  });
}

function geometryCenter(geometry) {
  const points = [];
  const walk = coordinates => typeof coordinates[0] === 'number' ? points.push(coordinates) : coordinates.forEach(walk);
  walk(geometry.coordinates);
  return [points.reduce((sum, point) => sum + point[1], 0) / points.length, points.reduce((sum, point) => sum + point[0], 0) / points.length];
}

function p0DistrictShortName(name) {
  return name
    .replace('Sahibzada Ajit Singh Nagar', 'S.A.S. Nagar')
    .replace('Shaheed Bhagat Singh Nagar', 'S.B.S. Nagar')
    .replace('Sri Muktsar Sahib', 'Muktsar');
}

function activeFacilities(ignoreCoverageScope = false) {
  const query = state.query.trim().toLowerCase();
  return facilities.filter(record => {
    const searchable = [record.Name, record.District, record.mapDistrict, record.Address, record.Type, record.Remarks, record.Contact, record.recordKindLabel, ...(record.serviceMentionLabels || [])].join(' ').toLowerCase();
    return state.categories.has(record.ownershipClaim)
      && (!state.detailType || record.recordKind === state.detailType)
      && (!state.selectedDistrict || record.mapDistrict === state.selectedDistrict)
      && (ignoreCoverageScope || !state.coverageScope || record.coverageScope === state.coverageScope)
      && (!query || searchable.includes(query));
  });
}

function p0GroupByDistrict(records) {
  const groups = new Map();
  records.filter(record => record.mapRepresentation === 'district_group_summary').forEach(record => {
    if (!groups.has(record.mapDistrict)) groups.set(record.mapDistrict, []);
    groups.get(record.mapDistrict).push(record);
  });
  return groups;
}

function render() {
  const active = activeFacilities();
  const scopeAgnostic = activeFacilities(true);
  const districtGroups = p0GroupByDistrict(active);
  const coverageRecords = active.filter(record => record.mapRepresentation === 'coverage_scope_control');
  document.getElementById('visibleCount').textContent = active.length;
  document.getElementById('headerCount').textContent = facilities.length;
  document.getElementById('resultCount').textContent = `(${active.length})`;
  p0UpdateOwnershipCounts();
  document.getElementById('visibleDistricts').textContent = districtGroups.size;
  document.getElementById('visibleRegions').textContent = coverageRecords.length;

  const markerGroup = document.getElementById('markerGroup');
  markerGroup.replaceChildren();
  districtGroups.forEach((records, districtName) => {
    const district = districtGeo.features.find(feature => feature.properties.name === districtName);
    if (!district) return;
    const anchor = labelAnchors[districtName] || geometryCenter(district.geometry);
    const [x, y] = project(anchor[0], anchor[1]);
    const count = records.length;
    const group = svg('g', { class: 'district-summary-group', 'data-district-summary': districtName, tabindex: '0', role: 'button', 'aria-label': `${districtName}: ${count} matching directory record${count === 1 ? '' : 's'}, grouped at district level; individual locations are not mapped.` });
    const circle = svg('circle', { cx: x, cy: y, r: Math.min(19, 10 + Math.sqrt(count) * 2.2), class: 'district-summary-marker' });
    const label = svg('text', { x, y: y + 4, class: 'district-summary-count', 'text-anchor': 'middle', 'aria-hidden': 'true' });
    label.textContent = count;
    group.append(circle, label);
    group.addEventListener('click', event => { event.stopPropagation(); focusDistrict(districtName); });
    group.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); focusDistrict(districtName); }
    });
    markerGroup.append(group);
  });

  document.querySelectorAll('.district').forEach(district => {
    const name = district.dataset.district;
    district.style.display = state.showDistricts ? '' : 'none';
    district.classList.toggle('active-district', state.selectedDistrict === name);
  });
  document.querySelectorAll('.region-wash').forEach(path => { path.style.display = state.showRegions && state.regions.has(path.dataset.region) ? '' : 'none'; });
  document.querySelectorAll('.district-label').forEach(label => {
    const name = label.dataset.districtLabel;
    label.style.display = state.showDistrictLabels ? '' : 'none';
    const count = districtGroups.get(name)?.length || 0;
    label.textContent = `${p0DistrictShortName(name)}${count ? ` · ${count}` : ''}`;
  });
  document.querySelectorAll('.region-label').forEach(label => { label.style.display = state.showRegionLabels && state.regions.has(label.dataset.regionLabel) ? '' : 'none'; });
  document.getElementById('riverGroup').style.display = state.showRivers ? '' : 'none';
  document.getElementById('riverLabelGroup').style.display = state.showRivers && state.showRiverLabels ? '' : 'none';
  p0RenderCoverageControls(scopeAgnostic, coverageRecords);
  renderList(active); renderContext(); renderSelection();
}

function renderList(items) {
  const container = document.getElementById('facilityList');
  const sorted = [...items].sort((left, right) => p0ScopeLabel(left).localeCompare(p0ScopeLabel(right)) || left.Name.localeCompare(right.Name));
  if (!sorted.length) {
    container.innerHTML = '<div class="empty">No listings in this directory for the selected filters. This does not establish that services are unavailable.</div>';
    return;
  }
  container.innerHTML = sorted.map(record => {
    const category = p0Category(record.ownershipClaim);
    return `<button class="facility ${state.selectedFacility === record.id ? 'is-selected' : ''}" data-facility="${esc(record.id)}"><div class="facility-top"><span class="swatch" style="background:${category.color};margin-top:3px"></span><p class="facility-name">${esc(record.Name)}</p></div><div class="facility-meta"><span class="pill ${category.className}">${esc(category.label)}</span><span>${esc(p0ScopeLabel(record))}</span></div><p class="p0-card-role">${esc(record.recordKindLabel)}</p></button>`;
  }).join('');
  container.querySelectorAll('[data-facility]').forEach(button => button.addEventListener('click', () => selectFacility(button.dataset.facility)));
}

function renderContext() {
  const box = document.getElementById('activeContext');
  if (state.selectedDistrict) {
    box.classList.add('visible');
    document.getElementById('contextText').textContent = `District group: ${state.selectedDistrict}. Individual service locations are not mapped.`;
  } else if (state.coverageScope) {
    box.classList.add('visible');
    document.getElementById('contextText').textContent = state.coverageScope === 'statewide' ? 'Statewide information/referral records.' : 'Punjab-wide or multi-district records.';
  } else {
    box.classList.remove('visible');
  }
}

function renderSelection() {
  const box = document.getElementById('selection');
  if (!state.selectedFacility) { box.classList.remove('visible'); box.innerHTML = ''; return; }
  const record = facilities.find(item => item.id === state.selectedFacility);
  if (!record) { box.classList.remove('visible'); return; }
  const category = p0Category(record.ownershipClaim);
  const telephone = p0SafeTelephone(record.Contact);
  const terms = (record.serviceMentionLabels || []).length ? `<p><strong>Source terms:</strong> ${esc(record.serviceMentionLabels.join(', '))}</p>` : '<p><strong>Source terms:</strong> Not classified beyond the supplied record.</p>';
  const contact = record.Contact ? `<p><strong>Supplied contact:</strong> ${telephone ? `<a class="contact-link" href="tel:${esc(telephone)}">${esc(record.Contact)}</a>` : `${esc(record.Contact)} <span class="p0-muted">(number format needs confirmation)</span>`}</p>` : '<p><strong>Supplied contact:</strong> Not available in the supplied source.</p>';
  box.innerHTML = `<div class="selection-heading"><div><span class="pill ${category.className}">${esc(category.label)}</span><h2 style="margin-top:7px">${esc(record.Name)}</h2></div><button class="close-selection" aria-label="Close selected listing">×</button></div><p><strong>Source record role:</strong> ${esc(record.recordKindLabel)}<br><strong>Coverage:</strong> ${esc(p0ScopeLabel(record))}</p><p class="address"><strong>Supplied address — not a mapped coordinate:</strong><br>${esc(record.Address)}</p><p class="p0-uncertainty">${esc(p0PrecisionLabel(record))}</p>${contact}${terms}<p><strong>Source remark:</strong> ${esc(p0PublicRemarks(record.Remarks))}</p><p class="p0-uncertainty">Current opening status and documented services have not been independently confirmed for this listing.</p>`;
  box.classList.add('visible');
  box.querySelector('.close-selection').addEventListener('click', () => { state.selectedFacility = null; render(); });
}

function selectFacility(id) {
  const record = facilities.find(item => item.id === id);
  state.selectedFacility = id;
  if (record?.mapRepresentation === 'district_group_summary' && state.selectedDistrict && state.selectedDistrict !== record.mapDistrict) state.selectedDistrict = null;
  if (record?.mapRepresentation === 'coverage_scope_control') state.selectedDistrict = null;
  render();
  document.getElementById('selection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function focusDistrict(name) {
  state.selectedDistrict = state.selectedDistrict === name ? null : name;
  state.coverageScope = '';
  state.selectedFacility = null;
  render();
}

function p0SetCoverageScope(scope) {
  state.coverageScope = state.coverageScope === scope ? '' : scope;
  state.selectedDistrict = null;
  state.selectedFacility = null;
  render();
}

function p0RenderCoverageControls(scopeAgnosticRecords, visibleCoverageRecords) {
  const container = document.getElementById('coverageControls');
  if (!container) return;
  const entries = [
    ['multi_district', 'Punjab-wide / multi-district'],
    ['statewide', 'Statewide information / referral'],
  ].map(([scope, label]) => [scope, label, scopeAgnosticRecords.filter(record => record.coverageScope === scope).length]);
  container.innerHTML = `<p class="section-label">Coverage scopes</p><div class="coverage-buttons">${entries.map(([scope, label, count]) => `<button class="coverage-button ${state.coverageScope === scope ? 'active' : ''}" type="button" data-coverage-scope="${scope}" aria-pressed="${state.coverageScope === scope}">${esc(label)} <span>${count}</span></button>`).join('')}</div><p class="coverage-note">${visibleCoverageRecords.length ? `${visibleCoverageRecords.length} coverage record${visibleCoverageRecords.length === 1 ? '' : 's'} currently shown separately from district groups.` : 'Coverage records are shown separately from district groups.'}</p>`;
  container.querySelectorAll('[data-coverage-scope]').forEach(button => button.addEventListener('click', () => p0SetCoverageScope(button.dataset.coverageScope)));
}

function makeExportSvg() {
  const copy = document.getElementById('map').cloneNode(true);
  copy.setAttribute('xmlns', NS); copy.setAttribute('width', '1040'); copy.setAttribute('height', '850'); copy.setAttribute('style', 'background:#eaf2ed');
  const style = document.createElementNS(NS, 'style'); style.textContent = exportStyleText(); copy.insertBefore(style, copy.firstChild);
  const key = svg('g', { id: 'exportKey', 'aria-hidden': 'true' });
  key.append(svg('rect', { x: 736, y: 634, width: 282, height: 190, fill: '#ffffff', 'fill-opacity': '.96', stroke: '#dce9e1', 'stroke-width': '1' }));
  const title = svg('text', { x: 751, y: 658, fill: '#24543f', 'font-family': 'Arial, sans-serif', 'font-size': '12', 'font-weight': '800', 'letter-spacing': '.7' }); title.textContent = 'MAP INTERPRETATION'; key.append(title);
  key.append(svg('circle', { cx: 760, cy: 682, r: 10, class: 'district-summary-marker' }));
  const groupLabel = svg('text', { x: 778, y: 686, fill: '#284438', 'font-family': 'Arial, sans-serif', 'font-size': '12' }); groupLabel.textContent = 'District-group record count'; key.append(groupLabel);
  const lines = [
    'Records are grouped by reported district',
    'or coverage scope—not facility locations.',
    'Current operation and service details are',
    'not independently confirmed.',
    `Dataset: ${datasetManifest.datasetVersion}`,
  ];
  lines.forEach((line, index) => { const text = svg('text', { x: 751, y: 712 + index * 19, fill: '#50655b', 'font-family': 'Arial, sans-serif', 'font-size': '11' }); text.textContent = line; key.append(text); });
  copy.append(key);
  return copy;
}

function p0CsvCell(value) {
  let text = String(value ?? '');
  if (/^[=+\-@]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

function exportVisible() {
  const columns = [
    ['entry_id', 'id'], ['legacy_id', 'legacyId'], ['name', 'Name'], ['record_kind', 'recordKindLabel'],
    ['source_ownership_claim', 'ownershipLabel'], ['source_terms', 'serviceMentionLabels'], ['coverage_scope', 'coverageScope'],
    ['reported_district_or_scope', 'displayScope'], ['source_district', 'District'], ['source_address', 'Address'],
    ['location_precision', 'locationPrecision'], ['map_representation', 'mapRepresentation'], ['source_type', 'Type'],
    ['phone_display', 'Contact'], ['source_remarks', 'Remarks'], ['source_row', 'sourceRow'], ['dataset_version', 'datasetVersion'],
  ];
  const rows = activeFacilities().map(record => columns.map(([, key]) => Array.isArray(record[key]) ? record[key].join('; ') : record[key] ?? ''));
  const csv = [columns.map(([label]) => label), ...rows].map(row => row.map(p0CsvCell).join(',')).join('\n');
  downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8' }), 'punjab-care-access-directory.csv');
}

function setupControls() {
  state.categories = new Set(P0_FILTER_CATEGORIES);
  state.detailType = '';
  state.coverageScope = '';
  const categoryGrid = document.querySelector('.category-grid');
  categoryGrid.innerHTML = P0_FILTER_CATEGORIES.map(value => {
    const category = p0Category(value);
    return `<button class="filter-button active" type="button" data-category="${value}" aria-pressed="true"><span class="dot" style="background:${category.color}"></span><span>${esc(category.label)}</span><b id="ownership-${value}">0</b></button>`;
  }).join('');
  categoryGrid.querySelectorAll('.filter-button').forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.category;
    state.categories.has(value) ? state.categories.delete(value) : state.categories.add(value);
    button.classList.toggle('active', state.categories.has(value));
    button.setAttribute('aria-pressed', state.categories.has(value));
    render();
  }));
  const typeLabel = [...document.querySelectorAll('.section-label')].find(element => element.textContent.trim() === 'Service type');
  if (typeLabel) typeLabel.textContent = 'Source record role';
  const selector = document.getElementById('typeSelect');
  selector.innerHTML = '<option value="">All source record roles</option>';
  P0_RECORD_KINDS.forEach(([value, label]) => { const option = document.createElement('option'); option.value = value; option.textContent = label; selector.append(option); });
  selector.setAttribute('aria-label', 'Source record role');
  selector.addEventListener('change', () => { state.detailType = selector.value; render(); });
  const coverageControls = document.createElement('section'); coverageControls.id = 'coverageControls'; coverageControls.className = 'coverage-controls';
  categoryGrid.insertAdjacentElement('afterend', coverageControls);
  const map = document.getElementById('map');
  const notice = document.createElement('p'); notice.id = 'p0MapNotice'; notice.className = 'p0-map-notice'; notice.textContent = 'Map shows record counts grouped by reported district or coverage scope—not facility locations.';
  map.insertAdjacentElement('beforebegin', notice);
  const metricFor = id => document.getElementById(id)?.closest('.metric');
  const districtMetric = metricFor('visibleDistricts'); const coverageMetric = metricFor('visibleRegions');
  if (districtMetric?.lastElementChild) districtMetric.lastElementChild.textContent = 'district groups';
  if (coverageMetric?.lastElementChild) coverageMetric.lastElementChild.textContent = 'coverage records';
  document.getElementById('search').addEventListener('input', event => { state.query = event.target.value; render(); });
  const bindings = [['districtLayer', 'showDistricts'], ['districtLabels', 'showDistrictLabels'], ['regionLayer', 'showRegions'], ['regionLabels', 'showRegionLabels'], ['riverLayer', 'showRivers'], ['riverLabels', 'showRiverLabels']];
  bindings.forEach(([id, key]) => document.getElementById(id).addEventListener('change', event => { state[key] = event.target.checked; render(); }));
  document.querySelectorAll('#regionToggles input').forEach(element => element.addEventListener('change', () => { element.checked ? state.regions.add(element.dataset.region) : state.regions.delete(element.dataset.region); render(); }));
  document.getElementById('clearDistrict').addEventListener('click', () => { state.selectedDistrict = null; state.coverageScope = ''; state.selectedFacility = null; render(); });
  document.getElementById('download').addEventListener('click', exportVisible);
  document.getElementById('exportPng').addEventListener('click', downloadMapPng);
  document.getElementById('exportPdf').addEventListener('click', downloadMapPdf);
  document.getElementById('zoomIn').addEventListener('click', () => zoomAt(1.25, W / 2, H / 2));
  document.getElementById('zoomOut').addEventListener('click', () => zoomAt(.8, W / 2, H / 2));
  document.getElementById('resetMap').addEventListener('click', resetMap);
  map.addEventListener('wheel', event => { event.preventDefault(); const point = svgPoint(event); zoomAt(event.deltaY < 0 ? 1.16 : .86, point.x, point.y); }, { passive: false });
  let drag = null;
  map.addEventListener('pointerdown', event => { drag = { x: event.clientX, y: event.clientY, tx: transform.x, ty: transform.y }; map.setPointerCapture(event.pointerId); });
  map.addEventListener('pointermove', event => { if (!drag) return; const rect = map.getBoundingClientRect(); transform.x = drag.tx + (event.clientX - drag.x) * W / rect.width; transform.y = drag.ty + (event.clientY - drag.y) * H / rect.height; updateMapTransform(); });
  map.addEventListener('pointerup', () => { drag = null; });
}

function p0UpdateOwnershipCounts() {
  P0_FILTER_CATEGORIES.forEach(value => {
    const element = document.getElementById(`ownership-${value}`);
    if (element) element.textContent = facilities.filter(record => record.ownershipClaim === value).length;
  });
}
