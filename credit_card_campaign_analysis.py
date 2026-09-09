import numpy as np
import pandas as pd

# ---------------------------------------------------------
# NOTE ON DATA:
# Real credit-card-level campaign data is not publicly available, so this
# analysis is built on the Hillstrom email marketing dataset as a public
# proxy, relabeled to simulate a credit-card campaign-targeting problem:
#   segment (email arm)      -> campaign_arm (cashback offer arm)
#   spend                    -> card_spend (post-campaign card spend)
#   visit                    -> login_or_app_open (digital engagement)
#   conversion                -> activation (offer activated / first txn)
#   mens / womens (purchase)  -> revolver_flag / transactor_flag (past usage)
#   gender_pref               -> customer_behavior_segment
#   recency                   -> recency (months since last card activity)
# ---------------------------------------------------------

# 1. Load the dataset
df = pd.read_csv("Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv")

# 2. Relabel columns and segment values to the credit-card story
df = df.rename(
    columns={
        "spend": "card_spend",
        "visit": "login_or_app_open",
        "conversion": "activation",
        "mens": "revolver_flag",
        "womens": "transactor_flag",
    }
)

df["campaign_arm"] = df["segment"].replace(
    {
        "Mens E-Mail": "Cashback Offer A",
        "Womens E-Mail": "Cashback Offer B",
        "No E-Mail": "Control - No Offer",
    }
)

# 3. Define customer behavior segments based on past card usage
df["customer_behavior_segment"] = np.where(
    (df["revolver_flag"] == 1) & (df["transactor_flag"] == 1),
    "Both",
    np.where(
        df["revolver_flag"] == 1,
        "Revolver Only",
        np.where(df["transactor_flag"] == 1, "Transactor Only", "Dormant"),
    ),
)

# ---------------------------------------------------------
# STEP 1: Baseline Campaign Impact Analysis
# ---------------------------------------------------------
baseline = (
    df.groupby("campaign_arm")
    .agg(
        customers=("recency", "count"),
        logins=("login_or_app_open", "sum"),
        login_rate=("login_or_app_open", "mean"),
        activations=("activation", "sum"),
        activation_rate=("activation", "mean"),
        total_card_spend=("card_spend", "sum"),
        avg_card_spend=("card_spend", "mean"),
    )
    .reset_index()
)

# Extract control metrics (No Offer)
control_avg_spend = baseline.loc[
    baseline["campaign_arm"] == "Control - No Offer", "avg_card_spend"
].values[0]    #.loc is used to select rows and columns based on labels/conditions
#.values converts the Pandas Series into a NumPy array,0 first element of the array
control_activation_rate = baseline.loc[
    baseline["campaign_arm"] == "Control - No Offer", "activation_rate"
].values[0]

# Calculate incremental impact vs Control
baseline["incremental_spend_per_cust"] = (
    baseline["avg_card_spend"] - control_avg_spend
)
baseline["incremental_activation_rate"] = (
    baseline["activation_rate"] - control_activation_rate
)
baseline["net_campaign_revenue"] = (
    baseline["incremental_spend_per_cust"] * baseline["customers"]
)

print("=== BASELINE CREDIT CARD CAMPAIGN IMPACT ASSESSMENT ===")
print(
    baseline[
        [
            "campaign_arm",
            "customers",
            "login_rate",
            "activation_rate",
            "avg_card_spend",
            "incremental_spend_per_cust",
            "net_campaign_revenue",
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# STEP 2: Cross-Segment Lift Analysis (Customer Behavior)
# ---------------------------------------------------------
segment_lift = (
    df.groupby(["customer_behavior_segment", "campaign_arm"])["card_spend"]
    .mean()
    .unstack("campaign_arm")
)

# Calculate incremental spend lift over 'Control - No Offer' per group
segment_lift["offer_a_lift"] = (
    segment_lift["Cashback Offer A"] - segment_lift["Control - No Offer"]
)
segment_lift["offer_b_lift"] = (
    segment_lift["Cashback Offer B"] - segment_lift["Control - No Offer"]
)

print("\n=== INCREMENTAL CARD SPEND LIFT BY CUSTOMER BEHAVIOR SEGMENT ===")
print(segment_lift[["Control - No Offer", "offer_a_lift", "offer_b_lift"]])


# ---------------------------------------------------------
# STEP 3: Opportunity Sizing Scenarios across Portfolio (64,000 cardholders)
# ---------------------------------------------------------
total_pop = len(df)

# Scenario A: Universal Cashback Offer A Rollout
scenario_a_lift = baseline.loc[
    baseline["campaign_arm"] == "Cashback Offer A", "incremental_spend_per_cust"
].values[0]
revenue_a = total_pop * scenario_a_lift

# Scenario B: Precision Segment-Matched Campaign
# Assign Offer A to Revolver Only & Both; Offer B to Transactor Only
# NOTE: customer_behavior_segment is the INDEX of segment_lift (from the
# groupby/unstack above), not a column -- so it must be read via row.name.
def get_best_treatment_lift(row):
    if row.name in ["Revolver Only", "Both"]:
        return row["offer_a_lift"]
    elif row.name == "Transactor Only":
        return row["offer_b_lift"]
    else:
        return max(row["offer_a_lift"], row["offer_b_lift"])


segment_lift["optimal_lift"] = segment_lift.apply(
    get_best_treatment_lift, axis=1
)
counts = df["customer_behavior_segment"].value_counts()
revenue_b = (segment_lift["optimal_lift"] * counts).sum()

# Scenario C: Active Recency Filter (Recency <= 3 months with Offer A)
active_df = df[df["recency"] <= 3]
active_control_spend = active_df.loc[
    active_df["campaign_arm"] == "Control - No Offer", "card_spend"
].mean()
active_offer_a_spend = active_df.loc[
    active_df["campaign_arm"] == "Cashback Offer A", "card_spend"
].mean()
active_lift = active_offer_a_spend - active_control_spend
active_offer_a_customers = len(
    active_df[active_df["campaign_arm"] == "Cashback Offer A"]
)
revenue_c = active_offer_a_customers * active_lift

print("\n=== OPPORTUNITY SIZING SUMMARY ===")
print(f"Scenario A (Unsegmented Rollout Total Revenue): ${revenue_a:,.2f}")
print(f"Scenario B (Precision Targeted Total Revenue) : ${revenue_b:,.2f}")
print(
    f"Scenario C (Active Recency Filter Net Revenue): ${revenue_c:,.2f} "
    f"(Targeting {active_offer_a_customers} customers)"
)

