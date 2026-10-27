/* P1 runtime: list-first navigation, accessible state, and safe static sharing. */
const P1_MESSAGES = localeMessages || {};
const P1_DISTRICTS = (districtAliases?.districts || []).map(item => item.name);
const P1_ROLE_VALUES = new Set(P0_RECORD_KINDS.map(([value]) => value));
const P1_SCOPE_VALUES = new Set(['statewide', 'multi_district']);
let p1LastTrigger = null;
let p1LastStatus = '';
let p1SearchTimer = null;

function t(key, fallbackOrReplacements = {}, replacements = {}) {
  const suppliedReplacements = fallbackOrReplacements && typeof fallbackOrReplacements === 'object' ? fallbackOrReplacements : replacements;
  let value = P1_MESSAGES[key];
  if (typeof value !== 'string' || !value.trim()) throw new Error(`Missing required approved English message: ${key}`);
  Object.entries(suppliedReplacements).forEach(([name, replacement]) => { value = value.replaceAll(`{${name}}`, String(replacement)); });
  return value;
}

function p1Normalize(value = '') {
  return String(value).normalize('NFKC').toLocaleLowerCase('en').replace(/[\u0300-\u036f]/g, '').replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

function p1Tokens(value = '') { return p1Normalize(value).split(' ').filter(Boolean); }

function p1AliasesForDistrict(district) {
  return (districtAliases?.districts || []).find(item => item.name === district)?.aliases || [];
}

function p1RecordSearchText(record) {
  return [
    record.Name, record.District, record.mapDistrict, ...p1AliasesForDistrict(record.mapDistrict),
    record.Address, record.Type, record.Remarks, record.recordKindLabel, ...(record.serviceMentionLabels || []),
  ].join(' ');
}

function p1MatchesQuery(record, query) {
  const tokens = p1Tokens(query);
  if (!tokens.length) return true;
  const haystack = p1Normalize(p1RecordSearchText(record));
  return tokens.every(token => haystack.includes(token));
}

function p1ActiveFacilities(ignoreCoverageScope = false) {
  return facilities.filter(record => (
    state.categories.has(record.ownershipClaim)
    && (!state.detailType || record.recordKind === state.detailType)
    && (!state.sourceTerm || (record.serviceMentionLabels || []).includes(state.sourceTerm))
    && (!state.selectedDistrict || record.mapDistrict === state.selectedDistrict)
    && (ignoreCoverageScope || !state.coverageScope || record.coverageScope === state.coverageScope)
    && p1MatchesQuery(record, state.query)
  ));
}

function activeFacilities(ignoreCoverageScope = false) { return p1ActiveFacilities(ignoreCoverageScope); }

function p1Status(message) {
  if (!message || message === p1LastStatus) return;
  p1LastStatus = message;
  const status = document.getElementById('appStatus');
  if (status) status.textContent = message;
}

function p1FilterSummary() {
  const parts = [];
  if (state.selectedDistrict) parts.push(`district: ${state.selectedDistrict}`);
  if (state.detailType) parts.push(`role: ${P0_RECORD_KINDS.find(([value]) => value === state.detailType)?.[1] || state.detailType}`);
  if (state.sourceTerm) parts.push(`source term: ${state.sourceTerm}`);
  if (state.coverageScope) parts.push(state.coverageScope === 'statewide' ? 'statewide coverage' : 'Punjab-wide / multi-district coverage');
  if (state.query.trim()) parts.push(`search: ${state.query.trim()}`);
  if (state.categories.size !== P0_FILTER_CATEGORIES.length) parts.push('source ownership claim');
  return parts;
}

function p1FilterSummaryText() {
  const parts = p1FilterSummary();
  return parts.length ? parts.join('; ') : 'all directory records';
}

function p1SetBodyView() {
  document.querySelector('.app')?.setAttribute('data-view', state.view);
  document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === state.view)));
}

function p1ValidateState(raw = new URLSearchParams(location.search)) {
  const categories = new Set(P0_FILTER_CATEGORIES);
  const ownership = raw.get('ownership');
  if (ownership) {
    const requested = ownership.split(',').filter(value => P0_FILTER_CATEGORIES.includes(value));
    if (requested.length) { categories.clear(); requested.forEach(value => categories.add(value)); }
  }
  const district = raw.get('district');
  const role = raw.get('role');
  const term = raw.get('term');
  const scope = raw.get('scope');
  const entry = raw.get('entry');
  const view = raw.get('view');
  const query = (raw.get('q') || '').trim().slice(0, 120);
  return {
    categories,
    selectedDistrict: P1_DISTRICTS.includes(district) ? district : null,
    detailType: P1_ROLE_VALUES.has(role) ? role : '',
    sourceTerm: facilities.some(record => (record.serviceMentionLabels || []).includes(term)) ? term : '',
    coverageScope: P1_SCOPE_VALUES.has(scope) ? scope : '',
    selectedFacility: facilities.some(record => record.id === entry) ? entry : null,
    view: view === 'map' ? 'map' : 'list',
    query,
    invalidEntry: Boolean(entry && !facilities.some(record => record.id === entry)),
  };
}

function p1ApplyUrlState(announceInvalid = false) {
  const parsed = p1ValidateState();
  state.categories = parsed.categories;
  state.selectedDistrict = parsed.selectedDistrict;
  state.detailType = parsed.detailType;
  state.sourceTerm = parsed.sourceTerm;
  state.coverageScope = parsed.coverageScope;
  state.selectedFacility = parsed.selectedFacility;
  state.view = parsed.view;
  state.query = parsed.query;
  const selectionNoLongerMatches = !p1CurrentSelectionIsVisible(p1ActiveFacilities());
  if (selectionNoLongerMatches) state.selectedFacility = null;
  const search = document.getElementById('search');
  const district = document.getElementById('districtSelect');
  const role = document.getElementById('typeSelect');
  const term = document.getElementById('sourceTermSelect');
  if (search) search.value = state.query;
  if (district) district.value = state.selectedDistrict || '';
  if (role) role.value = state.detailType;
  if (term) term.value = state.sourceTerm;
  p1SyncInputs();
  if (announceInvalid && parsed.invalidEntry) p1Status(t('invalidListing', 'That listing may have changed or is no longer available in this directory.'));
  else if (announceInvalid && selectionNoLongerMatches) p1Status(t('selectedNoLongerMatches', 'The selected listing no longer matches the active filters.'));
}

function p1WriteUrl(mode = 'replace') {
  const params = new URLSearchParams();
  if (state.query.trim()) params.set('q', state.query.trim());
  if (state.selectedDistrict) params.set('district', state.selectedDistrict);
  if (state.detailType) params.set('role', state.detailType);
  if (state.sourceTerm) params.set('term', state.sourceTerm);
  if (state.coverageScope) params.set('scope', state.coverageScope);
  if (state.selectedFacility) params.set('entry', state.selectedFacility);
  if (state.view === 'map') params.set('view', 'map');
  if (state.categories.size !== P0_FILTER_CATEGORIES.length) params.set('ownership', [...state.categories].join(','));
  const next = `${location.pathname}${params.toString() ? `?${params.toString()}` : ''}${location.hash}`;
  if (mode === 'push') history.pushState({}, '', next); else history.replaceState({}, '', next);
}

function p1CurrentSelectionIsVisible(active) {
  return !state.selectedFacility || active.some(record => record.id === state.selectedFacility);
}

function p1AfterStateChange({ url = 'push', announce = '' } = {}) {
  const active = p1ActiveFacilities();
  if (!p1CurrentSelectionIsVisible(active)) {
    state.selectedFacility = null;
    announce = t('selectedNoLongerMatches', 'The selected listing no longer matches the active filters.');
  }
  render();
  p1WriteUrl(url);
  if (announce) p1Status(announce);
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
    regionGroup.append(svg('path', { d: path, class: 'region-wash', fill: regionColors[region], 'data-region': region, 'aria-hidden': 'true' }));
    const district = svg('path', { d: path, class: 'district', 'data-district': name, 'aria-hidden': 'true' });
    district.addEventListener('click', () => p1SetDistrict(name));
    districtGroup.append(district);
    const anchor = labelAnchors[name] || geometryCenter(feature.geometry);
    const [x, y] = project(anchor[0], anchor[1]);
    const label = svg('text', { x, y: y - 2, class: 'district-label', 'data-district-label': name, 'aria-hidden': 'true' });
    label.textContent = p0DistrictShortName(name);
    labelGroup.append(label);
  });
  rivers.forEach(river => {
    const d = river.pts.map((point, index) => {
      const [x, y] = project(point[0], point[1]);
      return `${index ? 'L' : 'M'}${x},${y}`;
    }).join(' ');
    riverGroup.append(svg('path', { d, class: 'river', 'aria-hidden': 'true' }));
    const [x, y] = project(river.label[0], river.label[1]);
    const text = svg('text', { x, y, class: 'river-label', 'aria-hidden': 'true' });
    text.textContent = river.name === 'Kali Bein' ? river.name : `${river.name} River`;
    riverLabelGroup.append(text);
  });
  Object.entries(regionAnchors).forEach(([name, coordinate]) => {
    const [x, y] = project(coordinate[0], coordinate[1]);
    const label = svg('text', { x, y, class: 'region-label', 'data-region-label': name, 'text-anchor': 'middle', 'aria-hidden': 'true' });
    label.textContent = name.toUpperCase();
    regionLabelGroup.append(label);
  });
}

function render() {
  const active = p1ActiveFacilities();
  const scopeAgnostic = p1ActiveFacilities(true);
  const districtGroups = p0GroupByDistrict(active);
  const coverageRecords = active.filter(record => record.mapRepresentation === 'coverage_scope_control');
  document.getElementById('visibleCount').textContent = active.length;
  document.getElementById('headerCount').textContent = facilities.length;
  document.getElementById('resultCount').textContent = `(${active.length})`;
  document.getElementById('visibleDistricts').textContent = districtGroups.size;
  document.getElementById('visibleRegions').textContent = coverageRecords.length;
  p1UpdateOwnershipControls();
  p1RenderDistrictSummaries(districtGroups);
  document.querySelectorAll('.district').forEach(district => {
    const name = district.dataset.district;
    district.style.display = state.showDistricts ? '' : 'none';
    district.classList.toggle('active-district', state.selectedDistrict === name);
  });
  document.querySelectorAll('.region-wash').forEach(path => { path.style.display = state.showRegions && state.regions.has(path.dataset.region) ? '' : 'none'; });
  document.querySelectorAll('.district-label').forEach(label => {
    const count = districtGroups.get(label.dataset.districtLabel)?.length || 0;
    label.style.display = state.showDistrictLabels ? '' : 'none';
    label.textContent = `${p0DistrictShortName(label.dataset.districtLabel)}${count ? ` · ${count}` : ''}`;
  });
  document.querySelectorAll('.region-label').forEach(label => { label.style.display = state.showRegionLabels && state.regions.has(label.dataset.regionLabel) ? '' : 'none'; });
  document.getElementById('riverGroup').style.display = state.showRivers ? '' : 'none';
  document.getElementById('riverLabelGroup').style.display = state.showRivers && state.showRiverLabels ? '' : 'none';
  p1RenderCoverageControls(scopeAgnostic, coverageRecords);
  p1RenderFilterChips();
  p1RenderList(active);
  p1RenderContext(active, coverageRecords);
  p1RenderPrintContext();
  p1RenderSelection();
  p1SetBodyView();
}

function p1RenderPrintContext() {
  const context = document.getElementById('printContext');
  if (!context) return;
  context.textContent = t('printContext', {
    filters: p1FilterSummaryText(),
    datasetVersion: datasetManifest.datasetVersion,
  });
}

function p1RenderDistrictSummaries(districtGroups) {
  const markerGroup = document.getElementById('markerGroup');
  markerGroup.replaceChildren();
  districtGroups.forEach((records, districtName) => {
    const district = districtGeo.features.find(feature => feature.properties.name === districtName);
    if (!district) return;
    const anchor = labelAnchors[districtName] || geometryCenter(district.geometry);
    const [x, y] = project(anchor[0], anchor[1]);
    const group = svg('g', { class: 'district-summary-group', 'data-district-summary': districtName, 'aria-hidden': 'true' });
    const circle = svg('circle', { cx: x, cy: y, r: Math.min(19, 10 + Math.sqrt(records.length) * 2.2), class: 'district-summary-marker' });
    const label = svg('text', { x, y: y + 4, class: 'district-summary-count', 'text-anchor': 'middle', 'aria-hidden': 'true' });
    label.textContent = records.length;
    group.append(circle, label);
    group.addEventListener('click', event => { event.stopPropagation(); p1SetDistrict(districtName); });
    markerGroup.append(group);
  });
}

function p1El(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function p1RenderList(items) {
  const container = document.getElementById('facilityList');
  container.replaceChildren();
  const sorted = [...items].sort((left, right) => p0ScopeLabel(left).localeCompare(p0ScopeLabel(right)) || left.Name.localeCompare(right.Name));
  if (!sorted.length) {
    const isDistrict = Boolean(state.selectedDistrict);
    container.append(p1El('div', 'empty', isDistrict ? t('noLocalListings', 'No listings in this directory match the selected district and filters. This does not establish that services are unavailable.') : t('noMatches', 'No listings in this directory match the selected filters. This does not establish that services are unavailable.')));
    return;
  }
  sorted.forEach(record => {
    const category = p0Category(record.ownershipClaim);
    const card = p1El('article', `facility ${state.selectedFacility === record.id ? 'is-selected' : ''}`);
    const button = p1El('button', 'facility-open');
    button.type = 'button'; button.dataset.facility = record.id; button.setAttribute('aria-pressed', String(state.selectedFacility === record.id));
    const top = p1El('div', 'facility-top');
    const swatch = p1El('span', `swatch ${category.className}`); swatch.setAttribute('aria-hidden', 'true');
    top.append(swatch, p1El('p', 'facility-name', record.Name));
    const meta = p1El('div', 'facility-meta');
    meta.append(p1El('span', `pill ${category.className}`, category.label), p1El('span', '', p0ScopeLabel(record)));
    button.append(top, meta, p1El('p', 'p0-card-role', record.recordKindLabel));
  const terms = record.serviceMentionLabels?.length ? record.serviceMentionLabels.join(', ') : t('noSourceTerms');
  button.append(p1El('p', 'p1-card-line', `${t('sourceTerms')}: ${terms}`));
    button.append(p1El('p', 'p1-card-line', record.Contact ? `${t('suppliedContact', 'Supplied contact — not independently confirmed')}: ${record.Contact}` : t('contactUnavailable', 'Telephone not available in the supplied source.')));
    button.append(p1El('p', 'p1-card-caveat', p0PrecisionLabel(record)));
    button.append(p1El('span', 'p1-card-action', t('viewDetails', 'View details')));
    button.addEventListener('click', () => p1SelectFacility(record.id, button));
    card.append(button); container.append(card);
  });
}

function p1RenderContext(active, coverageRecords) {
  const box = document.getElementById('activeContext');
  const text = document.getElementById('contextText');
  if (state.selectedDistrict) {
    box.classList.add('visible'); text.textContent = `District group: ${state.selectedDistrict}. ${active.length} matching directory record${active.length === 1 ? '' : 's'}; individual service locations are not mapped.`;
  } else if (state.coverageScope) {
    box.classList.add('visible'); text.textContent = coverageRecords.length ? `${coverageRecords.length} coverage record${coverageRecords.length === 1 ? '' : 's'} shown separately from district groups.` : 'No matching coverage records under the current filters.';
  } else { box.classList.remove('visible'); }
}

function p1DetailLine(label, value, className = '') {
  const line = p1El('p', className); const strong = p1El('strong', '', `${label}: `); line.append(strong, document.createTextNode(value)); return line;
}

function p1RenderSelection() {
  const box = document.getElementById('selection');
  box.replaceChildren();
  if (!state.selectedFacility) { box.classList.remove('visible'); return; }
  const record = facilities.find(item => item.id === state.selectedFacility);
  if (!record) { box.classList.remove('visible'); return; }
  const category = p0Category(record.ownershipClaim);
  const headingRow = p1El('div', 'selection-heading');
  const headingWrap = p1El('div'); headingWrap.append(p1El('span', `pill ${category.className}`, category.label));
  const heading = p1El('h2', '', record.Name); heading.id = 'selectionHeading'; heading.tabIndex = -1; headingWrap.append(heading);
  const close = p1El('button', 'close-selection', '×'); close.type = 'button'; close.setAttribute('aria-label', t('closeDetails', 'Close selected listing'));
  close.addEventListener('click', p1CloseSelection);
  headingRow.append(headingWrap, close); box.append(headingRow);
  box.append(p1DetailLine(t('sourceRecordRole'), record.recordKindLabel));
  box.append(p1DetailLine(t('coverage'), p0ScopeLabel(record)));
  box.append(p1DetailLine(t('suppliedAddress'), record.Address, 'address'));
  box.append(p1El('p', 'p0-uncertainty', p0PrecisionLabel(record)));
  box.append(p1DetailLine(t('suppliedContact', 'Supplied contact — not independently confirmed'), record.Contact || t('contactUnavailable', 'Telephone not available in the supplied source.')));
  box.append(p1DetailLine(t('sourceTerms'), record.serviceMentionLabels?.length ? record.serviceMentionLabels.join(', ') : t('notClassified')));
  box.append(p1DetailLine(t('sourceRemark'), p0PublicRemarks(record.Remarks)));
  box.append(p1El('p', 'p0-uncertainty', t('unconfirmedStatus', 'Current opening status and documented services have not been independently confirmed for this listing.')));
  const actionRow = p1El('div', 'selection-actions');
  const share = p1El('button', 'small-action', t('copyLink', 'Copy link')); share.type = 'button'; share.addEventListener('click', p1ShareCurrent);
  actionRow.append(share);
  if (publicConfig?.correctionRoute?.url) {
    const report = p1El('a', 'small-action', 'Report directory information'); report.href = publicConfig.correctionRoute.url; report.rel = 'noopener noreferrer'; report.referrerPolicy = 'no-referrer'; actionRow.append(report);
  } else {
    actionRow.append(p1El('p', 'p1-report-note', t('reportUnavailable', 'A correction route has not yet been approved by the directory owner.')));
  }
  box.append(actionRow); box.classList.add('visible');
}

function p1SelectFacility(id, trigger) {
  const record = facilities.find(item => item.id === id);
  if (!record) return;
  p1LastTrigger = trigger || null;
  state.selectedFacility = id;
  if (record.mapRepresentation === 'district_group_summary' && state.selectedDistrict && state.selectedDistrict !== record.mapDistrict) state.selectedDistrict = null;
  if (record.mapRepresentation === 'coverage_scope_control') state.selectedDistrict = null;
  p1AfterStateChange({ announce: `${record.Name} details opened.` });
  requestAnimationFrame(() => {
    const heading = document.getElementById('selectionHeading');
    if (heading) {
      const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
      heading.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'nearest' }); heading.focus({ preventScroll: true });
    }
  });
}

function selectFacility(id) { p1SelectFacility(id, document.activeElement); }

function p1CloseSelection() {
  const id = state.selectedFacility;
  state.selectedFacility = null; p1AfterStateChange({ announce: 'Selected listing closed.' });
  requestAnimationFrame(() => {
    const replacement = id ? document.querySelector(`[data-facility="${CSS.escape(id)}"]`) : null;
    (replacement || document.getElementById('resultsHeading'))?.focus();
  });
}

function p1SetDistrict(name) {
  state.selectedDistrict = state.selectedDistrict === name ? null : name;
  state.coverageScope = ''; state.selectedFacility = null;
  document.getElementById('districtSelect').value = state.selectedDistrict || '';
  p1AfterStateChange({ announce: state.selectedDistrict ? `District selected: ${state.selectedDistrict}.` : 'District filter cleared.' });
}

function focusDistrict(name) { p1SetDistrict(name); }

function p1SetCoverageScope(scope) {
  state.coverageScope = state.coverageScope === scope ? '' : scope;
  state.selectedDistrict = null; state.selectedFacility = null;
  document.getElementById('districtSelect').value = '';
  p1AfterStateChange({ announce: state.coverageScope ? `${scope === 'statewide' ? 'Statewide' : 'Punjab-wide'} coverage selected.` : 'Coverage scope filter cleared.' });
}

function p0SetCoverageScope(scope) { p1SetCoverageScope(scope); }

function p1RenderCoverageControls(scopeAgnosticRecords, visibleCoverageRecords) {
  const container = document.getElementById('coverageControls');
  container.replaceChildren();
  container.append(p1El('p', 'section-label', t('coverageScopes')));
  const buttons = p1El('div', 'coverage-buttons');
  [['multi_district', 'Punjab-wide / multi-district'], ['statewide', 'Statewide information / referral']].forEach(([scope, label]) => {
    const count = scopeAgnosticRecords.filter(record => record.coverageScope === scope).length;
    const button = p1El('button', `coverage-button ${state.coverageScope === scope ? 'active' : ''}`, label); button.type = 'button'; button.setAttribute('aria-pressed', String(state.coverageScope === scope));
    const countBadge = p1El('span', '', String(count)); button.append(countBadge); button.addEventListener('click', () => p1SetCoverageScope(scope)); buttons.append(button);
  });
  container.append(buttons, p1El('p', 'coverage-note', visibleCoverageRecords.length ? `${visibleCoverageRecords.length} coverage record${visibleCoverageRecords.length === 1 ? '' : 's'} currently shown separately from district groups.` : 'Coverage records are shown separately from district groups.'));
}

function p1RenderFilterChips() {
  const container = document.getElementById('activeFilterChips'); container.replaceChildren();
  const entries = [];
  if (state.selectedDistrict) entries.push(['district', state.selectedDistrict]);
  if (state.detailType) entries.push(['role', P0_RECORD_KINDS.find(([value]) => value === state.detailType)?.[1] || state.detailType]);
  if (state.sourceTerm) entries.push(['term', state.sourceTerm]);
  if (state.coverageScope) entries.push(['scope', state.coverageScope === 'statewide' ? 'Statewide coverage' : 'Punjab-wide / multi-district coverage']);
  if (state.query.trim()) entries.push(['query', `Search: ${state.query.trim()}`]);
  if (state.categories.size !== P0_FILTER_CATEGORIES.length) entries.push(['ownership', 'Source ownership claim']);
  entries.forEach(([kind, label]) => {
    const chip = p1El('button', 'filter-chip', `${label} ×`); chip.type = 'button'; chip.addEventListener('click', () => {
      if (kind === 'district') state.selectedDistrict = null;
      if (kind === 'role') state.detailType = '';
      if (kind === 'term') state.sourceTerm = '';
      if (kind === 'scope') state.coverageScope = '';
      if (kind === 'query') { state.query = ''; document.getElementById('search').value = ''; }
      if (kind === 'ownership') state.categories = new Set(P0_FILTER_CATEGORIES);
      p1SyncInputs(); p1AfterStateChange();
    }); container.append(chip);
  });
}

function p1SyncInputs() {
  document.getElementById('districtSelect').value = state.selectedDistrict || '';
  document.getElementById('typeSelect').value = state.detailType || '';
  document.getElementById('sourceTermSelect').value = state.sourceTerm || '';
  document.querySelectorAll('[data-category]').forEach(button => { const active = state.categories.has(button.dataset.category); button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active)); });
}

function p1UpdateOwnershipControls() {
  P0_FILTER_CATEGORIES.forEach(value => {
    const element = document.getElementById(`ownership-${value}`);
    if (element) element.textContent = facilities.filter(record => record.ownershipClaim === value).length;
  });
}

function p1ClearDirectoryFilters() {
  state.categories = new Set(P0_FILTER_CATEGORIES); state.detailType = ''; state.sourceTerm = ''; state.query = ''; state.selectedDistrict = null; state.coverageScope = ''; state.selectedFacility = null;
  document.getElementById('search').value = ''; p1SyncInputs(); p1AfterStateChange({ announce: 'Directory filters cleared.' });
}

function p1ShareCurrent() {
  const url = location.href;
  const shareData = { title: 'Punjab Care Access Map', text: 'Source-derived directory record link', url };
  if (navigator.share) navigator.share(shareData).then(() => p1Status('Link shared.')).catch(() => {});
  else if (navigator.clipboard?.writeText) navigator.clipboard.writeText(url).then(() => p1Status('Link copied.')).catch(() => p1Status('Copy this link from your browser address bar.'));
  else p1Status('Copy this link from your browser address bar.');
}

function p1VisibleLayerSummary() {
  const layers = [];
  if (state.showRegions) layers.push('cultural-region overlay');
  if (state.showRivers) layers.push('schematic river layer');
  return layers.length ? `Visible layers: ${layers.join(' and ')}; both are orientation aids, not verified service information.` : 'No optional cultural-region or river layer is included.';
}

function makeExportSvg() {
  const copy = document.getElementById('map').cloneNode(true);
  copy.setAttribute('xmlns', NS); copy.setAttribute('width', '1040'); copy.setAttribute('height', '850'); copy.setAttribute('style', 'background:#eaf2ed');
  const style = document.createElementNS(NS, 'style'); style.textContent = exportStyleText(); copy.insertBefore(style, copy.firstChild);
  const key = svg('g', { id: 'exportKey', 'aria-hidden': 'true' });
  key.append(svg('rect', { x: 676, y: 578, width: 342, height: 246, fill: '#ffffff', 'fill-opacity': '.97', stroke: '#dce9e1', 'stroke-width': '1' }));
  const title = svg('text', { x: 692, y: 602, fill: '#24543f', 'font-family': 'Arial, sans-serif', 'font-size': '12', 'font-weight': '800', 'letter-spacing': '.7' }); title.textContent = 'MAP INTERPRETATION'; key.append(title);
  key.append(svg('circle', { cx: 702, cy: 627, r: 10, class: 'district-summary-marker' }));
  const groupLabel = svg('text', { x: 720, y: 631, fill: '#284438', 'font-family': 'Arial, sans-serif', 'font-size': '12' }); groupLabel.textContent = 'District-group directory record count'; key.append(groupLabel);
  const active = p1ActiveFacilities();
  const lines = [
    `Filtered records: ${active.length} (source-derived directory entries)`,
    `Filters: ${p1FilterSummaryText().slice(0, 52)}`,
    'Records are grouped by reported district or coverage scope,',
    'not facility locations. Current operation and service details',
    'are not independently confirmed.',
    `Exported: ${new Date().toISOString().slice(0, 10)} (export date, not verification date)`,
    `Dataset: ${datasetManifest.datasetVersion}`,
    p1VisibleLayerSummary().slice(0, 64),
  ];
  lines.forEach((line, index) => { const text = svg('text', { x: 692, y: 657 + index * 20, fill: '#50655b', 'font-family': 'Arial, sans-serif', 'font-size': '10.5' }); text.textContent = line; key.append(text); });
  copy.append(key); return copy;
}

function p0CsvCell(value) {
  let text = String(value ?? '');
  if (/^\s*[=+\-@]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

function exportVisible() {
  const items = p1ActiveFacilities();
  if (!items.length) { p1Status(t('emptyExport', 'There are no matching directory records to export.')); return; }
  const columns = [
    ['entry_id', 'id'], ['legacy_id', 'legacyId'], ['name', 'Name'], ['record_kind', 'recordKindLabel'],
    ['source_ownership_claim', 'ownershipLabel'], ['source_terms', 'serviceMentionLabels'], ['coverage_scope', 'coverageScope'],
    ['reported_district_or_scope', 'displayScope'], ['source_district', 'District'], ['source_address', 'Address'],
    ['location_precision', 'locationPrecision'], ['map_representation', 'mapRepresentation'], ['source_type', 'Type'],
    ['phone_display_unconfirmed', 'Contact'], ['source_remarks', 'Remarks'], ['source_row', 'sourceRow'], ['dataset_version', 'datasetVersion'],
    ['exported_at', 'exportedAt'], ['filter_summary', 'filterSummary'], ['export_notice', 'exportNotice'],
  ];
  const timestamp = new Date().toISOString();
  const rows = items.map(record => columns.map(([, key]) => {
    const calculated = { exportedAt: timestamp, filterSummary: p1FilterSummaryText(), exportNotice: 'Source-derived directory records; grouped geography is not a facility location; current operation and service details are not independently confirmed.' };
    const value = key in calculated ? calculated[key] : record[key]; return Array.isArray(value) ? value.join('; ') : value ?? '';
  }));
  const csv = [columns.map(([label]) => label), ...rows].map(row => row.map(p0CsvCell).join(',')).join('\n');
  downloadBlob(new Blob([csv], { type: 'text/csv;charset=utf-8' }), 'punjab-care-access-directory.csv');
  p1Status(t('exportSuccess', 'Your export is ready for download.'));
}

async function exportMapCanvas() {
  const copy = makeExportSvg(); const serialized = new XMLSerializer().serializeToString(copy);
  const url = URL.createObjectURL(new Blob([serialized], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    const image = new Image();
    await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = reject; image.src = url; });
    const scale = 2; const canvas = document.createElement('canvas'); canvas.width = 1040 * scale; canvas.height = 850 * scale;
    const context = canvas.getContext('2d'); context.fillStyle = '#eaf2ed'; context.fillRect(0, 0, canvas.width, canvas.height); context.drawImage(image, 0, 0, canvas.width, canvas.height);
    return canvas;
  } finally { URL.revokeObjectURL(url); }
}

async function p1DownloadMap(kind) {
  const button = document.getElementById(kind === 'png' ? 'exportPng' : 'exportPdf'); button.disabled = true; button.textContent = 'Working…';
  try {
    const canvas = await exportMapCanvas();
    if (kind === 'png') {
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png')); if (!blob) throw new Error('PNG conversion returned no data'); downloadBlob(blob, 'punjab-care-access-map.png');
    } else { downloadBlob(pdfBlobFromJpeg(bytesFromDataUrl(canvas.toDataURL('image/jpeg', .92)), canvas.width, canvas.height), 'punjab-care-access-map.pdf'); }
    p1Status(t('exportSuccess', 'Your export is ready for download.'));
  } catch (error) { console.error(error); p1Status(t('exportFailure', 'The export could not be created. Please try again.')); }
  finally { button.disabled = false; button.textContent = kind.toUpperCase(); }
}

async function downloadMapPng() { return p1DownloadMap('png'); }
async function downloadMapPdf() { return p1DownloadMap('pdf'); }

function setupControls() {
  state = {
    categories: new Set(P0_FILTER_CATEGORIES), detailType: '', sourceTerm: '', query: '', selectedDistrict: null, selectedFacility: null, coverageScope: '', view: 'list',
    regions: new Set(), showDistricts: document.getElementById('districtLayer').checked, showDistrictLabels: document.getElementById('districtLabels').checked,
    showRegions: document.getElementById('regionLayer').checked, showRegionLabels: document.getElementById('regionLabels').checked,
    showRivers: document.getElementById('riverLayer').checked, showRiverLabels: document.getElementById('riverLabels').checked,
  };
  document.querySelectorAll('#regionToggles input').forEach(element => { if (element.checked) state.regions.add(element.dataset.region); });
  const categoryGrid = document.querySelector('.category-grid'); categoryGrid.replaceChildren();
  P0_FILTER_CATEGORIES.forEach(value => {
    const category = p0Category(value); const button = p1El('button', 'filter-button active'); button.type = 'button'; button.dataset.category = value; button.setAttribute('aria-pressed', 'true');
    const dot = p1El('span', `dot ${category.className}`); dot.setAttribute('aria-hidden', 'true'); button.append(dot, document.createTextNode(category.label)); const count = p1El('b', '', '0'); count.id = `ownership-${value}`; button.append(count);
    button.addEventListener('click', () => { state.categories.has(value) ? state.categories.delete(value) : state.categories.add(value); p1AfterStateChange(); }); categoryGrid.append(button);
  });
  const districtSelect = document.getElementById('districtSelect'); districtSelect.replaceChildren(p1El('option', '', t('allPunjabDistricts', 'All Punjab districts'))); districtSelect.options[0].value = '';
  P1_DISTRICTS.forEach(name => { const option = p1El('option', '', name); option.value = name; districtSelect.append(option); });
  districtSelect.addEventListener('change', () => { state.selectedDistrict = districtSelect.value || null; state.coverageScope = ''; state.selectedFacility = null; p1AfterStateChange({ announce: state.selectedDistrict ? `District selected: ${state.selectedDistrict}.` : 'District filter cleared.' }); });
  const roleSelect = document.getElementById('typeSelect'); roleSelect.replaceChildren(p1El('option', '', t('allSourceRecordRoles', 'All source record roles'))); roleSelect.options[0].value = '';
  P0_RECORD_KINDS.forEach(([value, label]) => { const option = p1El('option', '', label); option.value = value; roleSelect.append(option); }); roleSelect.setAttribute('aria-label', t('sourceRecordRole', 'Source record role'));
  roleSelect.addEventListener('change', () => { state.detailType = roleSelect.value; p1AfterStateChange(); });
  const termLabel = p1El('div', 'section-label', t('sourceTerms', 'Source terms mentioned')); const termSelect = document.createElement('select'); termSelect.id = 'sourceTermSelect'; termSelect.className = 'type-select'; termSelect.setAttribute('aria-label', t('sourceTerms', 'Source terms mentioned')); termSelect.append(p1El('option', '', t('allSourceTerms', 'All source terms'))); termSelect.options[0].value = '';
  [...new Set(facilities.flatMap(record => record.serviceMentionLabels || []))].sort().forEach(label => { const option = p1El('option', '', label); option.value = label; termSelect.append(option); }); termSelect.addEventListener('change', () => { state.sourceTerm = termSelect.value; p1AfterStateChange(); });
  roleSelect.insertAdjacentElement('afterend', termSelect); termSelect.insertAdjacentElement('beforebegin', termLabel);
  const coverageControls = document.createElement('section'); coverageControls.id = 'coverageControls'; coverageControls.className = 'coverage-controls'; categoryGrid.insertAdjacentElement('afterend', coverageControls);
  const map = document.getElementById('map'); const notice = p1El('p', 'p0-map-notice', t('mapNotice', 'Map shows record counts grouped by reported district or coverage scope—not facility locations.')); notice.id = 'p0MapNotice'; map.insertAdjacentElement('beforebegin', notice);
  const metricFor = id => document.getElementById(id)?.closest('.metric'); const districtMetric = metricFor('visibleDistricts'); const coverageMetric = metricFor('visibleRegions'); if (districtMetric?.lastElementChild) districtMetric.lastElementChild.textContent = 'district groups'; if (coverageMetric?.lastElementChild) coverageMetric.lastElementChild.textContent = 'coverage records';
  document.getElementById('search').addEventListener('input', event => { clearTimeout(p1SearchTimer); p1SearchTimer = setTimeout(() => { state.query = event.target.value.trim().slice(0, 120); p1AfterStateChange({ url: 'replace' }); }, 120); });
  [['districtLayer', 'showDistricts', 'District boundaries'], ['districtLabels', 'showDistrictLabels', 'District labels'], ['regionLayer', 'showRegions', 'Cultural-region wash'], ['regionLabels', 'showRegionLabels', 'Regional labels'], ['riverLayer', 'showRivers', 'Major rivers'], ['riverLabels', 'showRiverLabels', 'River labels']].forEach(([id, key, label]) => { const input = document.getElementById(id); input.setAttribute('aria-label', label); input.addEventListener('change', event => { state[key] = event.target.checked; render(); p1WriteUrl('replace'); }); });
  document.querySelectorAll('#regionToggles input').forEach(element => element.addEventListener('change', () => { element.checked ? state.regions.add(element.dataset.region) : state.regions.delete(element.dataset.region); render(); p1WriteUrl('replace'); }));
  document.getElementById('clearDistrict').addEventListener('click', () => { state.selectedDistrict = null; state.coverageScope = ''; state.selectedFacility = null; p1SyncInputs(); p1AfterStateChange(); });
  document.getElementById('clearFilters').addEventListener('click', p1ClearDirectoryFilters);
  document.getElementById('download').addEventListener('click', exportVisible); document.getElementById('exportPng').addEventListener('click', downloadMapPng); document.getElementById('exportPdf').addEventListener('click', downloadMapPdf); document.getElementById('printDirectory').addEventListener('click', () => window.print());
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => { state.view = button.dataset.view === 'map' ? 'map' : 'list'; p1SetBodyView(); p1WriteUrl('push'); p1Status(`${state.view === 'map' ? 'Map' : 'List'} view selected.`); }));
  document.getElementById('zoomIn').addEventListener('click', () => zoomAt(1.25, W / 2, H / 2)); document.getElementById('zoomOut').addEventListener('click', () => zoomAt(.8, W / 2, H / 2)); document.getElementById('resetMap').addEventListener('click', resetMap);
  map.addEventListener('wheel', event => { event.preventDefault(); const point = svgPoint(event); zoomAt(event.deltaY < 0 ? 1.16 : .86, point.x, point.y); }, { passive: false });
  let drag = null; map.addEventListener('pointerdown', event => { drag = { x: event.clientX, y: event.clientY, tx: transform.x, ty: transform.y }; map.setPointerCapture(event.pointerId); }); map.addEventListener('pointermove', event => { if (!drag) return; const rect = map.getBoundingClientRect(); transform.x = drag.tx + (event.clientX - drag.x) * W / rect.width; transform.y = drag.ty + (event.clientY - drag.y) * H / rect.height; updateMapTransform(); }); map.addEventListener('pointerup', () => { drag = null; });
  window.addEventListener('popstate', () => { p1ApplyUrlState(true); render(); });
  p1ApplyUrlState(true);
}

function p0UpdateOwnershipCounts() { p1UpdateOwnershipControls(); }
