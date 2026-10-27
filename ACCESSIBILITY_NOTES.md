# Accessibility Notes

## Implemented P1 baseline

The site uses a semantic header, one main content landmark, a skip link to directory results, labelled native selects/search, a polite status region, buttons for all primary filtering actions, visible keyboard focus, a close button for selected details, and List/Map controls on narrow screens. The native district selector is the complete non-map browse path.

The SVG is a visual geographic overview. It does not expose district-count symbols as a required keyboard control. Pointer selection is an enhancement; districts can be selected without the map. Map layers are in a native `details` disclosure and default off for optional cultural-region and river interpretation.

The responsive layout starts with the directory list on narrow screens. Print styles hide visual-only map controls and keep record cards/uncertainty text in the printable directory. CSS includes a reduced-motion preference and primary controls are designed for a minimum 44px target where the compact layout permits it.

## Required human review before representing accessibility as complete

This project has not been certified for WCAG conformance. A qualified reviewer should test the rendered site with a keyboard, at least one desktop screen reader, at least one mobile screen reader/touch device, zoom/reflow, high contrast or forced-colors modes, and current target browsers. Review focus order after selecting and closing a record, dynamically updated status language, map-export labels, printed output, and any future translated strings.

Do not add `aria-live` announcements for every keystroke or map interaction. The current status updates are restrained to applied actions, selection, export completion/failure, and no-results state.
