#!/usr/bin/env python3
"""
Spectre - FantaMoneyball — Econometric Target Pricing & Auction Clearing Engine

Econometric valuation model based on historical Serie A data:
1. Regression-to-the-mean RoleFade:
   - Fits OLS on log(QA / QI) ~ prior_media_fantavoto per macro-role (DEF, MID, ATT).
   - Goalkeepers showed zero correlation and are kept at QI (goalkeeper_no_fade).
   - Applied strictly to players with regular appearance records in the prior season
     (25 <= partite_giocate <= 38). Thinner samples are flagged `thin_prior_sample_no_fade`.
   - Clamped to the 5th-95th percentile range of observed ratios per role to prevent wild extrapolations.
   - Floor guard: QI <= 2 is left untouched (`floor_qi`).
2. Team Reputation Discount:
   - NAP: -15% (factor 0.85)
   - MIL: -10% (factor 0.90)
3. Observed Clearing Prices from Real League Auctions:
   - Calibrated against historical league auction records.
   - Used for market baseline and opportunistic bargain detection (BARGAIN_BETA = 0.60).
"""

from __future__ import annotations

import json
import math
import os
import statistics
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from typing import Any

import openpyxl
import pandas as pd

from core import config

MIN_QI = 2
REGULAR_APPEARANCES_LO = 25
REGULAR_APPEARANCES_HI = 38
GOALKEEPER_MACRO = "GK"
TEAM_DISCOUNTS = {"NAP": 0.85, "MIL": 0.90}
BARGAIN_BETA = 0.60

CLASSIC_ROLE_MAP = {"p": "GK", "d": "DEF", "c": "MID", "a": "ATT"}


class QuotazioniHtmlParser(HTMLParser):
    """Parses historical player rows directly from fantacalcio.it HTML."""

    def __init__(self, season: str):
        super().__init__()
        self.season = season
        self.rows: list[dict[str, Any]] = []
        self.curr: dict[str, Any] | None = None
        self.capture_key: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        d = dict(attrs)
        classes = (d.get("class") or "").split()
        if tag == "tr" and "player-row" in classes:
            self.curr = {
                "season": self.season,
                "id": "",
                "name": "",
                "team": "",
                "role": d.get("data-filter-role-classic", "").lower(),
                "qi": 0,
                "qa": 0,
                "fvm": 0,
            }
        elif self.curr is not None:
            if tag == "a" and "player-name" in classes:
                href = (d.get("href") or "").rstrip("/")
                parts = href.split("/")
                self.curr["id"] = (
                    parts[-1]
                    if parts[-1].isdigit()
                    else (parts[-2] if len(parts) > 1 and parts[-2].isdigit() else "")
                )
            elif tag == "td" and d.get("data-col-key"):
                self.capture_key = d.get("data-col-key")

    def handle_data(self, data: str):
        if self.curr and self.capture_key:
            val = data.strip()
            if self.capture_key == "player_name" and not self.curr["name"]:
                self.curr["name"] = val
            elif self.capture_key == "team" and not self.curr["team"]:
                self.curr["team"] = val
            elif self.capture_key == "c_qi":
                self.curr["qi"] = int(val) if val.isdigit() else 0
            elif self.capture_key == "c_qa":
                self.curr["qa"] = int(val) if val.isdigit() else 0
            elif self.capture_key == "c_fvm":
                self.curr["fvm"] = int(val) if val.isdigit() else 0

    def handle_endtag(self, tag: str):
        if tag == "tr" and self.curr:
            if self.curr["qi"] > 0 and self.curr["qa"] > 0:
                self.rows.append(self.curr)
            self.curr = None
        elif tag == "td":
            self.capture_key = None


def get_cached_historical_quotazioni() -> list[dict[str, Any]]:
    """Loads historical quotazioni from cache or fetches them from fantacalcio.it."""
    cache_path = os.path.join(config.DATA_DIR, "historical_quotazioni_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) >= 1500:
                    return data
        except Exception:
            pass

    seasons = ["2022-23", "2023-24", "2024-25", "2025-26"]
    all_rows = []
    print("  [Pricing Model] Downloading historical quotazioni from fantacalcio.it...")
    for s in seasons:
        url = f"https://www.fantacalcio.it/quotazioni-fantacalcio/{s}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8")
            parser = QuotazioniHtmlParser(s)
            parser.feed(html)
            all_rows.extend(parser.rows)
            print(f"    -> {s}: {len(parser.rows)} quotazioni caricate")
        except Exception as e:
            print(f"    -> Avviso su {s}: {e}")

    if all_rows:
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(all_rows, f, ensure_ascii=False)
        except Exception:
            pass

    return all_rows


def fit_role_fades() -> dict[str, dict[str, float]]:
    """Fits the exact RoleFade linear regression: log(QA / QI) ~ prior_media_fantavoto."""
    quotazioni = get_cached_historical_quotazioni()
    if not quotazioni or not os.path.exists(config.STORICO_RAW_CSV):
        # Fallback pre-fitted weights from empirical Serie A 2022-2026 data
        return {
            "ATT": {"slope": -0.1858, "intercept": 1.1369, "clamp_lo": -1.1787, "clamp_hi": 0.5878},
            "MID": {"slope": -0.2738, "intercept": 1.7040, "clamp_lo": -1.0986, "clamp_hi": 0.7885},
            "DEF": {"slope": -0.3406, "intercept": 1.9586, "clamp_lo": -0.9163, "clamp_hi": 0.6931},
        }

    df_hist = pd.read_csv(config.STORICO_RAW_CSV)
    prior_season_map = {
        "2023-24": "2022-23",
        "2024-25": "2023-24",
        "2025-26": "2024-25",
    }

    prior_stats: dict[tuple[str, str], dict[str, float]] = {}
    for _, row in df_hist.iterrows():
        pid = str(row.get("player_id", "")).strip().replace(".0", "")
        s = str(row.get("season", "")).strip()
        try:
            pg = int(row["pg"]) if pd.notna(row["pg"]) else 0
            mfv = float(row["mfv"]) if pd.notna(row["mfv"]) else 0.0
            prior_stats[(pid, s)] = {"pg": pg, "mfv": mfv}
        except Exception:
            continue

    pairs_by_role: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for q in quotazioni:
        s = q["season"]
        if s not in prior_season_map:
            continue
        qi = q["qi"]
        qa = q["qa"]
        pid = str(q["id"])
        role = CLASSIC_ROLE_MAP.get(q["role"].lower(), q["role"].upper())

        if role == GOALKEEPER_MACRO or qi <= MIN_QI or qa <= 0:
            continue

        prev_s = prior_season_map[s]
        prior = prior_stats.get((pid, prev_s))
        if not prior or not (REGULAR_APPEARANCES_LO <= prior["pg"] <= REGULAR_APPEARANCES_HI):
            continue

        log_ratio = math.log(qa / qi)
        pairs_by_role[role].append((prior["mfv"], log_ratio))

    fades: dict[str, dict[str, float]] = {}
    for role, pairs in pairs_by_role.items():
        if len(pairs) < 20:
            continue
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        slope, intercept = statistics.linear_regression(xs, ys)
        sorted_ys = sorted(ys)
        clamp_lo = sorted_ys[int(0.05 * len(sorted_ys))]
        clamp_hi = sorted_ys[int(0.95 * len(sorted_ys)) - 1]
        fades[role] = {
            "slope": slope,
            "intercept": intercept,
            "clamp_lo": clamp_lo,
            "clamp_hi": clamp_hi,
        }

    return fades


def load_real_auction_sales() -> dict[str, dict[str, Any]]:
    """Loads observed clearing sales from Asta.xlsx (1000 credits) and historical auctions (500 credits)."""
    sales: dict[str, dict[str, Any]] = {}

    # 1. Historical Clearing Sales (416 players, 500cr scale)
    golden_file = os.path.join(config.DATA_DIR, "historical_clearing_sales_summary.json")
    if os.path.exists(golden_file):
        try:
            with open(golden_file, "r", encoding="utf-8") as f:
                golden_data = json.load(f)
            for p_name, d in golden_data.items():
                sales[p_name.strip().lower()] = {
                    "player_name": p_name,
                    "price_1000": int(d.get("mean_1000", 2)),
                    "price_500": int(round(d.get("mean_500", 1))),
                    "source": "historical",
                }
        except Exception as e:
            print(f"  [Pricing Model] Avviso lettura historical_clearing_sales_summary.json: {e}")

    # 2. Observed League Auction (Asta.xlsx, 10 teams, 1000cr scale)
    asta_file = os.path.join(config.DATA_DIR, "Asta.xlsx")
    if os.path.exists(asta_file):
        try:
            wb = openpyxl.load_workbook(asta_file, read_only=True)
            sheet = wb["rose (1)"] if "rose (1)" in wb.sheetnames else wb.active
            rows = list(sheet.iter_rows(values_only=True))[1:]
            for r in rows:
                if len(r) >= 9 and r[8] and r[5] is not None:
                    p_name = str(r[1]).strip().lower()
                    pid = str(r[8]).strip()
                    sales[p_name] = {
                        "fantacalcio_id": pid,
                        "player_name": r[1],
                        "team": str(r[2]).strip().upper(),
                        "role": str(r[3]).strip().upper(),
                        "price_1000": int(r[5]),
                        "price_500": max(1, round(int(r[5]) * 0.5)),
                        "qi": int(r[6]) if r[6] else 1,
                        "source": "asta_xlsx",
                    }
        except Exception as e:
            print(f"  [Pricing Model] Avviso lettura Asta.xlsx: {e}")

    return sales


def compute_target_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Econometric Target & Clearing Prices for all players:
      - target_price_1000
      - target_price_500
      - clearing_price_1000
      - clearing_price_500
      - target_flags
    """
    fades = fit_role_fades()
    auction_sales = load_real_auction_sales()

    # Load 2025-26 priors
    priors_2526: dict[str, dict[str, float]] = {}
    if os.path.exists(config.STORICO_RAW_CSV):
        df_hist = pd.read_csv(config.STORICO_RAW_CSV)
        df_2526 = df_hist[df_hist["season"] == "2025-26"]
        for _, row in df_2526.iterrows():
            pname = str(row["player_name"]).strip().lower()
            try:
                priors_2526[pname] = {
                    "pg": int(row["pg"]) if pd.notna(row["pg"]) else 0,
                    "mfv": float(row["mfv"]) if pd.notna(row["mfv"]) else 0.0,
                }
            except Exception:
                continue

    target_500_list: list[int] = []
    target_1000_list: list[int] = []
    clearing_1000_list: list[int] = []
    clearing_500_list: list[int] = []
    flags_list: list[str] = []

    for _, r in df.iterrows():
        p_name = str(r.get("player", "")).strip()
        norm_name = p_name.lower()
        role_raw = str(r.get("role", "C")).strip().lower()
        macro_role = CLASSIC_ROLE_MAP.get(role_raw, "MID")
        team = str(r.get("team", "")).strip().upper()

        qi = int(r.get("Prezzo_Consigliato_Cr", 1)) if pd.notna(r.get("Prezzo_Consigliato_Cr")) else 1
        fvm_1000 = float(r.get("FVM_1000", qi * 2)) if pd.notna(r.get("FVM_1000")) else float(qi * 2)
        fvm_500 = float(r.get("FVM", qi)) if pd.notna(r.get("FVM")) else float(qi)

        flags: list[str] = []
        prior = priors_2526.get(norm_name)
        adj_factor = 1.0

        if qi <= MIN_QI:
            flags.append("floor_qi")
        elif macro_role == GOALKEEPER_MACRO:
            flags.append("goalkeeper_no_fade")
        elif not prior:
            flags.append("no_prior_data")
        elif not (REGULAR_APPEARANCES_LO <= prior["pg"] <= REGULAR_APPEARANCES_HI):
            flags.append("thin_prior_sample_no_fade")
        elif macro_role in fades:
            f = fades[macro_role]
            raw = f["slope"] * prior["mfv"] + f["intercept"]
            log_ratio = max(f["clamp_lo"], min(f["clamp_hi"], raw))
            adj_factor = math.exp(log_ratio)
            flags.append(f"fade({adj_factor:.2f})")
        else:
            flags.append("no_role_fade_model")

        team_factor = TEAM_DISCOUNTS.get(team, 1.0)
        if team in TEAM_DISCOUNTS:
            flags.append(f"team_discount({team})")

        # Target Price formulas (econometric model)
        tp_500 = max(1, round(qi * adj_factor * team_factor))
        tp_1000 = max(1, round(fvm_1000 * adj_factor * team_factor))

        # Clearing Price from observed Asta.xlsx / golden sales or fallback to target price
        sale = auction_sales.get(norm_name)
        if not sale:
            clean_name = norm_name.replace(".", "").strip()
            for s_k, s_v in auction_sales.items():
                if s_k == clean_name or s_k.replace(".", "").strip() == clean_name:
                    sale = s_v
                    break

        if sale:
            cp_1000 = sale["price_1000"]
            cp_500 = sale["price_500"]
            flags.append(f"clearing_observed({sale.get('source', 'asta')})")
        else:
            cp_1000 = tp_1000
            cp_500 = tp_500

        target_500_list.append(tp_500)
        target_1000_list.append(tp_1000)
        clearing_1000_list.append(cp_1000)
        clearing_500_list.append(cp_500)
        flags_list.append(";".join(flags))

    df["target_price_500"] = target_500_list
    df["target_price_1000"] = target_1000_list
    df["clearing_price_1000"] = clearing_1000_list
    df["clearing_price_500"] = clearing_500_list
    df["target_flags"] = flags_list

    return df
