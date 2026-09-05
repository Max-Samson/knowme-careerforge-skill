# Template bundle contract

Each template contains canvas.html, sample-profile.json, style.css, metadata.json and README.md. canvas.html is the sole maintained HTML structure with explicit named slots and no candidate samples. Generate gallery previews with scripts/build/build-gallery.py using the same instantiator and CSS as actual resumes. sample-profile.json is explicitly fictional gallery input, never a runtime default. Generated previews belong in output, not src/templates.

The instantiator validates slot completeness and context before binding facts once. Shared profile normalization accepts missing/null fields, rejects unknown or mistyped data, and preserves every supplied education, experience and project entry. Escape candidate text before embedding it. Do not use sample-based regex substitution or default candidate achievements.

Inline styles in order: common/base.css, template style.css, common/canvas-bindings.css. Use CSS tokens for tunable spacing and typography; narrow columns must wrap long text and maintain readable contrast. No hidden body text, external assets or image-based body copy.

Each explicit .resume-page represents one A4 page. Two-page layouts need two page containers; the current validator deliberately rejects one oversized root flowing implicitly into multiple pages because per-page content acceptance would otherwise be ambiguous. --expected-pages is a maximum of one or two pages.

Tests must use temporary directories. Verify actual print layout and final PDF text, plus inspect rendered screenshots after geometry changes. Metadata ATS tiers describe design intent, not universal ATS certification. Read common/resume-contract.md and ../../references/07-artifact-contract.md for the complete contract.
