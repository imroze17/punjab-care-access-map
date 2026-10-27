/* Provenance-safe helper functions retained from P0; active P1 rendering lives in p1-runtime.js. */
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

function p0Category(value) { return P0_CATEGORY_BY_VALUE.get(value) || P0_CATEGORY_BY_VALUE.get('not_stated'); }
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
function geometryCenter(geometry) {
  const points = [];
  const walk = coordinates => typeof coordinates[0] === 'number' ? points.push(coordinates) : coordinates.forEach(walk);
  walk(geometry.coordinates);
  return [points.reduce((sum, point) => sum + point[1], 0) / points.length, points.reduce((sum, point) => sum + point[0], 0) / points.length];
}
function p0DistrictShortName(name) {
  return name.replace('Sahibzada Ajit Singh Nagar', 'S.A.S. Nagar').replace('Shaheed Bhagat Singh Nagar', 'S.B.S. Nagar').replace('Sri Muktsar Sahib', 'Muktsar');
}
function p0GroupByDistrict(records) {
  const groups = new Map();
  records.filter(record => record.mapRepresentation === 'district_group_summary').forEach(record => {
    if (!groups.has(record.mapDistrict)) groups.set(record.mapDistrict, []);
    groups.get(record.mapDistrict).push(record);
  });
  return groups;
}
