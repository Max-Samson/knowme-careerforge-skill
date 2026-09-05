# Template selection and readable composition

Select for the candidate's actual amount of content, strongest evidence and explicit preference. A backend title alone does not determine the layout. The ten current IDs below are directory IDs accepted by the pipeline; metadata describes design intent, not visual or ATS certification.

| ID | Structure | Review before choosing |
| --- | --- | --- |
| minimal | Single column | Straight reading order; sparse content needs breathing room rather than compression |
| international-flow | Single column | Consider for linear prose; inspect language and line lengths |
| modern | Sidebar, 32:68 | Keep side content short; check narrow-column wrapping |
| creative-tech | Sidebar, 28:72 | Use only when the visual emphasis suits the user |
| data-analyst | Sidebar, 30:70 | Do not invent metrics to match the template name |
| executive | Banner and split columns | Needs suitable supplied leadership evidence; a title does not confer it |
| classic | Structured table | Check sparse fields and reading order |
| compact-dense | Dense two columns | For substantial supplied content; avoid for a short career description |
| academic-research | Dense single column | Research content must actually be supplied |
| startup-generalist | Modular cards | Check block balance with the actual sections |

Use the existing search when no template was selected:

```bash
python3 <skill-root>/scripts/template/search-template.py "<target role>" --target-pages 1 --summary
```

The summary returns the top three candidates with IDs and layout metadata; the existing `--json` option returns all metadata only when needed. For a simple, sparse resume, prefer a readable single-column structure from the table over a dense sidebar just because it has a higher role score. Do not load every template source or build a gallery for a single resume.

The pipeline also ranks automatically if `--template` is omitted. Ranking does not inspect the final PDF's aesthetics. Inspect the selected output and report `templateUsed`; do not claim that all ten designs were visually compared if only one was rendered.

For experienced candidates, work evidence should be easy to find. Keep skill lists compact; avoid paragraphs claiming proficiency in every role keyword. A summary and a project section are optional, and should not repeat the same achievement. For sparse profiles, preserve honest whitespace, use a simple layout and ask for useful details only when needed. Do not fill a page with generic qualities or fabricated projects. For dense profiles, edit repetition before reducing type size or spacing.

Each template maintains `canvas.html`, `style.css`, `metadata.json`, `README.md` and a fictional `sample-profile.json`. Gallery previews use the same instantiator, combining common/base.css, template style.css and common/canvas-bindings.css. Read source only for a needed layout edit; never load gallery sample content to assemble candidate facts. Token tuning is described in 05-html-canvas-tokens.md. Multiple PDF pages require explicit page containers, regardless of metadata's maximum page count.
