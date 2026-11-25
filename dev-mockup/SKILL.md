---
name: dev-handoff
description: Define, assemble and audit a design handoff bundle — the folder of mockups, tokens and written spec that dev-ui-update consumes. Describes exactly what the bundle must contain (README with dated scope, precedence line, numbered decisions, per-screen specs, gap lists; one authoritative token file; self-rendering mockups with a frame index; frozen reference copies of the plan docs), audits an existing bundle against that contract with a pass/fail report, and renders the mockups to PNG screenshots. Never writes application code and never edits the plan docs in docs/. Use whenever the user wants to prepare, package, export, check, validate or "get ready" a design handoff, asks what a handoff folder should contain, asks whether mockups can be screenshotted, or before running dev-ui-update on a bundle that has not been checked.
---

# Dev Handoff

A design handoff bundle is the one thing that crosses from design into the dev pipeline. `dev-ui-update` reads it, writes `docs/design-system.html` from it, and sweeps the plan. Every gap in the bundle becomes a question in that run, or worse, a guess. This skill defines the bundle, builds or completes one, and audits one before `dev-ui-update` sees it.

## Hard constraints

1. **No application code.** Not even a token-to-CSS converter for the app. The render script in this skill is tooling for screenshots only.
2. **Never invent a design value or decision.** A missing hex, size, frame or decision is reported as missing. Ask the user or the designer; do not fill it from taste, from the base system, or from what the mockup "probably" means.
3. **Never edit the plan docs.** `docs/mvp-plan.html`, `docs/prd.html`, `docs/feature-*.html` and the rest belong to `dev-ui-update` and the other `dev-*` skills. This skill writes only inside the bundle folder.
4. **Do not edit the mockups' design.** Adding a missing runtime file, fixing a broken relative path, or adding a frame ID is packaging. Changing a color, a layout or a label is design, and is the designer's call.
5. **A shipped bundle is frozen.** Once `dev-ui-update` has consolidated it (its README carries the "consolidated into" block), only factual fixes are allowed. A revision is a new bundle with a supersession line, not an edit.

## Where the bundle lives

One folder per handoff, inside the repo:

- First handoff: `docs/design-handoff/`
- Each later handoff: `docs/design-handoff-YYYY-MM-DD/` (or `-v2`, `-v3`), never overwriting the previous bundle.

`dev-ui-update` also recognises `docs/handoff/`, `docs/handoff-*/`, `docs/design/` and `design-handoff*/` at the repo root. Prefer the names above.

## The bundle contract

```
docs/design-handoff/
├── README.md                 REQUIRED  the written spec, most important file
├── tokens.json               REQUIRED  one authoritative token file (or _ds/, below)
├── mockups/                  REQUIRED
│   ├── <Screen>.dc.html  or  <Screen>.html     one file per artboard
│   ├── canvas.json           when the mockups come from a canvas tool
│   └── support.js            REQUIRED if any mockup loads it
├── screenshots/              RECOMMENDED
│   ├── README.md             the frame index (dev-ui-update reads only this)
│   └── <Screen>.png          rendered images, never read by dev-ui-update
├── _ds/<system>-<id>/        OPTIONAL  when built on a published design system
│   ├── styles.css            authoritative token values
│   ├── readme.md             the base system's own guide
│   └── _ds_manifest.json
└── reference/                RECOMMENDED  frozen copies of the plan docs the designer worked against
```

### 1. `README.md` — required sections, in this order

| # | Section | What it must hold | Why |
|---|---|---|---|
| 1 | **Title and metadata** | Product name, bundle date (YYYY-MM-DD), bundle version, designer, link to the live canvas or source file | `dev-ui-update` keys the Handoff log on the date |
| 2 | **Fidelity and precedence** | One line stating fidelity (final / final-ish / exploratory), and the precedence rule verbatim: *"Where a mockup and this README disagree, this README wins."* | Without it, every disagreement becomes a question |
| 3 | **Supersedes** | First handoff: "None." Later handoff: which earlier bundle this replaces, wholly or by section | Drives update mode in `dev-ui-update` |
| 4 | **Base system and deviations** | The design system this builds on (a published system, or a sibling app such as "TheForge"), then a numbered, closed list of rules the app breaks on purpose, each with a reason | Becomes design-system section 3 |
| 5 | **Artboards** | Table: file · frame ID(s) · screen · what it shows · states drawn | Every screen needs a stable ID that survives renames |
| 6 | **Tokens** | Name the authoritative token file. Usage rules only (which token for what); values live in the token file, not repeated here | Avoids the README and the CSS drifting apart |
| 7 | **Typography and icons** | Font families, weights, fallback, role table (role · size / weight · usage); icon set, stroke weight, sizes per context, the full list of icons used, any reserved icon | Implementers transcribe these directly |
| 8 | **Shell** | Window/viewport, top bar, navigation (expanded and collapsed), rails, status bar — each region with width/height and fill token | |
| 9 | **Per-screen specs** | One subsection per screen, headed with its frame ID: layout, measurements in px, anatomy, every state drawn (empty, loading, error, selected, disabled, hover) | The mockup alone is not a spec: measurements must be written, not inferred from inline styles |
| 10 | **Interaction contracts** | Numbered rules that hold everywhere: what opens a menu, what may never auto-commit, undo granularity, drag/drop, keyboard map, timings (durations, delays) | Behavior the static mockups cannot show |
| 11 | **Decisions** | Numbered list of decisions the mockups lock, each naming the plan doc and section it **changes or adds to** (e.g. "changes mvp-plan §Decks: core order") | Becomes the conflict sweep's input |
| 12 | **Details the plan does not state** | Behaviors the mockups show that nobody has agreed yet, for confirm-or-remove | Keeps invented detail from becoming law silently |
| 13 | **Not mocked up** | Screens and states named but undrawn | Becomes design-system section 15 |
| 14 | **Open questions** | Numbered, each with who decides | |
| 15 | **Accessibility** | Contrast targets met, focus style, reduced-motion behavior, minimum hit sizes | |
| 16 | **Assets and licensing** | Fonts (and whether the app must bundle them rather than load them remotely), icon library and version, licenses | |

A section with nothing to say keeps its heading and says "None." An empty heading is information; a missing heading is a gap.

### 2. Token file — exactly one source of values

Either `tokens.json` or `_ds/*/styles.css`. If both exist, the README names which one wins.

`tokens.json` must cover:

- `name`, `source` (canvas link), `date`
- `fonts` — family, weights, and the bundling rule
- `modes` — every color role for **each** mode (dark, light): bg, surfaces, borders, text ramp (normal / muted / disabled)
- `themeColors` — every theme or accent with its text-on-dark and text-on-light variants, and the default
- domain palettes (decks, categories, statuses) with a note on which variant is for fills and which for text/icons
- `space`, `radius`, `elevation` (shadows), `size` (fixed component sizes), `motion` (durations, easings)

Every color that appears in a mockup must be a token, or listed in the README as a one-off with a reason. Values are hex (`#RRGGBB` / `#RRGGBBAA`) or px, never "about 12".

### 3. Mockups — must render without the canvas tool

- One file per artboard. File names are the frame IDs, or the README maps them.
- **Self-rendering.** If a mockup loads a runtime (`<script src="./support.js">`), that file ships in `mockups/`. If it cannot ship, every `{{prop}}` placeholder must have a `default` in the file's `data-props`, so `scripts/render_mockups.py` can render it.
- Fixed size per artboard, from `canvas.json` (`w`, `h`) or the file's `$preview` prop.
- Remote fonts are allowed in mockups only; the README's assets section says what the app bundles.
- Interactive states are drawn open as separate frames (a menu open, a hover ring shown), since the screenshots are static.
- No mockup links to a file that is not in the bundle.

### 4. `screenshots/` — the frame index

`screenshots/README.md` is a table: frame ID · file · screen · state · size · theme/mode. `dev-ui-update` reads this index instead of parsing the canvas, and never opens the images. The PNGs exist for humans and for review.

Render them with `scripts/render_mockups.py` (see below) rather than by hand, so they match the mockup source exactly.

### 5. `reference/` — what the designer worked against

Copies of the plan docs (`mvp-plan.html`, relevant `feature-*.html`) as they were when the designer started, with the date copied. Frozen forever; `docs/` always wins over them. Their value is showing later what the design was answering.

## Mode A: Assemble or complete a bundle

Use when the user has mockups (a canvas link, an export, a folder) and wants them packaged.

1. **Inventory** what exists against the contract above. Report it as a table before writing anything.
2. **Gather** the mockup sources into `mockups/`, and the runtime if any. Read a canvas artifact with the Artifact tool's `read` action, not WebFetch.
3. **Extract tokens** only from values that literally appear in the mockup sources or the designer's token export. List every color found that has no token name, and ask how to name it.
4. **Draft the README** using the 16-section skeleton. Fill only what the designer stated or the mockups literally show. Every inferred item goes into section 12 (details the plan does not state), not into decisions.
5. **Copy `reference/`** from the current `docs/` plan docs, dated today.
6. **Render screenshots** and write `screenshots/README.md`.
7. Run the Mode B audit on the result and report.

## Mode B: Audit a bundle

Use before `dev-ui-update`, or when the user asks whether a bundle is ready. Read-only unless the user approves fixes.

Check each item, and report **PASS / FAIL / N/A** with the evidence (file and line):

**README**
1. Has a date and a version.
2. States fidelity.
3. States the precedence rule (README beats mockups).
4. Has a Supersedes line.
5. Names the base system and lists deviations as a closed, numbered list.
6. Every mockup file appears in the artboard table, and every table row has a file.
7. Every screen has a spec subsection with written measurements.
8. Decisions are numbered and each names the plan doc it changes.
9. Has "details the plan does not state", "not mocked up" and "open questions" sections (even if "None.").

**Tokens**
10. Exactly one authoritative token file, or the README says which wins.
11. Both modes cover the same roles.
12. Every hex in the mockups is a token or a listed one-off. (Grep the mockups for `#[0-9A-Fa-f]{6}` and diff against the token file.)

**Mockups**
13. Every referenced local file (`support.js`, linked `.html`) exists.
14. Every `{{prop}}` has a default, or the runtime ships.
15. Every artboard has a size (`canvas.json` or `$preview`).
16. All mockups render: run the render script, every file produces a PNG and no `{{` survives.

**Consistency — the bundle against itself**
17. Counts in the README match the files (frames, screens, decks, icons).
18. Each README value that a mockup also draws matches the mockup (sizes, colors, labels, icon names). A README color word ("small orange count") that the mockups actually draw in the theme color is a FAIL: say which one is right.
19. Token names are spelled one way everywhere.

**Index and references**
20. `screenshots/README.md` exists and lists every frame.
21. `reference/` exists, or the README says why not.

Close the audit with:
- the FAIL list, each with the smallest fix and whether it is **packaging** (this skill can fix with approval) or **design** (designer or user decides);
- a verdict: **Ready**, **Ready with gaps** (dev-ui-update can run; the gaps become its questions), or **Not ready** (a required file is missing, or the mockups cannot render);
- the next command: `dev-ui-update` when ready.

## Rendering screenshots

`scripts/render_mockups.py` renders every mockup in a bundle to PNG with headless Chromium:

```
python3 -I ~/.claude/skills/dev-handoff/scripts/render_mockups.py <bundle-dir> [--out <dir>] [--chrome <path>] [--prop accent=#4C8DF6]
```

It:
- substitutes each `{{prop}}` with the file's `data-props` default (or a `--prop` override),
- drops a `support.js` include when the file does not exist,
- sizes each shot from `canvas.json` or `$preview`, falling back to 1440×900,
- writes PNGs to `<bundle>/screenshots/` by default (use `--out` to a scratch dir for a dry run),
- prints a per-file line and exits non-zero if any file fails or leaves a `{{` behind.

It works on copies; the mockup sources are never modified. Fonts load from the network, so rendering needs network access. Chromium is found from `--chrome`, `$CHROME`, the Playwright cache (`~/.cache/ms-playwright/chromium-*/`), or `chromium` / `google-chrome` on `PATH`.

After rendering, write or update `screenshots/README.md` from the printed lines. Ask before writing into a bundle that has already been consolidated.
