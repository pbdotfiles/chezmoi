---
name: review-plan
description: Adversarial review of an implementation plan. Use only when user asks for a plan review — then MUST be used. Always delegate to the review subagent; never review inline unless the user explicitly says to skip this skill.
---

# Plan Review

When the user explicitly asks for a review of an implementation plan.

## Procedure

1. **Extract the plan and problem statement** from the conversation. The plan is whatever you and the user have discussed — the architecture, steps, tradeoffs, decisions. The problem statement is the user's goal, distilled without your solution ideas. Include relevant constraints (language, framework, dependencies).

2. **Resolve reviewer**. Default is `review-plan` (inherits the main agent's model). Otherwise, pick the agent whose model best matches what the user named — match loosely, then use the resolved name as `subagent_type` in step 4. The available agents are:

   - `review-plan-glm` — opencode-go/glm-5.2
   - `review-plan-deepseek` — opencode-go/deepseek-v4-pro
   - `review-plan-minimax` — opencode-go/minimax-m3
   - `review-plan-qwen3.7-plus` — opencode-go/qwen3.7-plus
   - `review-plan-qwen3.7-max` — opencode-go/qwen3.7-max

   Examples: `glm` or `glm-5.2` → `review-plan-glm`; `qwen` or `qwen plus` or `qwen 3.7 plus` → `review-plan-qwen3.7-plus`; `qwen max` or `qwen 3.7 max` → `review-plan-qwen3.7-max`.

3. **Resolve mode**. There are two modes: TWO-STEPS (reviewer builds an alternative plan blind, then compares) and ONE-STEP (reviewer reads the plan and critiques it directly). Default to TWO-STEPS. Use ONE-STEP only when the user explicitly asked for a single-step review.

4. **Launch a single subagent call with the `task` tool**:

  Write the full plan to `<cwd>/.opencode/plans/review-plan-{Date.now()}.md` (the project root's `.opencode/plans/` directory; create it if it doesn't exist). This keeps the reviewer's blind phase truly blind — the plan is only accessible when the reviewer calls `read()` on the file.

  Set `subagent_type` to the resolved reviewer, `description` to a short summary, and `prompt` to:

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

  `{absolute_path_to_plan_file}` is the resolved absolute path of the file you just wrote (e.g., `/home/paul/projects/trailblazer2/.opencode/plans/review-plan-1781515003994.md`). Resolve from the project root before launching.

5. **Process the response**: present the reviewer's findings to the user. For each finding, state whether you agree (and what to change) or disagree (and why). Be intellectually honest — if the reviewer found a valid issue, concede. Do not defend your work out of pride. Highlight Critical and High first.
