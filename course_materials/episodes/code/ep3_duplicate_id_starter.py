"""Episode 3 starter code: "Check for duplicate survey taker ID."

This is deliberately flawed. It represents what an AI assistant might hand
back on a first pass if asked to reject a Survey Taker submission whose
respondent ID (Response.respondent_id, checked by is_valid_respondent_id in
src/form_logic.py) has already been used for that survey. It is NOT meant to
be merged anywhere -- it's the artifact students review in the episode 3
exercise, using an AI-assisted code review.

Drop has_duplicate_respondent_id into src/form_logic.py, and wire the excerpt
below into src/app.py's submit_survey_response. Mark both insertions with
#A2# comments.

Context students have at this point: episode 2 (control flow/callbacks, the
Survey/Question/Response data model, reading storage.py directly). They do
NOT yet have a unit-testing episode (that's episode 4) -- this review is
meant to be done by reading, tracing, and reasoning about the code with an
AI assistant's help, and then by running the app.
"""
from __future__ import annotations

from src.storage import load_responses  # type: ignore


def has_duplicate_respondent_id(survey_id: str, respondent_id: str) -> bool:
    """Whether another response to this survey already used respondent_id."""
    responses = load_responses(survey_id)
    return any(r.id == respondent_id for r in responses)


# --- Excerpt: how it gets wired into app.py's submit_survey_response ---
#
# The real callback (src/app.py) first checks that the survey still exists.
# The new duplicate check goes right after that, before the existing
# is_valid_respondent_id check. Everything from is_valid_respondent_id down
# is unchanged and shown only for context.
#
#     if load_survey(survey_id) is None:
#         return html.Div(SURVEY_GONE, style=WARNING), no_update
#     if has_duplicate_respondent_id(survey_id, respondent_id):            #A2#
#         return html.Div("⚠️ That ID has already been used for this survey.", style=WARNING), no_update  #A2#
#     if not is_valid_respondent_id(respondent_id):
#         return html.Div("⚠️ Your ID must be exactly 5 digits.", style=WARNING), no_update
#
#     response = Response(
#         id=generate_id("resp_"),
#         survey_id=survey_id,
#         submitted_at=datetime.now().isoformat(timespec="seconds"),
#         respondent_id=respondent_id,
#         answers=build_response_answers([i["qid"] for i in ids], values),
#     )
#     save_response(response)


# ===========================================================================
# INSTRUCTOR NOTES -- do not hand this section to students before the
# exercise. One bug is live, two problems are structural, and two points are
# design questions to raise, not code bugs.
# ===========================================================================
#
# BUG 1 (inside has_duplicate_respondent_id): compares `r.id` instead of
# `r.respondent_id`. `r.id` is the internally generated response id
# (generate_id("resp_") -> "resp_1a2b3c4d"), which can never equal a 5-digit
# ID -- so the function always returns False and the feature does nothing.
# It LOOKS plausible (both fields are "some kind of id"); you have to read
# what `r.id` is in models.py to catch it by reading. Running the app and
# actually trying a duplicate also exposes it (episode 3.4).
#
# PROBLEM 2 (at the call site): the duplicate check runs BEFORE
# is_valid_respondent_id. In the teaching edition this causes no visible
# failure today: every saved respondent_id passed is_valid_respondent_id, so
# a blank or malformed ID can't match anything and still reaches the format
# message. But the code only works because of that invariant, which the
# duplicate check doesn't own -- a hand-edited or imported response file
# with respondent_id "" (from_dict accepts it) would make a blank submission
# report "already used" instead of "must be 5 digits." It also reads every
# response file for input that's about to be rejected anyway. Validate
# format first, uniqueness second. A reviewer who calls this a live bug in
# the current app should be marked "wrong" -- ask them for the failing input.
#
# PROBLEM 3 (placement): the function does file I/O but lives in
# form_logic.py, whose docstring promises "No Dash, no files, so they're
# easy to test." It belongs in storage.py, or the callback should load the
# responses and pass them in. This matters in episode 4: as written it
# can't be unit-tested without the tmp_storage fixture.
#
# DESIGN QUESTION A: has_duplicate_respondent_id scopes the check to one
# survey (load_responses(survey_id)). Should an ID be unique per survey or
# across every survey? The spec doesn't say. A good review flags this as an
# assumption to confirm rather than silently picking one.
#
# DESIGN QUESTION B: respondents type their own ID (the field in
# survey_taker.py starts empty). Once bug 1 is fixed, a typo -- or someone
# else using your ID first -- locks you out, and the message confirms to
# anyone that a given ID has been used. Who fixes a lockout, and is that
# disclosure acceptable? Finding this needs survey_taker.py.
#
# PROCESS: no test was added for the new function (finding #6 in the
# episode's table; picked up in episode 4).
