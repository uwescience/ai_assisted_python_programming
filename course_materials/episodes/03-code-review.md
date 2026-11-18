# Episode 3: AI-Assisted Code Review

**Duration:** ~60 minutes
**Learning objective covered:** Conduct a code review using AI assists.
**Prerequisites:** Episode 2: students can trace a GUI interaction through a callback, know the `Survey`/`Question`/`Response` model, and have read `storage.py` directly. They have completed the pre-course LLM basics (VSCode setup, effective prompting, tokens and context), so 3.1 is a review that applies those ideas to code review.
**Materials:** The Survey Manager: Teaching Edition repo; `course_materials/episodes/code/ep3_duplicate_id_starter.py`, with the **instructor-notes section removed** from the copy students receive; `course_materials/prompting_skills.md`; sample data from `python -m scripts.make_sample_data` (two surveys, five responses each).

By the end of this episode, students will have (1) reviewed a realistic AI-written change on its own `git` branch, (2) found where in the code a respondent's ID is checked and stored, (3) run an AI-assisted review and graded its findings against their own, and (4) run the app to test whether the change does what it claims, which settles questions the diff alone can't.

The change under review is a first draft of **"check for a duplicate survey-taker ID,"** written the way an AI assistant plausibly would on a first pass. Students **review** it; they don't fix it. Episode 5 implements the same feature properly, so everything found here becomes the requirements list for that episode.

The main lesson: **a code review is only as good as the context it's given.** An AI that reviews only the diff will miss things that one given the right surrounding files will catch. And neither replaces running the app to check the change's central claim.

---

## Before class (instructor prep, ~10 min)

1. On the starter repo, create a branch `ep3-duplicate-id` from `main`.
2. Add `has_duplicate_respondent_id` from the starter file to `src/form_logic.py`, and add `from src.storage import load_responses` to that module's imports.
3. In `src/app.py`, import it next to `is_valid_respondent_id`. Insert the starter's duplicate-check block into `submit_survey_response` directly **after** the `if load_survey(survey_id) is None:` check and **before** the existing `is_valid_respondent_id` check, so the order matches the excerpt. Mark both insertions with `#A2#` comments.
4. Commit with the message `Reject duplicate respondent IDs on submit` and push the branch. Students check out this branch. They don't receive the instructor notes.
5. Run `pytest` on the branch and confirm it still passes, including `tests/test_guardrails.py` (still five callbacks, still under 800 lines). Nothing tests the new function, and that gap is a review finding in itself, picked up in episode 4.

---

## 3.1 Review of LLM basics, applied to code review (15 min)

### Prompts, tokens, context (5 min)

Students already know these terms. Spend the time on what each means **for a review**:

- **Context is everything the model can see.** A reviewer that sees only the diff doesn't know what `r.id` is. That's defined in `models.py`, which isn't in the diff. A reviewer can't flag a mistake about something it can't see.
- **Tokens make context a budget.** Show rough sizes: all of `src/` in the teaching edition is about 18,500 characters (~4,500 tokens), and `models.py` plus `storage.py` are about 1,000 tokens together. Pasting the whole repo works for an app this small, but not for a real one, and even here a larger context dilutes the model's attention. The skill is choosing the **right** files: the diff plus the definitions it depends on.
- **Prompts set the reviewer's job.** Return to `prompting_skills.md` (role, context, specific request, precise references). "Review this" gets generic style comments. "Is each field this function compares the one the docstring promises?" gets the bug.

### Setup in VSCode (5 min)

Get everyone to the same working state. Ask them to raise a hand at each step if anything goes wrong.

- The AI assistant from the pre-course setup is open in VSCode and can read files in the workspace.
- The repo is cloned and the terminal is in the repo's root folder.
- `python -m src.app` starts the app at `http://127.0.0.1:8052`. Leave it running for 3.4.

### `git` best practices for AI-assisted work (5 min)

- **Separate branch.** AI-written changes live on their own branch (`ep3-duplicate-id`), never directly on `main`. If the change is bad, deleting the branch undoes it.
- **Review the diff, not the files.** Run `git diff main...ep3-duplicate-id`. The three-dot form shows only what the branch changed relative to where it started. The diff is the review's subject, and the tool to hand an AI as its starting context.
- **Small, single-purpose commits.** One feature per commit makes the diff short enough to review well, whether by a human or an AI.
- **Nothing merges unreviewed.** That includes code the AI wrote. The AI that wrote it is a poor reviewer of it, because it has the same blind spots.

**Activity:** every student checks out the branch and saves the diff to a file:

```bash
git fetch origin
git switch ep3-duplicate-id
git diff main...ep3-duplicate-id > ep3.diff
```

---

## 3.2 Coding task: where in the code is the ID checked? (10 min)

**Human pass first (5 min, no AI).** Read `ep3.diff` and answer on paper:

1. When the respondent clicks **Submit**, which callback runs, and in what order does it now check things?
2. `has_duplicate_respondent_id` compares `r.id`. What is `r`, and what is in its `id` field? (Students should open `models.py` to answer this. That's the point.)
3. Where does a respondent's ID come from, and what stops them from typing anything they like?

**Then the AI-assisted trace (5 min).** Students use the same tracing technique as episode 2's 2.5:

> I'm reviewing the change in `ep3.diff`. When I click "Submit" in the Survey Taker tab, trace exactly what happens: which `@callback` in `src/app.py` fires, what its `Input`/`State`/`Output`s are, and every check it makes before `save_response` writes to disk, in order. For each field the new code compares, tell me which class it belongs to in `src/models.py` and how its value is generated.

**Expected answers**, for the instructor to check against:

1. `submit_survey_response`. The checks in order are: the survey still exists (`load_survey`), then the **new** duplicate check, then the **existing** `is_valid_respondent_id`. (There's no `n_clicks` guard; `prevent_initial_call=True` handles the page-load case, as episode 2 showed. If the AI claims a guard exists, that's a "wrong" for later.)
2. `r` is a `Response`. `r.id` is the internal id, `generate_id("resp_")`, a value like `resp_1a2b3c4d`. The ID the respondent types is `r.respondent_id`.
3. The respondent types it. The field in `survey_taker.py` starts empty and has `maxLength=5`; `is_valid_respondent_id` then requires exactly five digits. Nothing ties an ID to a person.

If a student's paper answer to question 2 was "the respondent's ID," don't correct them yet. That mistake is exactly what 3.3 is built to catch.

---

## 3.3 The AI-assisted review (15 min)

Run the review **twice**, with different context, and compare the results. The difference between the two runs is the lesson.

**Run A: diff only (4 min).** Students start a **fresh** AI session (so it hasn't seen the 3.2 trace), attach or paste only `ep3.diff`, and ask:

> You are a senior Python reviewer. Review this diff for correctness bugs, ranked most severe first. For each, give the line, the failure scenario, and a suggested fix.

**Run B: diff plus the definitions it depends on (4 min).** In a new session, students attach `ep3.diff`, `src/models.py`, `src/storage.py`, and `src/form_logic.py`, and ask:

> You are a senior Python reviewer. The attached diff adds duplicate-ID rejection to Survey Taker submissions. The other attached files define every type and storage function the diff uses. Review the diff for correctness bugs, ranked most severe first. For each, give the line, a concrete failure scenario (specific inputs and what goes wrong), and a suggested fix. For every field the diff compares, confirm against `models.py` that it's the field the docstring promises. List any assumptions the diff makes that a spec should settle.

**Grade the reviews (7 min).** Reveal the findings list below and have each student mark both runs as **found**, **missed**, or **wrong**. Wrong means a confident finding that isn't true. Treat that category seriously, because a reviewer that produces confident false findings wastes the developer's time.

| # | Finding | Kind | Where |
|---|---|---|---|
| 1 | Compares `r.id` (the internal `resp_…` id) instead of `r.respondent_id`. The two can never be equal, so the function **always returns `False`** and the feature does nothing. | Bug (headline) | `has_duplicate_respondent_id` |
| 2 | The duplicate check runs **before** format validation. Today this is harmless only because every saved `respondent_id` already passed `is_valid_respondent_id`; a response file with `respondent_id: ""` (hand-edited or imported — `from_dict` accepts it) would make a blank submission say "already used" instead of "must be 5 digits." It also reads every response file for input that will be rejected anyway. Validate format first, uniqueness second. | Fragile ordering | Call order in `submit_survey_response` |
| 3 | The function does file I/O but lives in `form_logic.py`, whose docstring promises "No Dash, no files, so they're easy to test." It belongs in `storage.py`, or the callback should pass the responses in. | Design (placement) | `form_logic.py` imports |
| 4 | Is uniqueness per survey (`load_responses(survey_id)`) or across all surveys? The spec doesn't say. A good review flags this as an assumption to confirm rather than picking one silently. | Design question | `has_duplicate_respondent_id` |
| 5 | Respondents type their own ID. Once bug 1 is fixed, a typo — or someone else using your ID first — locks you out, and the rejection message confirms to anyone that a given ID has been used. Who resolves a lockout? | Design consequence | Interaction with `survey_taker.py` |
| 6 | No tests were added for the new function. | Process | Whole diff |

Expected pattern, which isn't guaranteed and is worth discussing either way: Run A often finds 2, 4, and 6 but misses 1, or guesses at 1 while hedging, because it has never seen `Response`. Run B usually finds 1, and can find 3 because it sees `form_logic.py`'s docstring. Finding 5 needs `survey_taker.py`, which neither run was given. Ask the room: **what would you have to attach for the AI to find 5?**

Watch for the "wrong" category on finding 2: an AI may present it as a live bug ("a blank ID will be rejected as a duplicate"). Ask the student for the input that makes it fail in the current app — there isn't one, because no saved response has a blank ID. Severity claims need the same verification as the findings themselves.

Reviews that diverge are useful. If one AI flags something the table doesn't list, have the student check it against the code before accepting or dismissing it. Possible extra findings worth crediting are a check-then-write race between two simultaneous submits and the cost of `load_responses` reading every response file on each submit. Both are real but low priority for this app.

**Deliverable:** each student's graded table (found, missed, or wrong for runs A and B), plus one sentence on what context made the difference.

---

## 3.4 Does it do what it claims? Run it. (10 min)

So far, everything has come from reading. Now students **use the app** to test the change's one promise: a second submission with the same ID is rejected.

1. In the running app, open **Survey Taker**, choose a survey, type the ID `11111`, answer anything, and click **Submit**. The green thank-you message appears and Submit is disabled.
2. Reload the page (or choose a different survey and then this one again) to get a fresh form. Choose the same survey, type `11111` again, and click **Submit**.
3. Before anyone clicks, ask: *what should the respondent see?* (The orange "⚠️ That ID has already been used for this survey." message, and nothing saved.)

**What actually happens:** the second submission is accepted with the same thank-you message. Confirm with `ls data/responses/<survey_id>/` and open the two newest files: two responses, both with `"respondent_id": "11111"`. The Survey Analyzer's table shows both rows. The feature does nothing, silently — no error, no warning, and `pytest` still passes.

**Then ask why** (have students give the AI `src/app.py`, `src/form_logic.py` and `src/models.py`):

> I submitted the same respondent ID twice to one survey on this branch, and both responses were saved. Trace `has_duplicate_respondent_id` with the values from my second submission and explain why it returned `False`.

This is bug 1 again, reached from the other direction. Students who missed it in 3.2 and 3.3 find it here in about a minute, without having read `models.py` at all.

**While the app is open, one more thing reading won't show:** try typing a six-digit ID such as `123456`. The field stops at five characters (`maxLength=5` in `survey_taker.py`), so a too-long ID never reaches `is_valid_respondent_id` and never gets the "must be 5 digits" message — the browser silently truncates it. Reading `is_valid_respondent_id` alone suggests otherwise. Ask: is silently dropping the last digit the behavior we want once IDs must be unique? (It means a respondent who mistypes can end up with someone else's ID — feeding finding 5.)

**Takeaways:**

- **Test the claim, not just the code.** The change says "reject duplicate IDs." The cheapest possible check — submit the same ID twice — refutes it. A review that never tries the feature can approve a change that does nothing.
- **Running and reading find different things.** Reading found the placement and ordering problems (2, 3), which running can't show. Running proved bug 1 beyond argument and exposed the `maxLength` behavior, which isn't in any Python file the reviewers were given.
- This mirrors episode 2's rule: **an AI's account of the code is a hypothesis; running the app is the test.**

**Deliverable:** a short addition to the 3.3 table, labeled "found by running": the steps, what was saved (the two response files), and the `maxLength` observation.

---

## Wrap-up check (last 5 min, informal)

Ask the room, cold: *"You're about to ask an AI to review a 40-line diff. What do you attach, and what do you do after it answers?"*

A good answer covers three things without prompting:

- **Attach** the diff plus the definitions it uses: the classes in `models.py` it reads fields from, the functions it calls in `storage.py`, and the module it adds code to (here, `form_logic.py`, whose docstring sets the rules).
- **Ask** a specific reviewer's question, such as "does each compared field match its docstring?", rather than "review this."
- **Verify** each finding against the code, then **run** the affected interaction, trying the exact thing the change claims to do.

Close by collecting the room's findings into one list (1–6 plus the "found by running" notes). That list is the starting spec for episode 5, where students implement duplicate-ID checking properly.
