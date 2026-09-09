---
name: web-app-visual-design
description: Use when redesigning or restyling the fanta-lab web UI (themes, component visuals, tab/nav design, animations, illustrations) — especially after a mockup or component has been judged "too basic", "generic AI design", disproportionate, or not matching a real visual reference image the user provided.
---

# Web App Visual Design (fanta-lab)

Use this skill together with the `fantalab-ui-designer` custom agent (`.github/agents/fantalab-ui-designer.agent.md`) for any visual restyle of `web/app.py` / `web/static/`. Don't do high-fidelity UI design work directly in the main conversation loop — dispatch to that agent, which defaults to a top-tier reasoning model chosen for visual/design judgment.

## Why This Skill Exists

Baseline failure observed: quick inline HTML/CSS mockups (built for the brainstorming visual-companion browser tab) reliably look "like a design student's first project" — flat emoji instead of icons, oversized components relative to real content density, decorative elements disconnected from a reference image, animations that are technically present but generic (simple fades/rotates) instead of purposeful. The user explicitly rejected this output and asked for a dedicated skill + performant model.

## Core Principle

**Match scale to the real page, not to an empty mockup canvas.** A component designed in isolation (a lone browser tab, no surrounding content) always looks bigger and more spacious than it will in the actual app, which is already dense with data (tables, badges, stat rows). Before finalizing any component's size, place it in — or reference the real dimensions of — the existing `web/app.py` layout, not a blank page.

## Design Workflow

1. **Ground every visual choice in a concrete reference.** If the user shares a reference image (a photo, a screenshot, a style example), treat it as the literal source of truth for texture, proportions, and composition — not as vague "inspiration" to reinterpret loosely. Re-examine the reference for details easy to miss: exact aspect ratio, how much of the surface is empty vs. decorated, where visual weight concentrates, material/texture cues (matte vs. glossy, worn vs. pristine).
2. **Build inside the real codebase, not a throwaway mockup.** Prototype changes directly in `web/static/css/` and `web/app.py`'s inline `<style>` block (see `core/README.md` / `web/README.md` for current structure), or in a scratch `.html` file that includes the actual page's surrounding markup — never an isolated component on a blank background. Isolated previews hide scale and density problems.
3. **Icons: use a real icon set, never emoji.** This app already loads Font Awesome — check current usage (`grep -n "fa-solid\|fa-brands" web/app.py`) before adding a new library. Pick icons for their actual semantic fit (a gauge for analytics, a flask for the AI/experimental copilot), not the first visually-close match.
4. **Animation must be purposeful, not decorative filler.** Every animation should communicate state (active/inactive, loading, success/error, hover-affordance) or reinforce the theme's material logic (e.g., a gear-shaped element rotating makes sense; a card randomly bouncing does not). Prefer CSS custom properties + `cubic-bezier` easing already used elsewhere in `web/app.py` (search `cubic-bezier` for the existing motion language) over new ad-hoc timing curves, to keep the whole app feeling like one coherent system.
5. **Density check before presenting.** Count how many of these a real tab/card will actually need to show at once (8 nav items, dozens of table rows, several badges) and verify the new design doesn't force excessive whitespace or oversized chrome around that real content volume.
6. **State explicitly what reference/precedent each major choice is based on** when presenting the design back to the user (e.g., "the frame proportions come from the leather-journal photo you shared, scaled to fit an 80px nav slot instead of a 400px journal cover") — this makes it easy for the user to correct a specific decision rather than rejecting the whole direction.

## Quick Reference: Common "Generic AI Design" Tells to Avoid

| Tell | Fix |
|---|---|
| Emoji as icons | Use the app's existing icon library (Font Awesome) with semantically chosen glyphs |
| Components sized for an empty canvas | Prototype against real page density; check actual container dimensions in `web/app.py` |
| Decorative elements disconnected from any reference | Tie every ornament back to a specific detail in the user-provided reference image |
| Animation for animation's sake | Every motion should signal state or reinforce material logic |
| New easing/timing invented ad hoc | Reuse the app's existing `cubic-bezier` motion language |
| One-shot flat mockup, no iteration loop | Present, name the reference each choice came from, invite targeted correction |

## Delegation

For actual implementation (not just exploration), dispatch to the `fantalab-ui-designer` agent so design work runs on a stronger model than the default lightweight subagent tier. See that agent's file for its exact model/tool configuration.
