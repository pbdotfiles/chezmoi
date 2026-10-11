---
name: review-plan
description: Adversarial review of an implementation plan. Use only when user asks for a plan review — then MUST be used. Always delegate to the review subagent; never review inline unless the user explicitly says to skip this skill.
---

# Plan Review

When the user explicitly asks for a review of an implementation plan.

## Procedure

1. **Extract the plan and problem statement** from the conversation. The plan is whatever you and the user have discussed — the architecture, steps, tradeoffs, decisions. The problem statement is the user's goal, distilled without your solution ideas. Include relevant constraints (language, framework, dependencies).

2. **Resolve reviewer model**. By default, set no model: the reviewer inherits the main agent's model. If the user named a model, use it verbatim when it is an exact `provider/model` (or `provider/model#variant`) reference; otherwise look up the best match with the `models` tool. Never guess an ID.

3. **Resolve mode**. There are two modes: TWO-STEPS (reviewer builds an alternative plan blind, then compares) and ONE-STEP (reviewer reads the plan and critiques it directly). Default to TWO-STEPS. Use ONE-STEP only when the user explicitly asked for a single-step review.

4. **Launch a single subagent call with the `subagent` tool**:

  Write the full plan to `~/.opencode/plan/review-plan-{Date.now()}.md` (OpenCode's plan directory, the only place the Plan agent may write; create it if it doesn't exist). This keeps the reviewer's blind phase truly blind — the plan is only accessible when the reviewer calls `read()` on the file.

  Set `agent` to `review-plan`, `model` to the resolved model (omit it for the default), `description` to a short summary, and `prompt` to:

  **TWO-STEPS:**
  ```
  PLAN REVIEW — TWO-STEPS.
  PROBLEM: {problem_statement}
  CONSTRAINTS: {constraints}
  PLAN PATH: {absolute_path_to_plan_file}
  ```

  **ONE-STEP:**
  ```
  PLAN REVIEW — ONE-STEP.
  PROBLEM: {problem_statement}
  CONSTRAINTS: {constraints}
  PLAN PATH: {absolute_path_to_plan_file}
  ```

  `{absolute_path_to_plan_file}` is the resolved absolute path of the file you just wrote (e.g., `/home/paul/.opencode/plan/review-plan-1781515003994.md`). Expand `~` before launching.

5. **Process the response**: present the reviewer's findings to the user. For each finding, state whether you agree (and what to change) or disagree (and why). Be intellectually honest — if the reviewer found a valid issue, concede. Do not defend your work out of pride. Highlight Critical and High first.
