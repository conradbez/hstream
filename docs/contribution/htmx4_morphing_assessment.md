# Assessment: htmx 4 morphing vs. HStream's swap-on-rerun

_Scope: what htmx 4.0 (released 28 Aug 2026, morphing built into core) changes for
HStream's "re-run the whole script on every input, then diff-and-swap" model.
Companion to [`update_strategies.md`](./update_strategies.md)._

## Status

**Migration applied on this branch and verified** (see "Verification" below).
The template now pins `htmx.org@4.0.0`, uses `hx-swap="innerMorph"`, and drops the
idiomorph / path-deps / debug extension scripts.

## TL;DR

- **Net positive.** The big win is for inputs; the cost is small and bounded.
- **The `@latest` pin was a latent risk, not an active break.** `htmx.org@latest`
  currently still resolves to **htmx 2.0.10** — htmx 4.0.0 is published but is not
  yet the npm `latest` tag. So we were not silently on 4 already; the risk was an
  eventual unvalidated major bump. Pinning `@4.0.0` removes that risk either way.
- **The big win is for inputs.** htmx 4 protects focused inputs and preserves
  unfocused input values across a morph. Those are exactly the two problems the
  `focusout`/`hx-swap="none"` component wiring and half of the `pick_a_strategy`
  machinery exist to work around. Verified in a browser (below).
- **It does not replace the whole strategy engine.** The progressive-render paths
  (append while a long script is still running, don't-clobber-partially-rendered)
  are orthogonal to morphing and stay.
- **Low risk for us specifically:** no Alpine → the CSP `style-src` caveat is N/A;
  web-component focus regressions matter only if a user embeds one.
- **One removal to note:** `hx-disabled-elt` no longer exists in htmx 4, so the
  in-flight disabling of inputs/buttons on `#run_hs_dummy` is now a no-op. Harmless
  for correctness (re-runs are idempotent) but worth a follow-up if double-submit
  protection is wanted.

## How HStream swaps today

On every input change: `set_component_value` → `trigger_run_hs_event` → `run_hs`
re-executes the user's whole script → `partial_or_full_html_content` diffs the new
HTML against the last-sent HTML and picks one of four strategies
(full / nothing / partial-replace / partial-append).

Two relevant facts about the current wiring:

1. **`#hs-content` swaps with `hx-swap="morph:innerHTML"`** — idiomorph via the
   `idiomorph-ext.min.js` extension (`hstream/templates/format_html.html:67`).
2. **Inputs are defensively wired against the morph.** `text_input` posts with
   `hx-swap="none"` and `number_input` triggers on `focusout`
   (`components.py:131`, `:165`). This is deliberate: idiomorph reset an input's
   `.value` to the `value` **attribute** on every morph, and could clobber a field
   mid-type. Waiting for `focusout` and never re-swapping the input from its own
   POST are workarounds for that.

So a real chunk of HStream's complexity is idiomorph-shortcoming insurance, not
essential domain logic.

## What htmx 4 changes for us

| htmx 4 feature | Effect on HStream |
| --- | --- |
| Focused input value survives a morph even if the server returns something different | Removes the "typing gets clobbered" failure mode. Enables live triggers (`keyup`/`input`) instead of `focusout`, i.e. Streamlit-style reactivity while typing. |
| Unfocused inputs keep the user's value unless the `value` **attribute** changed | Removes idiomorph's `.value`-reset behaviour that `hx-swap="none"` was guarding against. |
| `innerMorph` / `outerMorph` are core `hx-swap` values; `outerSync` morphs attrs then replaces children | Drop the `idiomorph-ext.min.js` `<script>`; `morph:innerHTML` becomes `innerMorph`. One fewer dependency, one fewer `@latest` surprise. |
| Declarative opt-outs: `hx-morph-skip`, `hx-morph-skip-children` + global selector config | A cleaner way to freeze widgets/custom components than routing them through the partial-replace id bookkeeping. |
| Tuning: `morphIgnore` (attr prefixes), `morphScanLimit` (default 10) | Knobs if positional matching misbehaves on large/repeated component lists. |

The algorithm is still idiomorph's id-map underneath, so **stable `id`s still
matter** — HStream's `container_for_HSSTREAMUSERFILELINE…` ids already provide
exactly that, so we're well-positioned.

## What it does *not* buy us

- **The strategy engine doesn't disappear.** Strategies 3/4 aren't only about
  focus preservation — they also drive *progressive rendering while the script is
  still running* (strategy 3's "DO NOT UPDATE PREVIOUS HTML … useful where a
  script hasn't finished rendering"; strategy 4 appends as the first run builds
  up). Morphing is per-swap DOM reconciliation; it has nothing to say about
  streaming partial output across multiple polled responses. That logic stays.
- **The realistic simplification** is narrower but still worthwhile: once htmx 4
  preserves focus/values, the *steady-state* (script finished) path can lean on
  `innerMorph` of full HTML and shed the input-specific guards, and possibly
  collapse "nothing / partial-replace" for the finished case. The running-script
  append path is untouched.
- **Web components: roughly the same.** htmx issue #3602 reports `outerMorph`
  auto-focusing web components during the swap (breaking focus-dependent
  behaviour), with #3590 asking for "fat morph" full-page-swap focus coverage.
  Only relevant if an HStream user embeds a focus-sensitive web component
  (cf. `test_custom_component.py`); mitigate with `hx-morph-skip` on such nodes.
- **CSP caveat is N/A.** The reported `style-src` violation comes from morph
  reconciling Alpine's inline styles; HStream ships no Alpine (verified — template
  loads only htmx, hyperscript, pico), so this doesn't apply unless a user adds it.

## Concrete migration checklist

- [x] **Pin versions.** `htmx.org@latest` → `htmx.org@4.0.0/dist/htmx.min.js`;
      `hyperscript.org@latest` → `@0.9.13`. Validate deliberately rather than
      drifting on `@latest`.
- [x] **Swap syntax.** `hx-swap="morph:innerHTML"` → `hx-swap="innerMorph"`
      (`format_html.html`).
- [x] **Drop the extensions.** Removed the `idiomorph-ext.min.js`, `path-deps.js`,
      and `debug.js` `<script>`s — morphing is core in htmx 4 and the old
      `dist/ext/*.js` paths 404. Also removed the two `("hx-ext", "debug")` attrs
      in `components.py` (text and file inputs).
- [ ] **Revisit input guards (follow-up).** With focus/value protection, test
      whether `number_input` can move off `focusout` to a live trigger and whether
      `text_input`'s `hx-swap="none"` guard is still needed. This is where the UX
      upgrade (live reactivity) is realized — deliberately left as a separate
      change so this PR is a behaviour-preserving swap.
- [ ] **Custom components (follow-up).** If any embed focus-sensitive web
      components, add `hx-morph-skip` and watch #3602/#3590.
- [ ] **`hx-disabled-elt` replacement (follow-up).** Removed in htmx 4; decide
      whether double-submit protection needs re-implementing.

## Verification

Because this sandbox's browser can't reach the CDN and can't run the Django server
and Chromium simultaneously, the migration was verified in two halves that don't
need both at once (real htmx 4.0.0 served locally to the browser):

**Browser — real htmx 4.0.0, `innerMorph`:**
- `window.htmx.version === "4.0.0"`; the `hx-get` + `hx-swap="innerMorph"` load
  pattern hstream uses populates `#hs-content`, and a subsequent swap morphs it.
- **Focused-input protection (the headline win):** with an input focused and
  `half-typed` in it, firing three `update_content_event`-triggered morphs (echo
  advanced `tick 1`→`tick 4`, so morphs really ran) left the input **still focused
  with its typed value intact** — even though the server returned an empty input
  each time. This is the mid-type clobber that htmx 2 + idiomorph could not
  guarantee. Zero JS page errors throughout.

**Server (in-process, no browser):** template renders with htmx `@4.0.0`,
`innerMorph`, and no idiomorph/path-deps/debug scripts; text/number/checkbox/button/
file components still render valid `hx-post` markup with no `hx-ext="debug"`; the
untouched `pick_a_strategy` still returns full/nothing/append as expected.

> Note on running the app's own Playwright suite (`tests/1_basic_test.py`): it
> loads htmx from unpkg in the browser and starts the server via `conftest.py`, so
> it exercises the same interactions in CI where the browser has network. The
> two-halves approach above is only a sandbox workaround, not a replacement.

## Verdict

Meaningfully better for the input/live-validation story that a Streamlit-like tool
lives on, and it lets us delete real workaround code around focus and input values.
It is not a rewrite of the diffing engine — the progressive-render strategies are
orthogonal and stay. Given the template is already on `@latest`, the practical
recommendation is to **pin, migrate the swap syntax deliberately, then relax the
input guards to unlock live reactivity** — capturing the upside on our schedule
instead of inheriting htmx 4 by accident.
