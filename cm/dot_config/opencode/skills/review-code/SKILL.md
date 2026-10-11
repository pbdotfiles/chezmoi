---
name: review-code
description: Adversarial review of code changes. Use only when user asks for a code review — then MUST be used. Always delegate to the review subagent; never review inline unless the user explicitly says to skip this skill.
---

# Code Review

When the user asks for a review of code.

## Prerequisites

Git is required. If there is no git repository, tell the user.

## Procedure

1. **Determine diff scope.** Translate the user's request into BASE and TARGET refs (commits, branches, or working tree). Use two-dot (`..`) semantics: the subagent always runs `git diff {BASE}..{TARGET}`. If the user wants merge-base semantics (e.g., "review my PR"), resolve the merge base yourself (e.g., `git merge-base origin/main HEAD`) and pass it as BASE. Examples:
   - `"review my changes"` → BASE=HEAD, TARGET=.
   - `"review my PR"` → BASE=`$(git merge-base origin/main HEAD)`, TARGET=HEAD
   - `"review HEAD~3..HEAD"` → pass through as BASE=HEAD~3, TARGET=HEAD
   - `"review commit abc123"` → BASE=abc123~, TARGET=abc123
   - `"diff branch-X vs branch-Y"` → BASE=branch-X, TARGET=branch-Y

2. **Extract FOCUS.** If the user specified what to focus on, capture it verbatim as a free-text instruction. It may be a file path, function name, theme, or subsystem. If not, use `all`.

3. **Extract context.** The user's intent:
   - If OpenCode generated the code under review, extract the problem statement from conversation (goal + constraints — distil without your solution ideas; same rule as review-plan step 1).
   - If the user stated intent directly (e.g., "review my implementation of X"), capture it verbatim.
   - If neither, use `Infer intent from the code changes.`

4. **Resolve mode.** Default to TWO-STEPS (reviewer sketches their own approach before seeing the diff). Use ONE-STEP when the user says `quick`, `fast`, or `single-step`.

5. **Resolve reviewer models.** By default, set no model: a single reviewer inherits the main agent's model. If the user named one or more models, resolve each one: use it verbatim when it is an exact `provider/model` (or `provider/model#variant`) reference; otherwise look up the best match with the `models` tool. If several models match (e.g., the same model under different providers), prefer the provider the user named; if it is still ambiguous, ask the user. Never guess an ID. Each resolved model gets its own reviewer.

6. **Launch one subagent call per reviewer** with the `subagent` tool. With several reviewers, issue all calls in the same message so they run in parallel. Every reviewer gets the identical prompt; only `model` differs.
   - `agent` — `review-code`
   - `model` — resolved model from step 5; omit it for the default
   - `description` — short summary of what's being reviewed (include the model name when there are several reviewers)
   - `prompt` —

   **TWO-STEPS:**
   ```
   CODE REVIEW — TWO-STEPS.
   CONTEXT: {context}
   DIFF: BASE={base} TARGET={target} FOCUS={focus}
   ```

   **ONE-STEP:**
   ```
   CODE REVIEW — ONE-STEP.
   CONTEXT: {context}
   DIFF: BASE={base} TARGET={target} FOCUS={focus}
   ```

7. **Present findings.** Group by severity. For each finding, state whether you agree (and what to change) or disagree (and why). Be intellectually honest — if the reviewer found a valid issue, concede. Do not defend your code out of pride. Highlight Critical and High first.

   With several reviewers, merge their findings into one list instead of presenting each report separately:
   - Deduplicate findings that describe the same issue, and tag each finding with the reviewer(s) that raised it (model name).
   - When reviewers rate the same issue differently, use the highest severity and note the disagreement.
   - Treat findings raised by several reviewers as higher confidence. Verify single-reviewer findings against the code before endorsing them.
   - List direct contradictions between reviewers separately, with your assessment of which side is right.
   - If a reviewer failed or returned nothing usable, say so and continue with the others.
