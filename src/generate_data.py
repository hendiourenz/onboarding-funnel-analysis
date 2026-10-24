"""Generate synthetic mobile-banking onboarding events.

Each user moves through these steps and may drop off at any point:
    download -> signup -> bvn_verified -> account_funded -> first_transaction

All data is synthetic. Drop-off rates are set to look realistic for a
Nigerian digital-banking app (BVN/ID verification is the big friction point).
"""
import csv
import random
from pathlib import Path

random.seed(42)

STEPS = ["download", "signup", "bvn_verified", "account_funded", "first_transaction"]
CHANNELS = {
    # channel: (share of users, per-step continue probabilities for steps 2..5)
    "organic_search": (0.25, [0.78, 0.55, 0.62, 0.70]),
    "instagram_ads": (0.30, [0.65, 0.42, 0.50, 0.58]),
    "referral": (0.20, [0.88, 0.72, 0.78, 0.85]),
    "agent_banking": (0.15, [0.92, 0.80, 0.70, 0.80]),
    "radio_tv": (0.10, [0.60, 0.40, 0.48, 0.55]),
}
N_USERS = 20000


def main():
    out = Path(__file__).resolve().parent.parent / "data" / "onboarding_events.csv"
    names = list(CHANNELS)
    weights = [CHANNELS[c][0] for c in names]
    rows = []
    for uid in range(1, N_USERS + 1):
        channel = random.choices(names, weights)[0]
        probs = CHANNELS[channel][1]
        reached = 1  # everyone starts at download
        for p in probs:
            if random.random() < p:
                reached += 1
            else:
                break
        rows.append({"user_id": uid, "channel": channel,
                     "furthest_step": STEPS[reached - 1]})
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["user_id", "channel", "furthest_step"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} users to {out}")


if __name__ == "__main__":
    main()
