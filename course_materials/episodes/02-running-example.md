# Episode 2: Running Example

**Duration:** ~60 minutes
**Learning objective covered:** Use AI to understand the structure of an application — (a) how control flow relates to GUI interactions, (b) key data structures, (c) accessing and manipulating application data.
**Prerequisites:** Students have Dash installed and have already written a one-page "Hello World" Dash app (pre-course requirement). They have read `course_materials/dash_programming.md` before class. They can run the app from the repository root (`python -m src.app`, served on http://127.0.0.1:8052) and have seeded sample data with `python -m scripts.make_sample_data` (two surveys, five responses each).
**Materials:** The Survey Manager: Teaching Edition (`src/app.py`, `models.py`, `storage.py`, `survey_maker.py`, `survey_taker.py`, `survey_analyzer.py`, `form_logic.py`, `constants.py`), `docs/data-model.md` (kept hidden from students until the check-your-work step in 2.6), `course_materials/specifications/task_status_hovers.md`.

By the end of this episode, students will have (1) traced one GUI interaction all the way to stored data, (2) produced their own diagram of the app's data model and checked it against the real one, (3) written a short script that reads survey data directly, and (4) shipped one small, real feature (the Survey Maker hover) using that understanding.

Everything in this episode is **exploration and one small build**, not a feature of real scope — that's episodes 5 onward. The point here is to leave with an accurate mental model of the codebase before changing it.

The teaching edition is deliberately small: three tabs, three question types (`text`, `yesno`, `checkbox`), exactly **five** callbacks, and under 800 lines in `src/`. `tests/test_guardrails.py` enforces those limits, and that matters in 2.7.

---

## 2.1 Description of the Survey Manager (5 min)

Walk through the three tabs live (don't just describe them) — Survey Maker, Survey Taker, Survey Analyzer — using the running app. Ask students to notice, without reading code yet: what data must exist for each tab to work? (A survey definition with its questions; a submitted response, tied to a survey and a 5-digit respondent ID.) This primes 2.6 — they'll check their guess against the AI's answer later.

## 2.2–2.4 Dash, widgets, HTML, layout (10 min)

This is review, not new material — students read `dash_programming.md` and already built a Hello World app. Spend this block on:

- A 5-minute live walkthrough of `src/app.py`'s `app.layout` tree: a `dcc.Tabs` with three `dcc.Tab`s, each filled by a layout function (`maker_layout()`, `taker_layout()`, `analyzer_layout()`) from its own module. Point out that tab switching takes no callback at all — `dcc.Tabs` handles it in the browser.
- The "widget namespace" idea: every `id` is how Python code and the browser DOM refer to the same thing, and in this app every id lives in `src/constants.py`. Show the two kinds: plain strings (`MAKER_TITLE = "maker-title"`) and pattern-matching dicts (`{"type": MAKER_Q_TEXT, "row": 2}` for each of the Maker's 5 fixed question rows, `{"type": ANSWER, "qid": ...}` for each answer box in the Taker).
- One quick comprehension check: "Find the `id` of the Survey Title input box in `survey_maker.py`. What would you pass as `Output(...)` if you wanted to write to it?" (Answer: `Output(cn.MAKER_TITLE, "value")`, i.e. `Output("maker-title", "value")`.)

Don't over-invest here — if the room is solid on Hello World, move faster.

## 2.5 Callbacks, and (a) control flow ↔ GUI interactions (15 min)

**Concept (5 min):** Review `Input`/`Output`/`State` from `dash_programming.md` directly against a real callback — `save_survey_callback` in `app.py` is a good pick: one `Input` (the Save button), several `State`s (the title, the description, and every question row's type, text and options, read with `ALL`), and one `Output` (the status message). Then point at `refresh_survey_lists` for the contrast: an `Input` that isn't a button (the `dcc.Tabs` `value`) and two `Output`s from one callback.

The five callbacks are numbered in comments in `app.py`; it's worth having students skim all five before the activity, since there are so few.

**Activity (10 min) — AI-assisted trace, then verify by running it:**

Each student picks one interaction (assign different ones around the room so answers can be compared):

- Clicking "Save Survey" in Survey Maker
- Clicking "Submit" in Survey Taker
- Switching to the Survey Taker tab and choosing a survey from the dropdown

**Prompt to give the AI** (adapt the bracketed interaction):

> I'm learning this codebase. When I [click "Save Survey" in the Survey Maker tab], trace exactly what happens: which `@callback` in `src/app.py` fires, what its `Input`/`State`/`Output`s are, and which helper functions in `form_logic.py` or `storage.py` it calls before anything is written to disk. List the steps in order; don't skip any.

**Then verify, don't just trust it:** run the app, perform the real interaction, and check the AI's trace step by step. Places this app will catch a lazy trace:

- **What fires at page load, and what doesn't.** `save_survey_callback` and `submit_survey_response` have `prevent_initial_call=True`; `refresh_survey_lists` doesn't, and must not — it's what fills the dropdowns when the page first opens. Ask the AI why each one is set the way it is.
- **A dynamically created button doesn't submit on its own.** The Submit button is created by `show_survey` each time a survey is chosen. An AI will often claim `submit_survey_response` needs an `if not n_clicks` guard against firing when the button mounts. Run it and see: choosing a survey saves nothing (`tests/e2e_check.py` checks exactly this). The guard was removed from this edition because the running app showed it wasn't needed.
- **Freshness depends on a tab switch.** A survey saved in the Maker shows up in the Taker's dropdown only because switching tabs triggers `refresh_survey_lists` — no callback ever passes data from one tab to another.
- **Saving twice makes two surveys.** The Maker keeps the form's contents after a save, and each click generates a new `srv_...` id, so clicking Save again creates a second survey with the same title (both appear in the dropdowns). A trace that says "the survey is updated" is wrong.
- **What re-enables Submit.** A successful submit disables the button; choosing a survey again re-renders the whole form, including a fresh, enabled button.

If the AI's trace doesn't mention these where relevant, that's the teaching moment: **an AI's architectural explanation is a hypothesis to test by running the code, not a fact to relay.**

**Deliverable:** a short sequence diagram (mermaid, or even a numbered list) of the chosen interaction, annotated with any place the live behavior differed from the AI's first answer.

## 2.6 Information model — (b) key data structures and (c) accessing/manipulating data (20 min)

**(b) Key data structures (12 min).**

**Prompt:**

> Looking at `src/models.py` and the functions in `src/storage.py`, diagram the relationship between `Survey`, `Question`, and `Response`. Show which fields exist on each, and how `survey_id` connects a `Response` back to its `Survey`. Then explain: why isn't `Question` stored in its own file the way `Survey` is? And what does a value in `Response.answers` look like for each question type?

Students produce their own diagram first (5 min), *then* compare it against `docs/data-model.md` (6 min, now revealed) — which the instructor built the same way. Discuss any mismatch as a group. Common misses:

- A `Question`'s id is a key used inside `Response.answers`, not just an id within its own `Survey` — that's the only link from a response to a question.
- The shape of an answer depends on the question type: a string for `text`, `"Yes"`/`"No"` for `yesno`, a **list** of selected options for `checkbox`. An unanswered question is simply missing from `answers` (see `build_response_answers` in `form_logic.py`), not stored as `None` or `""`.
- `Response` has two ids: `id` (internal, `resp_...`, generated) and `respondent_id` (the 5 digits the person typed). Mixing them up is the bug students will hunt in episode 3's code review.
- The `survey_id` "foreign key" is enforced by directory layout (`data/responses/<survey_id>/`), not by any check.
- `list_surveys()` returns plain dicts with just `id` and `title`, not `Survey` objects — you need `load_survey()` to see the questions.

These are exactly the kind of detail an AI can get wrong on a first pass if not asked to check the actual storage and form-logic code, not just the dataclasses.

**(c) Accessing and manipulating data (8 min).**

**Prompt:**

> Using only the public functions in `src/storage.py` (no Dash, no UI), write a short script that lists every survey with more than N responses, printing each response's `respondent_id` and `submitted_at`. Run it against the sample data in `surveys/` and `data/`.

Students run the script against the app's real on-disk data and confirm the output matches what they see in the Survey Analyzer tab for the same survey (the response count and the raw-responses table). This is their first time touching the data layer directly instead of through the UI — it matters again in episode 4, when they write unit tests against `storage.py` and `form_logic.py` without a running Dash server.

**Deliverable:** the diagram from (b), plus the working script and its output from (c).

## 2.7 (A1) Hands-on: the Survey Maker hover (10 min)

Spec: `course_materials/specifications/task_status_hovers.md` — the Survey Maker should show, on hover, the list of available surveys and the number of questions in each.

There's no starter code for this; students add it. Two facts shape the solution, and the prompt should make the AI confront both:

- `dcc.Tab` has no `title` property, so the native tooltip has to go on an element inside the Maker tab — e.g. the "Make a survey" heading in `maker_layout()`, which `html.H3` supports via `title`. It needs an `id` (added to `constants.py`) so a callback can write to it.
- The app must keep **exactly five** callbacks (`tests/test_guardrails.py`). So the hover can't get a new callback of its own; it has to be another `Output` on an existing one.

**Prompt:**

> I want to add a native browser tooltip to the Survey Maker tab in `src/app.py` showing one line per survey: its title and number of questions. `dcc.Tab` has no `title` property, and `tests/test_guardrails.py` requires exactly five callbacks. Where should `title` go, how should it be kept up to date when a survey is added, and which existing callback should produce it? `list_surveys()` doesn't return question counts — what do I need to call to get them?

The intended answer is a third `Output` on `refresh_survey_lists`, built from `list_surveys()` plus `load_survey()` for each question count. Have students check the alternatives the AI might offer against the code:

- **Set `title` once in `maker_layout()` at import time:** goes stale the moment a survey is added. Have students try it — hover, save a survey, hover again.
- **Add a new callback:** fails `pytest tests/test_guardrails.py`. Run it.
- **Add the `Output` to `save_survey_callback`:** updates on save, but then nothing fills the hover at page load.

With the `refresh_survey_lists` solution, ask: after saving a survey, does the hover update right away? (No — only after a tab switch, for the same reason the Taker dropdown does.) This closes the loop: the same control-flow-to-GUI understanding from 2.5 is what explains when the hover is fresh.

**Deliverable:** a working hover on the Survey Maker tab that reflects the current list of surveys, with `pytest` still passing, committed to their own fork of the repo.

---

## Wrap-up check (last 5 min, informal)

Ask the room, cold: "If I added a new question type tomorrow, which files would you expect to touch, and why?" A good answer names `survey_maker.py` (add it to `QUESTION_TYPES` so the Maker offers it), `survey_taker.py` (`_answer_input`, to render an input for it), and `survey_analyzer.py` (`question_chart`, to chart its answers) — plus `form_logic.py` if the new type has its own validation rule, the way `checkbox` requires at least two options. A sharp answer also notes that `models.py` likely doesn't change, because `Question.type` is a plain string. Saying all this without re-reading the code is the actual signal this episode worked.
