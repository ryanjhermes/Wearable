# BACtrack Skyn — competitive synthesis

**Prepared 2026-09-17.** Sources: the 11 PDFs in this folder, plus web research on KHN Solutions
conducted 2026-09-17. Claims are attributed; anything unconfirmed is marked and listed at the end.

This is a competitor brief, not a design document. Nothing here is a decision.

---

## Bottom line

BACtrack Skyn is the most credible wrist-worn alcohol biosensor in existence and the closest analogue
to what we are building. It won NIAAA's $200,000 Wearable Alcohol Biosensor Challenge in 2016.

**Ten years later it still cannot be sold to a consumer.** It is a $99/month, FDA-uncleared,
research-use-only instrument with a dead consumer storefront. Its own validation literature — largely
funded and supported by BACtrack — documents three unsolved problems:

1. **It cannot produce a BAC number.** Translating transdermal alcohol concentration (TAC) to blood
   alcohol has no reliable method. The device markets "an estimate of your % BAC range," not a value.
2. **Its timing is unpredictable per person.** Mean lag to blood alcohol is 23.9 min with a standard
   deviation of 26.1 min — the variance exceeds the mean.
3. **It only collects data when it is charged and worn**, and in the hardest field study it captured
   24% of available person-days, with 97.4% of that loss attributed to battery.

The strategic read: **direct ethanol measurement at the wrist is a solved sensing problem and an
unsolved product problem.** The competitive opening is not better ethanol detection. It is everything
downstream of it.

---

## The company

| | |
|---|---|
| Entity | KHN Solutions (LLC in FDA filings, Inc. in recent patent assignments) |
| Founded | 2001, by Keith Nothacker (founder & CEO), as a UPenn senior |
| HQ | San Francisco, CA |
| Ownership | Private. **No disclosed venture funding** — apparently bootstrapped on breathalyzer revenue |
| Core business | 23 consumer/professional breathalyzer SKUs, $42.99–$149.99, plus recurring calibration ($19.99–$54.99) and mouthpiece revenue |
| B2B | `BACtrack View` remote monitoring sold to courts and custody cases (pricing not public) |

The important structural fact: **Skyn is not the business.** The business is breathalyzers with a
consumables-and-calibration annuity. Skyn is a ten-year R&D program that has not reached market. That
tells us the company can outlast us financially, but is not moving fast on this product line.

## What Skyn actually is

- Electrochemical **fuel cell**, same sensing principle as the SCRAM ankle monitor, but with **passive
  airflow and no pump** — that is what shrinks it and lets it sample fast.
- **Samples every 20 s** (~90× SCRAM's 30-minute rate). 37 g, 4.7 × 2.5 × 0.6 cm.
- Worn on the **inside of the wrist**, chosen to raise sensitivity and cut lag.
- Also logs **skin temperature and motion** — used for wear detection only, **not** for correcting TAC.
- Marketed: up to 10-day battery, 4 h charge, ~72 h on-device storage, water-resistant (not waterproof),
  **iOS only**.
- Generations: 2016 prototype → 2018 prototype → T10 → T15.

**Commercial status, verified 2026-09-17:** $99/month research license only. `skyn.bactrack.com`'s
product endpoint returns zero purchasable SKUs; its consumer pages (`how-it-works`, `product-roadmap`,
`faq`) all 404. Skyn does not appear in the main BACtrack store. Site-wide disclaimer: *"For
Investigational Use Only… not cleared or approved by the US FDA."* A separate Criminal Justice B2B
page exists, quote-request only.

---

## What the evidence says

### Detection works. This is settled — do not attack it.

The largest validation (Fairbairn et al. 2025, *Drug and Alcohol Dependence* 266:112519 — the file
named `elsevier-...` in this folder), n=100, 5.39M readings, 14 ambulatory days:

- **AUROC 0.966, sensitivity 89.8%, specificity 90.6%.**

Older T10 hardware was much weaker in the field (Penn State 2023: sensitivity 55.5%, specificity 86.4%,
44.5% false negatives). **Do not cite the weak numbers as if they describe current hardware** — they
describe a superseded generation. Skyn detects *that* someone drank, reliably.

### Quantification does not work. This is the opening.

| Measure | Skyn vs self-report (field, n=11) | SCRAM |
|---|---|---|
| Peak intensity | **r = 0.35** | 0.78 |
| Area under curve | 0.52 | 0.79 |
| Estimated BAC | 0.30 | 0.61 |
| Rise rate agreement | **0.18–0.19, not significant** | — |

> "TAC is not quantitatively equivalent to BAC or BrAC and there are not currently reliable methods for
> translating TAC to BAC" — Penn State validation study, p.2

> "data from the current Skyn prototype represents a raw value… has not been standardized to include a
> meaningful zero metric or reflect a scale comparable to BAC" — Fairbairn ACER, p.21

The device has **no true zero** and a **person-varying baseline**. Every study builds its own ad-hoc
episode-detection rules; the manufacturer ships none.

### Timing is the deepest structural weakness.

| | Skyn | SCRAM |
|---|---|---|
| Time to first detection | 22.1 min (SD 12.4) | 22.5 min (SD 13.0) |
| Peak TAC vs peak breath alcohol | **+54 min** | +120 min |
| Mean lag across the curve | **23.9 min, SD 26.1** | 68.6 min, SD 36.8 |

Skyn roughly halves SCRAM's lag. But **the standard deviation exceeds the mean**, and per-device means
range 16.5–32.5 min with SDs to 39 min. A group-mean correction cannot recover an individual's
real-time BAC. Across the wider literature, lag estimates span **30 minutes to 5 hours**.

### Direct measurement carries confounds we do not inherit.

- **Environmental ethanol is indistinguishable from drinking.** Hand sanitizer and cologne produce
  steep false peaks. Penn State's cleaning rules **deleted 260 of 414 candidate episodes (63%)**;
  Richards deleted 38%. Wrist siting is *worse* for this than ankle.
- **Sensor accuracy decays with device age.** AUROC 0.87 within 3 months of shipment vs 0.79 after; the
  drinking threshold moved 56 → 173 h·µg/L between cohorts, so one cohort's rules gave only 70%
  specificity in the next. One study suggests the membrane "likely needs replaced periodically."
- **It cannot detect 1–2 drink episodes**, even after lowering the threshold.

### Deployment is where it actually breaks.

| Study | Wear/data capture |
|---|---|
| Ash 2022 (the "Yale" file), 14-day trial | **158 of 658 person-days = 24%.** 97.4% of loss attributed to battery |
| Fairbairn 2025, n=100 (best case) | 92.8% median wear, but 19.3 h median recording gap per participant |
| Rosenberg (preprint, n=5) | 96% of days; the one loss was a dead battery |

Observed battery was **24–72 h against a 72 h advertised spec**. On-device storage is ~72 h and **data
are overwritten if not synced** within it. One study lost days because staff missed a download.

**Acceptability, though, is excellent** — and this matters, because it means comfort is not the
differentiator. Versus SCRAM: physical discomfort 4% vs 53%, social discomfort 0% vs 40%, interferes
with clothing 0% vs 51%. No participant refused the Skyn; five refused the SCRAM ankle unit.

### What the researchers say is missing

Their wish-list is close to a product spec, and it is instructive that most of it is not about sensing:

- ≥1 week of real battery and untethered storage
- Waterproofing
- **A battery/status indicator** — neither device nor app shows battery level
- A trustworthy **wear-detection** algorithm (Skyn has none; temperature cutoffs vary by season)
- **Automated drinking-vs-interferent scoring** — the manufacturer ships no detection rules at all
- Tamper-evident attachment and wearer identification (blocks justice and contingency-management use)

---

## Where we can differentiate

Our approach is fundamentally different: we infer intoxication from **physiological proxies** —
PPG-derived HR/HRV/perfusion index, skin temperature, ambient temperature/humidity, and 6-axis motion —
rather than measuring ethanol. That difference creates five real openings and one serious liability.

### 1. We are structurally immune to their two worst confounds

Hand sanitizer cannot raise our heart rate, and we have no membrane to drift. The 63% episode-deletion
rate and the AUROC 0.87→0.79 age decay are *categorical* weaknesses of fuel-cell sensing that we do not
inherit. This is the cleanest, most defensible claim we have, and it costs us nothing to make.

### 2. Latency is the prize — and it is ours to win or lose

Skyn's peak trails real blood alcohol by 54 minutes with unpredictable per-person variance. Cardiovascular
response to alcohol — HR elevation, peripheral vasodilation visible in perfusion index, HRV suppression —
is a *direct* physiological effect, not a diffusion process through the stratum corneum. There is a
strong prior that it is faster.

**This is our single biggest potential advantage and it is completely unvalidated.** We have measured
nothing. Treat it as the primary hypothesis to test, not a claim to market.

### 3. Every signal we collect is useful when sober

Skyn's output when nobody is drinking is a flat line. Ours is heart rate, sleep, activity and skin
temperature — the same data Whoop and Oura users wear daily by choice. This changes the compliance
economics that produced Skyn's 24% capture rate: a device with daily standalone value stays on the wrist.
Skyn's adherence problem is partly a *single-purpose-device* problem, and we are not a single-purpose
device.

### 4. Ambient de-confounding is native to our design

The literature names ambient temperature and humidity as confounds and **quantifies none of them**.
Skyn logs skin temperature but does not use it to correct TAC; one paper speculates its temp and motion
streams *might* explain TAC–BAC variance but never tests it. We carry a TMP117 skin sensor and an SHT40
ambient sensor as separate channels by design. That is a modelling advantage they have on the bench and
have not exploited.

### 5. Sub-threshold and outcome-based detection

Skyn cannot see 1–2 drinks. More interestingly: **Richards 2024 does not predict BAC at all** — it
predicts alcohol-induced *blackouts* from TAC curve shape (rise duration OR 2.65). Even the incumbent's
best research is retreating from the BAC number toward behavioural outcomes.

That is a strategic hint worth taking seriously. **"Impairment" or "risk state" may be both more
achievable and more useful than a BAC decimal**, and it is a target our channels suit — the LSM6DS3TR-C
gyro gives sway, tremor and gait instability, which are impairment signals with no transdermal analogue.

### The liability: battery, where we are currently far behind

Their #1 documented failure is battery — 24–72 h observed. **Our 250 mAh cell gives 3–4 h.** We are an
order of magnitude worse on the exact axis that destroyed their field studies, and our own documentation
already names battery as the binding constraint that prevents capturing a full drinking session.

Related: our locked constraints cut all status LEDs, but "no battery indicator" is an explicit complaint
in this literature. Two exposed test pads are not a user-facing status signal. Worth revisiting whether a
single DNP-able indicator earns its ~1 mm².

### Summary

| Axis | Skyn | Us | Verdict |
|---|---|---|---|
| Detects that drinking occurred | AUROC 0.966 | unknown | **They win. Don't fight here** |
| Quantifies how much | r = 0.35 | unknown | **Open — their weakest point** |
| Real-time responsiveness | +54 min, SD 26 | untested, likely faster | **Our biggest opportunity** |
| Environmental false positives | 63% episode deletion | immune by construction | **We win structurally** |
| Sensor drift / consumable | AUROC decays with age | no consumable | **We win structurally** |
| Value when sober | none | HR, sleep, activity | **We win** |
| Battery | 24–72 h (10 d claimed) | 3–4 h | **We lose badly** |
| Comfort / acceptability | excellent | unknown | **Parity at best** |
| Regulatory standing | FDA-uncleared after 10 yrs | none | **Both blocked** |
| Validation evidence | ~8 peer-reviewed studies | zero | **They win decisively** |

---

## Two cautions

**The regulatory ceiling is the same for us, and we will hit it with weaker evidence.** Skyn spent ten
years and an NIH grand prize and still ships "For Investigational Use Only… should not be used as a tool
to determine whether you should operate a motor vehicle." Any plan that depends on users making driving
decisions from our output inherits that ceiling. KHN has four FDA 510(k) clearances — **all breath
testers, none transdermal.**

**They have patents and they litigate.** KHN holds at least seven patents around transdermal alcohol
monitoring. Those read as ethanol-sensing *hardware* claims (sensor + microporous membrane + housing +
wrist fastener), which is not our architecture. But **US12076144, "Wearable system and method for
monitoring intoxication," has not been read** — the research hit a 503 before claim 1. If that claims
intoxication monitoring beyond direct ethanol sensing, it is the single most relevant IP item to this
project. It should be checked by someone qualified before any commercial step. A search for patents
claiming intoxication inference from HR/HRV/temperature/accelerometry found no clean hit, but that is a
non-exhaustive negative result, not a freedom-to-operate opinion.

---

## Unverified — do not cite without checking

1. Funding, headcount and ownership (~30 employees, $200K) — search snippets only, pages not fetched.
2. Whether Skyn has a consumable. **Absence of evidence only.** The $99/month subscription may exist
   precisely to amortize sensor replacement; one paper suggests the membrane needs periodic replacement.
3. Whether a Skyn developer SDK exists. `developer.bactrack.com/documentation` returns 404.
4. What the $99/month covers — per device, minimum term, portal included.
5. `US12076144` claim scope (see above).
6. Competitor statuses (Smart Start BARE, Milo/Proof ION, Quantac, Soberlink) — snippets only.
7. NIAAA challenge pages and the vendor-promoted Daubert/Frye report — snippets only. Note that report
   covers BACtrack **View** (breath), **not** Skyn; do not read it across.

## Folder housekeeping

- `Leeman-STEADY-paper.pdf` is **not a wearable study** — it is a smartphone breathalyzer app trial
  (Leeman 2021, *Psychology of Addictive Behaviors*) and mentions transdermal sensing only in its
  reference list. Possibly filed here by mistake.
- `Wearable-alcohol-monitors-...-pilot-study.pdf` and `...-pilot-study-1.pdf` are byte-identical
  duplicates (same SHA-256).
- `elsevier-wearable-alcohol-biosensor-report-2024.pdf` is not a market report. It is Fairbairn et al.
  2025, *Drug and Alcohol Dependence* 266:112519 — the largest Skyn validation to date, and the most
  important single file in this folder.
- Unit ambiguity across the corpus: Penn State reports TAC in mg/L air, Richards uses µg/L air for the
  same numeric threshold. Unresolved by these documents.
