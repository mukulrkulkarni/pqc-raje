# Engineering Critic 403 Resolution (Gemini access)

## Summary
The project experienced repeated **403 Forbidden** errors when delegating Engineering Gate reviews to the **Engineering Critic** agent.

This document records the root cause, the fix, and the standard operating procedure (SOP) for future Engineering Gate reviews.

## Symptoms
- Delegations to `engineering-critic` (and sometimes `engineering-lead` when it attempted to call the critic) failed with:
  - `GoogleGenerativeAI Error: ... gemini-2.5-flash ... 403 Forbidden: Your project has been denied access`

## Root cause
- The `engineering-critic` agent was configured to use a **Gemini model** (`gemini-2.5-flash`).
- The runtime/provider for that model returned 403 for this project (likely due to missing/invalid API key, quota, billing, or regional access restrictions).
- While some configuration overlays showed a non-Gemini model, the **effective runtime execution** still remapped/fell back unpredictably under the `innovium` runtime.

## Fix applied
We reconfigured the Engineering Critic agent to use the Claude Agent runtime so that:
1) the configured model is honored at execution time,
2) delegation no longer depends on Gemini access.

**Current working configuration (verified):**
- Agent: `engineering-critic`
- Runtime: `claude` (Claude Code / Claude Agent SDK)
- Model: `claude-opus-4-5`

**Evidence:**
- `agent-management__get_agent` shows `runtime=claude`, `model=claude-opus-4-5`.
- A live delegation self-report returned: `Claude Code + claude-opus-4-5`.

## SOP: Engineering Gate reviews going forward
1. Use `engineering-critic` for Engineering Gate checks.
2. If an access error reappears:
   - Confirm the agent runtime/model with `agent-management__get_agent`.
   - Ensure runtime is `claude` (preferred) or another non-Gemini runtime.
   - Switch to a known-good model available in this environment (example: `claude-opus-4-5`, `claude-sonnet-5`, or `gpt-4.1`).
3. Only if the critic agent is unavailable, use Engineering Lead direct inspection as a temporary fallback and document the limitation in the gate report.

## Notes
- This fix is an agent configuration change; no repository source-code changes are required for it.
- The project policy still applies: small chunks, meaningful negative tests, approval-before-gates, commit-after-gates.
