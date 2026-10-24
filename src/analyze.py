"""Analyze the onboarding funnel: overall, by channel, and where to focus."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["download", "signup", "bvn_verified", "account_funded", "first_transaction"]


def funnel_counts(df):
    """How many users reached AT LEAST each step."""
    rank = df["furthest_step"].map({s: i for i, s in enumerate(STEPS)})
    return pd.Series({s: int((rank >= i).sum()) for i, s in enumerate(STEPS)})


def funnel_table(counts):
    t = pd.DataFrame({"users": counts})
    t["pct_of_start"] = (t["users"] / t["users"].iloc[0] * 100).round(1)
    t["step_conversion_pct"] = (t["users"] / t["users"].shift(1) * 100).round(1)
    t["step_dropoff_pct"] = (100 - t["step_conversion_pct"]).round(1)
    return t


def main():
    df = pd.read_csv(ROOT / "data" / "onboarding_events.csv")
    overall = funnel_table(funnel_counts(df))
    print("OVERALL FUNNEL\n", overall, "\n")
    overall.to_csv(ROOT / "outputs" / "overall_funnel.csv")

    # End-to-end conversion and activation by channel
    by_channel = {}
    for ch, g in df.groupby("channel"):
        c = funnel_counts(g)
        by_channel[ch] = {
            "users": c.iloc[0],
            "signup_to_bvn_pct": round(c["bvn_verified"] / c["signup"] * 100, 1),
            "download_to_first_txn_pct": round(c["first_transaction"] / c.iloc[0] * 100, 1),
        }
    ch_table = pd.DataFrame(by_channel).T.sort_values("download_to_first_txn_pct", ascending=False)
    print("BY CHANNEL\n", ch_table, "\n")
    ch_table.to_csv(ROOT / "outputs" / "channel_comparison.csv")

    # Biggest leak = the step with the lowest step conversion
    worst = overall["step_conversion_pct"].iloc[1:].idxmin()
    print(f"Biggest drop-off: {worst} "
          f"({overall.loc[worst, 'step_dropoff_pct']}% of users lost at this step)")

    # Charts
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(overall.index[::-1], overall["users"][::-1], color="#2f6f9f")
    for i, (u, p) in enumerate(zip(overall["users"][::-1], overall["pct_of_start"][::-1])):
        ax.text(u + 150, i, f"{u:,} ({p}%)", va="center", fontsize=9)
    ax.set_title("Onboarding funnel: users reaching each step")
    ax.set_xlim(0, overall["users"].max() * 1.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ROOT / "outputs" / "funnel.png", dpi=150)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ct = ch_table["download_to_first_txn_pct"]
    ax.bar(ct.index, ct.values, color="#2f6f9f")
    for i, v in enumerate(ct.values):
        ax.text(i, v + 0.3, f"{v}%", ha="center", fontsize=9)
    ax.set_title("Download to first transaction, by acquisition channel")
    ax.set_ylabel("% of downloads")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(ROOT / "outputs" / "channel_conversion.png", dpi=150)


if __name__ == "__main__":
    main()
