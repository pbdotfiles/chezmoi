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

5. **Resolve reviewer.** Default inherits the main agent's model via the `review-code` subagent. Otherwise, pick the agent whose model best matches what the user named — match loosely, then use the resolved name as `subagent_type` in step 6. The available agents are:

   - `review-code-glm` — opencode-go/glm-5.2
   - `review-code-deepseek` — opencode-go/deepseek-v4-pro
   - `review-code-minimax` — opencode-go/minimax-m3
   - `review-code-qwen3.7-plus` — opencode-go/qwen3.7-plus
   - `review-code-qwen3.7-max` — opencode-go/qwen3.7-max

   Examples: `glm` or `glm-5.2` → `review-code-glm`; `qwen` or `qwen plus` or `qwen 3.7 plus` → `review-code-qwen3.7-plus`; `qwen max` or `qwen 3.7 max` → `review-code-qwen3.7-max`.

6. **Launch a single subagent call** with the `task` tool:
   - `subagent_type` — resolved reviewer name
   - `description` — short summary of what's being reviewed
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
