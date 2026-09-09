# credit-card-campaign-opportunity-sizing
Quantifies incremental revenue from targeted credit card campaigns — comparing universal rollout vs. precision segment-matched targeting using Python (pandas)
Data note

Real card-level campaign data isn't publicly available, so this analysis is built on the public Hillstrom E-Mail Analytics dataset, relabeled to simulate a credit-card cashback campaign:

Original field	Relabeled as
segment	campaign_arm (Cashback Offer A / B / Control)
spend	card_spend (post-campaign card spend)
visit	login_or_app_open (digital engagement)
conversion	activation (offer activated / first transaction)
mens / womens	revolver_flag / transactor_flag (past usage)
recency	recency (months since last card activity)

Customers are further segmented by past usage into Revolver Only, Transactor Only, Both, or Dormant.

Approach
Baseline campaign impact assessment — compares login rate, activation rate, and average card spend for each offer arm against the no-offer control, and derives incremental spend and net campaign revenue per arm.
Cross-segment lift analysis — breaks incremental card-spend lift down by customer behavior segment, to see which offer works best for which type of customer rather than assuming one offer fits everyone.
Opportunity sizing across the portfolio (64,000 cardholders) — projects total incremental revenue under three go-to-market scenarios:
Scenario A — Universal rollout: one offer sent to the entire portfolio
Scenario B — Precision targeting: each behavior segment matched to whichever offer performs best for it
Scenario C — Recency-filtered targeting: offer restricted to customers active in the last 3 months
Key finding

Precision, segment-matched targeting outperforms a universal rollout — sending the same offer to everyone leaves revenue on the table by over-serving segments that don't respond and under-serving those that do. (Run credit_card_campaign_analysis.py to reproduce the exact revenue figures for each scenario on your machine.)

Skills demonstrated

Python (pandas, numpy), campaign analytics, customer segmentation, incremental lift measurement, opportunity sizing / revenue modeling, targeting strategy design.

Files
credit_card_campaign_analysis.py — full analysis script
Run it
bash
pip install pandas numpy
python credit_card_campaign_analysis.py

Requires the Hillstrom dataset CSV (Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv) in the same directory — publicly available for download.
