#!/usr/bin/env python3
"""
Generate 4-Quadrant Value Maps (Scatter Plots) for each Fantacalcio role.
Style inspired by 'Cost of Living vs. Quality of Life' matrix.
Saves high-res PNG images directly to the artifact directory.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from adjustText import adjust_text

ARTIFACT_DIR = Path("/Users/a409835/.gemini/antigravity-ide/brain/f696c793-d21c-4ca2-ad96-98dee896977f")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = Path("data/dataset_finale.csv")

ROLE_CONFIGS = {
    "P": {
        "title": "PORTIERI TITOLARI",
        "badge": "[P]",
        "x_th": 30,
        "y_th": 156,
        "x_col": "FVM_1000",
        "y_col": "predicted_pts_p50",
        "y_label": "Punti Totali Attesi P50 (Clean Sheet + Malus Subiti)",
        "x_label": "Costo Medio d'Asta (Crediti su base 1000 — FVM)",
        "filename": "value_map_portieri.png",
        "filter_min_pts": 90,
        "n_labels_per_quadrant": 7,
        "only_starters": True,
    },
    "D": {
        "title": "DIFENSORI (NO 1a FASCIA — MID & LOW TIER)",
        "subtitle": "Ricalibratura senza i Top (>35 cr) per zoomare su Steal (1-14 cr) e Solidi di Reparto (15-32 cr)",
        "badge": "[D]",
        "x_th": 14,
        "y_th": 162,
        "x_col": "FVM_1000",
        "y_col": "predicted_pts_p50",
        "y_label": "Punti Totali Attesi P50 (Titolarita' + Media Voto Modificatore + Bonus)",
        "x_label": "Costo Medio d'Asta (Crediti su base 1000 — FVM)",
        "filename": "value_map_difensori.png",
        "filter_min_pts": 100,
        "max_fvm": 35,
        "n_labels_per_quadrant": 10,
        "custom_badges": {
            "best_value": "BEST VALUE [STEAL D'ASTA 1-14 cr]\nLe Vere Gemme da Modificatore a Costo Minimo",
            "premium": "SOLIDI 2a FASCIA [15-32 cr]\nTitolari di Livello & Terzini che Valgono la Spesa",
            "budget": "BUDGET ROTAZIONE [1-14 cr]\nTappabuchi (1-5 cr) e Coperture da Panchina",
            "trap": "SOVRAPPREZZATI 2a FASCIA [15-32 cr]\nNome/Hype ma Resa Sotto la Media (Obiettivi Drain)",
        },
    },
    "C": {
        "title": "CENTROCAMPISTI (NO 1a FASCIA — MID & LOW TIER)",
        "subtitle": "Ricalibratura senza i Top (>60 cr) per zoomare su Steal (1-20 cr) e Solidi 2a Fascia (21-57 cr)",
        "badge": "[C]",
        "x_th": 20,
        "y_th": 168,
        "x_col": "FVM_1000",
        "y_col": "predicted_pts_p50",
        "y_label": "Punti Totali Attesi P50 (Gol, Assist, xG/xA & FantaMedia)",
        "x_label": "Costo Medio d'Asta (Crediti su base 1000 — FVM)",
        "filename": "value_map_centrocampisti.png",
        "filter_min_pts": 105,
        "max_fvm": 60,
        "n_labels_per_quadrant": 10,
        "custom_badges": {
            "best_value": "BEST VALUE [STEAL D'ASTA 1-20 cr]\nLe Vere Gemme da Bonus a Costo Contenuto",
            "premium": "SOLIDI 2a FASCIA [21-57 cr]\nCentrocampisti da Bonus e Media Voto Elevata",
            "budget": "BUDGET ROTAZIONE [1-20 cr]\nTappabuchi (1-5 cr) e Regolaristi da Panchina",
            "trap": "SOVRAPPREZZATI 2a FASCIA [21-57 cr]\nNome/Hype ma Resa Sotto la Media (Obiettivi Drain)",
        },
    },
    "A": {
        "title": "ATTACCANTI (NO 1a FASCIA — 2°, 3°, 4° SLOT)",
        "subtitle": "Ricalibratura senza i Bomber Top (>100 cr) per zoomare su Occasioni (1-30 cr) e 2° Slot (31-98 cr)",
        "badge": "[A]",
        "x_th": 30,
        "y_th": 165,
        "x_col": "FVM_1000",
        "y_col": "predicted_pts_p50",
        "y_label": "Punti Totali Attesi P50 (Proiezione Gol, Rigori, Volume Tiri)",
        "x_label": "Costo Medio d'Asta (Crediti su base 1000 — FVM)",
        "filename": "value_map_attaccanti.png",
        "filter_min_pts": 100,
        "max_fvm": 100,
        "n_labels_per_quadrant": 10,
        "custom_badges": {
            "best_value": "BEST VALUE [OCCASIONI 1-30 cr]\nAttaccanti ad Alta Resa Gol/Assist a Prezzi Scontati",
            "premium": "2° SLOT SOLIDI [31-98 cr]\nSeconde Punte & Titolari da Doppia Cifra Potenziale",
            "budget": "BUDGET ROTAZIONE [1-30 cr]\nJolly da Ultimi Slot (1-10 cr) e Riserve",
            "trap": "SOVRAPPREZZATI 2a FASCIA [31-98 cr]\nPunte da Flop/Turnover Pagate Troppo (Obiettivi Drain)",
        },
    },
}


def generate_map(df_role: pd.DataFrame, cfg: dict):
    fig, ax = plt.subplots(figsize=(15, 10.5), dpi=160)
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    x_col = cfg["x_col"]
    y_col = cfg["y_col"]
    x_th = cfg["x_th"]
    y_th = cfg["y_th"]

    # Filter out inactive players
    data = df_role[df_role[y_col] >= cfg["filter_min_pts"]].copy()
    data = data[data[x_col] > 0].copy()

    if cfg.get("max_fvm"):
        data = data[data[x_col] < cfg["max_fvm"]].copy()

    if cfg.get("only_starters"):
        # Isolate genuine starting goalkeepers of Serie A.
        # Exclude backup keepers (Grabara, Mascardi, Josep Martinez, Sanchez Ro., etc.) who don't play 38 games
        known_backups = [
            "Grabara", "Mascardi", "Martinez Jo.", "Palmisani", "Daffara", 
            "Tornqvist", "Gollini", "Sportiello", "Padelli", "Pinsoglio", 
            "Torriani", "Desplanches", "Radunovic", "Pisseri", "Pozzi", "Russo A.",
            "Sanchez Ro.", "Montipò"
        ]
        data = data[
            (~data["player"].isin(known_backups)) &
            (
                (data["starts_2627"] >= 1) |
                (data["player"].isin(["Perri", "Vicario"])) |
                (data[x_col] >= 15)
            )
        ]

    # Determine axis boundaries with clean padding
    x_min = max(0, data[x_col].min() * 0.8)
    x_max = data[x_col].max() * 1.06
    y_min = data[y_col].min() * 0.96
    y_max = data[y_col].max() * 1.05

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # ─────────────────────────────────────────────────────────────
    # QUADRANT BACKGROUND SHADING
    # ─────────────────────────────────────────────────────────────
    # Top-Left: Best Value (Mint Green)
    ax.add_patch(patches.Rectangle((x_min, y_th), x_th - x_min, y_max - y_th, 
                                   facecolor="#dcfce7", alpha=0.55, zorder=0))
    # Top-Right: Premium Elite (Sky Blue)
    ax.add_patch(patches.Rectangle((x_th, y_th), x_max - x_th, y_max - y_th, 
                                   facecolor="#e0f2fe", alpha=0.55, zorder=0))
    # Bottom-Left: Budget Tier (Warm Sand / Beige)
    ax.add_patch(patches.Rectangle((x_min, y_min), x_th - x_min, y_th - y_min, 
                                   facecolor="#fef9c3", alpha=0.45, zorder=0))
    # Bottom-Right: Overpriced Traps (Soft Coral / Rose)
    ax.add_patch(patches.Rectangle((x_th, y_min), x_max - x_th, y_th - y_min, 
                                   facecolor="#fee2e2", alpha=0.55, zorder=0))

    # ─────────────────────────────────────────────────────────────
    # QUADRANT DIVIDERS
    # ─────────────────────────────────────────────────────────────
    ax.axvline(x=x_th, color="#64748b", linestyle="--", linewidth=1.4, alpha=0.8, zorder=1)
    ax.axhline(y=y_th, color="#64748b", linestyle="--", linewidth=1.4, alpha=0.8, zorder=1)

    # ─────────────────────────────────────────────────────────────
    # QUADRANT WATERMARKS & BADGES
    # ─────────────────────────────────────────────────────────────
    bv_text = cfg.get("custom_badges", {}).get("best_value", "BEST VALUE [ALTA RESA / BASSO COSTO]\nLe Vere Gemme d'Asta (Occasioni & Steal)")
    prem_text = cfg.get("custom_badges", {}).get("premium", "PREMIUM ELITE [TOP DI REPARTO]\nExpensive, But Worth It (Resa Dominante)")
    budg_text = cfg.get("custom_badges", {}).get("budget", "BUDGET ROTATION [SLOT DI COPERTURA]\nCosto Minimo (1-10 cr) • Titolarita' da Rotazione")
    trap_text = cfg.get("custom_badges", {}).get("trap", "OVERPRICED TRAPS [TRAPPOLE HYPE]\nCosto Elevato / Nome • Resa Sotto la Media (Pacchi)")

    # Best Value Badge (Top-Left)
    ax.text(x_min + (x_th - x_min) * 0.04, y_max - (y_max - y_th) * 0.05,
            bv_text,
            fontsize=10.2, fontweight="bold", color="#15803d",
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#ffffff", edgecolor="#86efac", alpha=0.92, lw=1.3))

    # Premium Elite Badge (Top-Right)
    ax.text(x_max - (x_max - x_th) * 0.04, y_max - (y_max - y_th) * 0.05,
            prem_text,
            fontsize=10.2, fontweight="bold", color="#0369a1",
            va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#ffffff", edgecolor="#7dd3fc", alpha=0.92, lw=1.3))

    # Budget Tier Badge (Bottom-Left)
    ax.text(x_min + (x_th - x_min) * 0.04, y_min + (y_th - y_min) * 0.06,
            budg_text,
            fontsize=9.8, fontweight="bold", color="#a16207",
            va="bottom", ha="left",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#ffffff", edgecolor="#fde047", alpha=0.92, lw=1.3))

    # Overpriced Traps Badge (Bottom-Right)
    ax.text(x_max - (x_max - x_th) * 0.04, y_min + (y_th - y_min) * 0.06,
            trap_text,
            fontsize=9.8, fontweight="bold", color="#b91c1c",
            va="bottom", ha="right",
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#ffffff", edgecolor="#fca5a5", alpha=0.92, lw=1.3))

    # ─────────────────────────────────────────────────────────────
    # SCATTER POINTS CLASSIFICATION
    # ─────────────────────────────────────────────────────────────
    def get_quadrant(row):
        x = row[x_col]
        y = row[y_col]
        if x < x_th and y >= y_th:
            return "best_value"
        elif x >= x_th and y >= y_th:
            return "premium"
        elif x < x_th and y < y_th:
            return "budget"
        else:
            return "trap"

    data["quadrant"] = data.apply(get_quadrant, axis=1)

    color_map = {
        "best_value": "#16a34a", # emerald green
        "premium": "#0284c7",    # deep sky blue
        "budget": "#ca8a04",     # dark gold
        "trap": "#dc2626",       # crimson red
    }

    # Plot points
    for q_name, q_color in color_map.items():
        q_data = data[data["quadrant"] == q_name]
        ax.scatter(
            q_data[x_col],
            q_data[y_col],
            color=q_color,
            s=75,
            alpha=0.82,
            edgecolors="#1e293b",
            linewidths=0.7,
            zorder=3,
        )

    # ─────────────────────────────────────────────────────────────
    # SMART ANNOTATIONS / LABELS
    # ─────────────────────────────────────────────────────────────
    n_labels = cfg["n_labels_per_quadrant"]
    labeled_rows = []

    # 1. Best Value: highest predicted points and biggest surplus
    q_bv = data[data["quadrant"] == "best_value"].sort_values(by=y_col, ascending=False)
    labeled_rows.extend(q_bv.head(n_labels).to_dict("records"))

    # 2. Premium Elite: highest cost and highest points
    q_pe = data[data["quadrant"] == "premium"].sort_values(by=x_col, ascending=False)
    labeled_rows.extend(q_pe.head(n_labels).to_dict("records"))

    # 3. Traps: highest cost among low points (worst traps)
    q_tr = data[data["quadrant"] == "trap"].sort_values(by=x_col, ascending=False)
    labeled_rows.extend(q_tr.head(n_labels).to_dict("records"))

    # 4. Budget: top performers in budget
    q_bg = data[data["quadrant"] == "budget"].sort_values(by=y_col, ascending=False)
    labeled_rows.extend(q_bg.head(min(4, n_labels // 2)).to_dict("records"))

    # Remove duplicates
    seen_players = set()
    unique_labeled = []
    for r in labeled_rows:
        if r["player"] not in seen_players:
            seen_players.add(r["player"])
            unique_labeled.append(r)

    texts = []
    for r in unique_labeled:
        x_val = r[x_col]
        y_val = r[y_col]
        name = r["player"]
        team = r.get("team", "")
        q = r["quadrant"]

        # Color coded text badge
        t_color = "#0f172a"
        if q == "best_value":
            t_color = "#14532d"
        elif q == "premium":
            t_color = "#0c4a6e"
        elif q == "trap":
            t_color = "#7f1d1d"

        txt = ax.text(
            x_val,
            y_val,
            f"{name} ({int(x_val)}cr)",
            fontsize=8.5,
            fontweight="bold",
            color=t_color,
            zorder=4,
        )
        texts.append(txt)

    if texts:
        adjust_text(
            texts,
            ax=ax,
            arrowprops=dict(arrowstyle="->", color="#475569", lw=0.6, alpha=0.7),
            expand_points=(1.3, 1.3),
            force_points=(0.25, 0.4),
            force_text=(0.4, 0.6),
        )

    # ─────────────────────────────────────────────────────────────
    # TITLES, LABELS & STYLING
    # ─────────────────────────────────────────────────────────────
    title_text = f"{cfg['badge']} MAPPA DEL VALORE — {cfg['title']}"
    subtitle_text = cfg.get("subtitle", "Analisi a 4 Quadranti: Costo Medio nelle Aste (FVM 1000) vs. Rendimento Statistico Atteso")
    
    ax.set_title(f"{title_text}\n{subtitle_text}", fontsize=14, fontweight="heavy", pad=16, color="#0f172a", loc="left")
    ax.set_xlabel(cfg["x_label"], fontsize=11, fontweight="bold", labelpad=10, color="#1e293b")
    ax.set_ylabel(cfg["y_label"], fontsize=11, fontweight="bold", labelpad=10, color="#1e293b")

    # Clean grid
    ax.grid(True, linestyle=":", alpha=0.45, color="#94a3b8")
    ax.tick_params(axis="both", which="major", labelsize=10, colors="#334155")
    for spine in ax.spines.values():
        spine.set_edgecolor("#cbd5e1")
        spine.set_linewidth(1.0)

    # Watermark / footer
    fig.text(0.98, 0.015, "Fanta-Lab Intelligence Engine • Valutazione Quantitativa Serie A 2026/27",
             fontsize=8.5, color="#64748b", ha="right", style="italic")

    plt.tight_layout()
    output_path = ARTIFACT_DIR / cfg["filename"]
    fig.savefig(output_path, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Generated: {output_path}")
    return output_path


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {len(df)} players")

    for role, cfg in ROLE_CONFIGS.items():
        sub = df[df["role"] == role]
        generate_map(sub, cfg)

    print("All 4 Value Maps generated successfully!")


if __name__ == "__main__":
    main()
