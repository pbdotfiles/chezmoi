---
name: review-plan
description: Adversarial review of an implementation plan. Use only when user asks for a plan review — then MUST be used. Always delegate to the review subagent; never review inline unless the user explicitly says to skip this skill.
---

# Plan Review

When the user explicitly asks for a review of an implementation plan.

## Procedure

1. **Extract the plan and problem statement** from the conversation. The plan is whatever you and the user have discussed — the architecture, steps, tradeoffs, decisions. The problem statement is the user's goal, distilled without your solution ideas. Include relevant constraints (language, framework, dependencies).

2. **Resolve reviewer**: if the user said `glm` or `glm-5.1` → `review-plan-glm`; otherwise → `review-plan`. These are subagent names — use the resolved name as the `subagent_type` in the `task` call in step 4.

3. **Resolve mode**. There are two modes: TWO-STEPS (reviewer builds an alternative plan blind, then compares) and ONE-STEP (reviewer reads the plan and critiques it directly). Default to TWO-STEPS. Use ONE-STEP only when the user explicitly asked for a single-step review.

4. **Launch a single subagent call with the `task` tool**:

  Write the full plan to `/tmp/opencode/review-plan-{Date.now()}.md`. This keeps the reviewer's blind phase truly blind — the plan is only accessible when the reviewer calls `read()` on the file.

  Set `subagent_type` to the resolved reviewer, `description` to a short summary, and `prompt` to:

  **TWO-STEPS:**
  ```
  PLAN REVIEW — TWO-STEPS.
  PROBLEM: {problem_statement}
  CONSTRAINTS: {constraints}
  PLAN PATH: /tmp/opencode/review-plan-{Date.now()}.md
  ```

  **ONE-STEP:**
  ```
  PLAN REVIEW — ONE-STEP.
  PROBLEM: {problem_statement}
  CONSTRAINTS: {constraints}
  PLAN PATH: /tmp/opencode/review-plan-{Date.now()}.md
  ```

5. **Process the response**: present the reviewer's findings to the user. For each finding, state whether you agree (and what to change) or disagree (and why). Be intellectually honest — if the reviewer found a valid issue, concede. Do not defend your work out of pride. Highlight Critical and High first.
