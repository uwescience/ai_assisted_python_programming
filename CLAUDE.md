# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Materials for a course on AI-assisted Python programming. The running example is the
**Survey Manager: Teaching Edition**, a small Dash app (make a survey, take it, analyze
responses). Course content lives in `course_materials/` (outline, episodes, learning
objectives); design docs live in `docs/` — `docs/teaching_edition_spec.md` is the
authoritative spec for the app, and `docs/data-model.md` describes the information model.

The content was copied in from a sibling repo (`../ai_assisted_coding`, via the `cpd`
helper script) where it lived under `teaching/`. Many docstrings, the README, and the spec
still say "run from the `teaching/` folder" — in this repo, the **repository root** plays
that role. The `teaching/` directory here is empty.

## Commands

Run everything from the repository root.

```bash
source activate.sh                 # activates the `aip/` venv and sets PYTHONPATH
pip install -r requirements.txt
python -m src.app                  # serves on http://127.0.0.1:8052 (PORT in src/constants.py)
python -m scripts.make_sample_data # seeds two surveys with five responses each

pytest                                         # all unit tests (testpaths = tests)
pytest tests/test_taker.py                     # one file
pytest tests/test_taker.py::test_name          # one test

python tests/e2e_check.py   # Playwright browser check; not collected by pytest
                            # needs: pip install playwright && playwright install chromium
```

`activate.sh` also sources `../BaseStack/bin/setup_run.sh`, which may not exist on every
machine; activating `aip/bin/activate` directly is sufficient.

## Architecture

- `src/app.py` builds the Dash app (three tabs) and defines **all** callbacks. Tab
  layouts come from `survey_maker.py`, `survey_taker.py`, `survey_analyzer.py`, which
  only build components (plus `render_survey_form` / `build_results` helpers) — they
  register no callbacks.
- `src/form_logic.py` holds pure, Dash-free helpers (validating Maker rows, respondent
  IDs, assembling answers) so callback logic is unit-testable without a browser.
- `src/models.py`: `Survey`, `Question` (types `text`, `yesno`, `checkbox`), `Response`
  dataclasses with `to_dict`/`from_dict`; `from_dict` silently drops unknown keys.
- `src/storage.py`: JSON persistence — `surveys/<survey_id>.json` and
  `data/responses/<survey_id>/<response_id>.json`, rooted at the repo root via the
  module-level `SURVEYS_DIR` / `RESPONSES_DIR`. Unreadable/invalid JSON loads as `None`.
- `src/constants.py`: every component id. Pattern-matching ids use dicts such as
  `{"type": MAKER_Q_TEXT, "row": i}` and `{"type": ANSWER, "qid": ...}`, read with `ALL`.
- Modules import each other as `from src.x import ...`; `conftest.py` puts the root on
  `sys.path` so tests import the same way.

### Testing conventions

- Use the `tmp_storage` fixture (in `conftest.py`) for anything touching storage; it
  monkeypatches `SURVEYS_DIR`/`RESPONSES_DIR` to a temp dir.
- Callbacks are tested by calling the decorated functions directly with plain values.

### Design constraints enforced by tests (`tests/test_guardrails.py`)

The teaching edition must stay small for students. These are tested — don't break them
without updating the spec:

- Exactly **5** `@callback`s in `src/app.py`: `save_survey_callback`,
  `refresh_survey_lists`, `show_survey`, `submit_survey_response`, `analyze_survey`.
- No `allow_duplicate` and no `MATCH` anywhere in `src/`.
- All of `src/` totals **under 800 lines**.

Decisions behind these (and others, e.g. fixed number of question rows, no "required"
flag, duplicate titles allowed) are recorded in the Decisions section of
`docs/teaching_edition_spec.md`; check it before changing app behavior.
