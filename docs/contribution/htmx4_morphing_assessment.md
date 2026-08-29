# Assessment: htmx 4 morphing vs. HStream's swap-on-rerun

_Scope: what htmx 4.0 (released 28 Aug 2026, morphing built into core) changes for
HStream's "re-run the whole script on every input, then diff-and-swap" model.
Companion to [`update_strategies.md`](./update_strategies.md)._

## TL;DR

- **Net positive, and partly forced on us.** The template already loads
  `htmx.org@latest`, so htmx 4 is being pulled *today* — this is a migration to
  plan, not a hypothetical.
- **The big win is for inputs.** htmx 4 protects focused inputs and preserves
  unfocused input values across a morph. Those are exactly the two problems the
  `focusout`/`hx-swap="none"` component wiring and half of the `pick_a_strategy`
  machinery exist to work around.
- **It does not replace the whole strategy engine.** The progressive-render paths
  (append while a long script is still running, don't-clobber-partially-rendered)
  are orthogonal to morphing and stay.
- **Low risk for us specifically:** no Alpine → the CSP `style-src` caveat is N/A;
  web-component focus regressions matter only if a user embeds one.

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

1. **Pin versions.** `htmx.org@latest` and unversioned `idiomorph-ext` /
   `path-deps` / `hyperscript` are already live-loading htmx 4. Pin htmx to an
   explicit `4.x` and validate deliberately rather than drifting.
2. **Swap syntax.** `hx-swap="morph:innerHTML"` → `hx-swap="innerMorph"`
   (`format_html.html:67`).
3. **Drop the extension.** Remove the `idiomorph-ext.min.js` `<script>`; confirm
   `path-deps`/`debug` ext paths still resolve under the htmx 4 dist layout.
4. **Revisit input guards.** With focus/value protection, test whether
   `number_input` can move off `focusout` to a live trigger and whether
   `text_input`'s `hx-swap="none"` guard is still needed. This is where the UX
   upgrade (live reactivity) is realized.
5. **Custom components.** If any embed focus-sensitive web components, add
   `hx-morph-skip` and watch #3602/#3590.
6. **Regression-test the strategy engine.** The append/partial paths are the risky
   surface — verify progressive rendering of a slow script still streams correctly.

## Verdict

Meaningfully better for the input/live-validation story that a Streamlit-like tool
lives on, and it lets us delete real workaround code around focus and input values.
It is not a rewrite of the diffing engine — the progressive-render strategies are
orthogonal and stay. Given the template is already on `@latest`, the practical
recommendation is to **pin, migrate the swap syntax deliberately, then relax the
input guards to unlock live reactivity** — capturing the upside on our schedule
instead of inheriting htmx 4 by accident.
