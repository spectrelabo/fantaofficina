# Project timeline

This page tells the story of `fanta-lab`: where it started, what it became through seven pillars of work, and where it's heading. It's not a technical changelog — the per-module READMEs cover that — but a narrative for anyone who wants to understand *why* the project is shaped the way it is.

## 1. Where we came from

`fanta-lab` started as a script built for a single moment of the season: the pre-season auction draft. The goal was simple and narrow — given a list of available players, produce a "fair" price to bid on each one, to be consulted on draft night and then set aside until the following year.

The statistical core of that first version was a quantile regression model (Gradient Boosting Regressor) trained on historical player data, able to estimate not a single number but three percentiles of expected end-of-season points: P10 (pessimistic scenario), P50 (median scenario), and P90 (optimistic scenario). From that distribution of expected points came VORP (Value Over Replacement Player), which compared each player to a hypothetical baseline replacement at the same position to arrive at a fair price consistent with the auction budget.

It was, in essence, a snapshot: a single calculation, run once, to decide how to spend a budget in a single evening. Everything that happened afterward — the seven pillars described below — is the story of how that snapshot became a film: a system that keeps observing, updating, and recalibrating its estimates across the entire 38-matchday season.

## 2. What this demo build shows

**Pillar 1 — Dual-track community/personal.** The first step of architectural maturity: separating a "community" configuration, meant to be shared and reproduced by anyone cloning the repository, from a "personal" configuration holding data and parameters specific to whoever runs the project for their own league. A cascading configuration layer driven by the `APP_ENV` environment variable made this split possible without duplicating code.

**Pillar 2 — Critical bugfixes.** A series of fixes that made the system reliable in production: a `player_id` fallback to guarantee training reproducibility even when the primary identifier is unavailable; improved resilience of data-source scraping, with fallback mechanisms for when pages change structure or stop responding; a recalibration of the Scala Slot percentiles to account for differences across positions; and a blueprint of dynamic percentages, rescaled against the league's actual budget instead of a fixed value.

**Pillar 3 — Public demo baseline.** This public repository is a simplified, didactic version of the project: it demonstrates the end-to-end auction pipeline (data loading, pricing, Excel export) with a bundled example dataset and no live scraping. The full commercial product — real historical data pipelines, a trained quantile-regression model, in-season analytical modules, and an AI assistant — is a private product, not distributed here.

The common thread across this project, statistically speaking, is the move from a point estimate calculated once to a system that reasons in terms of full outcome distributions rather than single expected values: a quantile regression model estimates not a single number but three percentiles of expected points (pessimistic, median, optimistic scenarios), and VORP (Value Over Replacement Player) compares each player to a replacement-level baseline at the same position to arrive at a fair auction price.

## 3. Where we're going

The direction the project is moving in isn't a checklist of features, but an underlying idea: making statistical uncertainty more central, and more accessible, over time — reasoning increasingly in terms of full distributions rather than single expected values, and translating that sophistication into decisions that make sense to someone who plays fantasy football for fun, not to do data science.
