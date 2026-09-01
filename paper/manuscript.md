# Consumer AI Dispatch Advice Under Unresolved Port-Access Conditions: A 96-Response Challenge-Set Evaluation

**Short title:** Consumer AI advice under unresolved port-access conditions  
**Authors:** [Author 1], [Author 2], [Author 3]  
**Affiliations:** [Affiliation(s)]  
**Corresponding author:** [Name, postal address, email]  
**ORCID identifiers:** [Add as applicable]  
**Manuscript type:** Original research / methods and evaluation study  
**Version:** Working manuscript, 31 August 2026

## Abstract

**Background:** A pre-dispatch question about a single truck movement may depend on vehicle measurements, route classification, permit scope, current restrictions, public-road authorities, Port Authority rules, and terminal requirements. A consumer AI product can state generally correct rules yet still communicate that a present trip may proceed before those conditions are resolved.

**Objective:** To evaluate whether four consumer AI products communicated explicit or conditional present-trip clearance when material facts, authority handoffs, current conditions, or source conflicts remained unresolved in scenario-based questions about access to APM Terminals Elizabeth.

**Methods:** We conducted a prospectively frozen challenge-set evaluation comprising six scenario families, two prompt variants, four free consumer AI product surfaces, and two repeated outputs per product × scenario × variant cell (6 × 2 × 4 × 2 = 96 responses). Every scenario’s frozen reference disposition required withholding present-trip clearance pending verification. The products were ChatGPT, Claude, Copilot, and Gemini in their recorded free/default surface modes. Two human reviewers independently classified all 96 responses under a frozen codebook. The primary endpoint was an explicit or conditional present-trip dispatch, route, permit, authority-coverage, or terminal-entry go while at least one scenario-defined material condition remained unresolved. Agreement was calculated from the locked originals before Reviewer A adjudicated only the five disagreements. We report counts, observed proportions, and paired repetition summaries.

**Results:** Scenario-specific endpoint-positive counts were 1/16 for missing axle facts, 8/16 for dimensions and local access, 1/16 for cross-authority permit coverage, 5/16 for mutable Port Street restrictions, and 0/16 for each of the DTR-conflict and gate-credential scenarios. Across all six scenarios, 15 of 96 captured responses met the primary endpoint (15.6%). An analysis-stage descriptive synthesis of the two scenarios centered on local-route access or mutable route restrictions contained 13 of the 15 endpoint-positive responses: 13/32 (40.6%), compared with 2/64 (3.1%) across the other four scenarios. Before adjudication, reviewers agreed on 91/96 labels (94.8%); unweighted Cohen’s κ was 0.824 (paired response-level BCa 95% CI, 0.650–0.938). Forty-five of 48 matched repetition pairs received the same final label.

**Conclusions:** Within this frozen unresolved-condition challenge set, consumer AI products sometimes communicated present-trip clearance before the scenario-defined conditions for that clearance had been established. The observed endpoint was concentrated in two route-oriented scenarios, generating a hypothesis for factorized replication. The study does not estimate the prevalence of problematic logistics advice, establish comparative product safety, show that route complexity or prompt pressure caused the observed pattern, or prove that any real trip would have been illegal or harmful.

**Keywords:** consumer artificial intelligence; large language models; drayage; port access; dispatch; regulatory compliance; human evaluation; Cohen’s kappa; operational decision support

## 1. Introduction

Operational questions in last-mile drayage often compress a layered decision into a deceptively simple request: “Can I release this truck?” For a movement into a marine terminal, that decision may turn on axle weights and spacings, loaded dimensions, network and local-route classification, permit scope, mutable roadway conditions, driver credentials, Port Authority requirements, and terminal appointment or training status. The existence of a generally applicable weight limit, permit, or route designation does not necessarily resolve whether a particular movement may proceed at a particular time.

Consumer conversational AI products make it easy to ask such questions in ordinary language. Their output can combine rules, qualifications, and a bottom-line recommendation in one response. Prior work on general-purpose language systems has emphasized broad risk taxonomies, factuality, calibration, and multidimensional evaluation [1–4]. For an operational decision, however, factual recitation and action-level disposition are distinct. A response may mention the right threshold or advise checking a source while still converting an unresolved condition into a conditional present-trip “go.” Conversely, a response may describe several hypothetical pathways without clearing the current trip. Evaluating the disposition therefore requires a rule that operates on what the response actually authorizes, not merely on whether it contains relevant regulatory language.

This study examines that distinction in a bounded port-access setting. A locked evidence record identified two inbound paths to APM Terminals Elizabeth and the physical and regulatory layers relevant to them. Six prompts were then constructed to resemble pre-dispatch questions while varying missing facts, authority arrangements, and forms of ambiguity. Every scenario was deliberately an unresolved case: its frozen reference disposition was to withhold present-trip clearance until the specified uncertainty was resolved. The resulting design is therefore a challenge set for inappropriate clearance, not a balanced benchmark of overall legal accuracy, usefulness, or decision quality.

The study’s primary question was whether four free consumer AI product surfaces would communicate explicit or conditional present-trip clearance when safe resolution required preserving scenario-defined missing facts, authority handoffs, mutable conditions, or source conflicts. Four design commitments distinguish the evaluation. First, the evidence boundary, prompts, product set, repetitions, reference dispositions, endpoint, and review rules were hash-locked before collection. Second, the matrix included multiple ambiguity types and two outputs from every exact product × scenario × prompt-variant cell. Third, two humans independently applied a frozen operational-disposition codebook, with agreement measured from their locked originals before Reviewer A resolved the disagreements. Fourth, product identity was joined to the frozen final labels only after human review and adjudication.

The intended contribution is narrow but practical: to define and apply an operational endpoint that distinguishes stating a relevant rule from clearing a present trip. The paper reports the resulting 96-response matrix, the scenario-level concentration of endpoint-positive outputs, the limited repetition check, and the boundaries required to interpret those findings responsibly.

## 2. Study setting and evidence boundary

### 2.1 Port-access setting

The setting was inbound container drayage to APM Terminals Elizabeth in Elizabeth, New Jersey. The locked evidence repository identified two processed inbound paths [5]:

- **Path A:** New Jersey Turnpike southbound → Exit 13A → North Avenue → McLester Street → Tripoli Street.

- **Path B:** U.S. Route 1 & 9 southbound → North Avenue East → North Avenue → McLester Street → Tripoli Street.

Across these two retained approaches, the official roadway data classified segments as Highway Authority, State, County, or Municipal before the movement reached separately governed Port Authority and private-terminal access layers [5]. That classification establishes the study’s multi-layer setting; it does not certify either path for every vehicle, load, or date.

These paths illustrate why the final miles cannot be represented as one undifferentiated regulatory segment. Depending on the movement, the operational question can implicate New Jersey size-and-weight and truck-access rules [6–8], New Jersey Turnpike Authority roadway rules [9], county or municipal restrictions, Port Authority marine-terminal provisions [10,11], federal secure-access credentials [12], and private terminal procedures [11,13]. The study did not assume that possession of one permit or satisfaction of one layer supplied blanket authorization across the others.

The two route-oriented experimental scenarios must not be conflated with the repository’s two processed inbound paths. Scenario S2 used the Path B/North Avenue–County Route 624 local-access issue. Scenario S4 instead concerned Port Street between Brewster Road and Marlin Street and a prompt-supplied, dated NJPASS bulletin. Port Street was not part of the repository’s locked processed route files. The dated bulletin in S4 was treated only as a scenario fact whose continuing status remained unresolved, not as a repository-established current condition.

The frozen S4 disposition record also identified a stored route-survey threshold, but neither the frozen prompt nor the locked rule catalog supplied a numerical threshold. No numerical route-survey threshold was asserted in this manuscript or used to determine the primary endpoint. S4’s withholding disposition followed from the explicitly unresolved currentness, permit route, police instructions, Port Authority approval, and terminal approval.

### 2.2 Locked evidence record

The evidence record was the public `last-mile-drayage-pilot` repository at commit `7fe49ebb0fc8376f0f183e1f614c06d284c13343` [5]. Eight retained files were hash-locked before collection: the repository README, source registry, entity nodes, physical nodes, physical edges, regulatory nodes, regulatory edges, and physical–regulatory coupling edges. The locked files established the retained entities, physical route structure, authority layers, exact rule text and source identifiers, and the linkages used to define each scenario’s known and unresolved conditions.

The source set included official or operator materials from the New Jersey Department of Transportation, New Jersey Turnpike Authority, Port Authority of New York and New Jersey, federal regulations, APM Terminals, Union County, the City of Elizabeth, and official roadway GIS services [5–13]. Source statements, applicability classifications, and compliance conclusions were kept conceptually separate. A map or operator page was used only for the kind of fact it could establish.

This evidence record was intentionally bounded. It did not purport to identify every restriction, credential, weather condition, vehicle defect, police direction, gate condition, or other fact that could affect an actual trip. Mutable observations required live rechecking. Prompt-supplied dated observations remained scenario facts unless independently established by the locked record. Source conflicts that the record did not resolve remained unresolved. Accordingly, the reference dispositions defined what could be concluded from the frozen evidence and prompt—not the ultimate legality of an unobserved real-world movement.

**Figure 1. Study logic.**

```text
Locked evidence record establishes what is known and unresolved
                              ↓
Four consumer AI products answer realistic, frozen pre-dispatch prompts
                              ↓
Two independent human reviewers classify the operational disposition
                              ↓
Simple descriptive statistics summarize the captured outputs
```

## 3. Methods

### 3.1 Design, unit of analysis, and prospective freeze

The unit of analysis was one complete consumer-product response to one frozen prompt. The factorial matrix was:

```text
6 scenario families × 2 prompt variants × 4 products × 2 repetitions
= 96 planned responses
```

The study files described the matrix as frozen before collection. At 14:45:08 EDT on 30 August 2026, the design, gold reference dispositions, evidence lock, human-rating codebook, initial collection schedule, and all 12 prompt texts were cryptographically locked. The lock stated that no primary response existed before it was created. This internal, prospective hash lock is not described as public preregistration.

The frozen design required each scenario to be reported separately before aggregate interpretation. It also specified that product comparisons were descriptive and secondary, that the two original human rating files could not be selectively chosen after outcomes were known, and that failed cells could not be silently replaced. All 96 planned cells ultimately yielded usable captured responses, so no missing-run bound was required.

### 3.2 Scenario construction

The six scenario families varied the missing or unresolved input, the arrangement of operational or regulatory authorities, and the form of ambiguity. Each prompt specified a movement date of 2 September 2026. The prompt facts differed across scenarios, but every frozen reference disposition required withholding the relevant present-trip clearance until the listed issue was resolved. Table 1 summarizes the challenge set.

**Table 1. Frozen scenario families and reference dispositions.**

| ID | Scenario focus | Material unresolved conditions | Authority-layer structure | Frozen reference disposition |
|---|---|---|---|---|
| S1 | 80,000-lb combination with axle facts missing | Axle/group weights, axle spacings, loaded dimensions, divisibility, exact route, timing, and permit status | Primarily New Jersey public-road size, weight, and permit rules | Withhold present-trip permit and dispatch clearance |
| S2 | Dimensions and local terminal access | Loaded width, height, semitrailer length, whether local segments were unrestricted, and whether the sequence was the direct terminal-access route | State access-network rule plus county/local terminal-access conditions | Withhold present-trip route and oversize clearance |
| S3 | 88,000-lb sealed container and permit handoff | Turnpike approval, county/local handling, Port Authority coverage, current permit route, and terminal acceptance | State, toll-road, county/local, Port Authority, and terminal layers | Withhold cross-authority route clearance |
| S4 | Overdimensional Port Street movement and mutable restrictions | Current bulletin status, permit route, escort instructions, Port Authority approval, terminal approval, closure/lane/detour status | State permit portal, police instructions, Port Authority, and terminal layers | Withhold route clearance pending live recheck and required authorizations |
| S5 | Used 2010 diesel, unknown DTR status, and conflicting tariff language | Current DTR verification, ownership amendment, RFID association, and authoritative resolution of a tariff-text conflict | Port Authority registry/tariff rules plus terminal entry | Withhold entry clearance and preserve the unresolved regulatory fork |
| S6 | Road-legal vehicle with gate conditions unresolved | Driver TWIC and SeaLink status, APM safety induction, appointment, and same-day transaction status | Federal credentialing, Port Authority access, and private terminal operations | Withhold terminal-entry clearance |

S1 tested whether a gross weight of exactly 80,000 lb and a five-axle configuration would be treated as sufficient despite missing axle and bridge-formula inputs. S2 required distinguishing a route’s absence from the New Jersey Access Network list from the separate conditional rule permitting direct access to a terminal on local unrestricted roads. S3 supplied a New Jersey annual ocean-container permit but left its coverage across toll, local, Port Authority, and terminal layers unresolved. S4 supplied a state permit and a dated bulletin while explicitly withholding current route, escort, and terminal confirmations. S5 presented temporal tariff language and an unresolved DTR record that could not be repaired by inference. S6 made public-road and vehicle conditions compliant while leaving the driver’s credentials and terminal-operational conditions unknown.

Because all six scenarios required withholding clearance, the matrix measures one asymmetric failure mode: inappropriate clearance under unresolved conditions. It does not estimate false-denial frequency, over-caution, or balanced decision accuracy. A categorical “no” could still be factually poor or operationally unhelpful without meeting this study’s clearance endpoint.

### 3.3 Prompt variants and repeated outputs

Each scenario had a neutral and a dispatch-pressure variant. The factual scenario and substantive question were held constant. The pressure version added one sentence:

> “The driver is waiting and I need a yes-or-no dispatch decision now; please do not send me away to call multiple agencies unless that is genuinely necessary.”

The variant was intended to examine the same unresolved decision under a stronger request for immediacy. Evaluating more than one prompt formulation can expose wording-sensitive behavior that a single formulation would not show [17]. The design did not document randomized collection order, and the analysis did not treat any observed variant difference as causal.

Because a single generated output leaves run-to-run variation unobserved, two outputs were captured for each exact product × scenario × variant cell [16]. These were repeated product-output runs, not independent people, separate logistics cases, or a longitudinal product sample. With only two repetitions per exact cell, they provide a limited descriptive check on whether the aggregate finding appeared in both runs; they do not characterize long-run response distributions.

### 3.4 Consumer AI products and response collection

The sampled entities were four free consumer AI product surfaces, not fixed underlying model APIs. The visible surface modes recorded during collection were:

- **ChatGPT:** `free_default_unpersonalized`;

- **Claude:** `Sonnet 5 · Medium`;

- **Copilot:** `Smart`; and

- **Gemini:** `Gemini Flash`.

These labels describe the consumer interfaces as displayed during collection. They do not guarantee a stable or fully disclosed underlying model, tool configuration, routing policy, or system instruction.

All responses were captured on 30 August 2026 between 18:48:32 and 20:00:03 UTC. Each run used a fresh conversation context: temporary fresh chats for ChatGPT and Copilot, incognito fresh chats for Claude, and signed-in fresh chats for Gemini. Prior conversational context was prohibited. Prompt text had to match its frozen SHA-256 hash, scoring during collection was prohibited, and no manual prompt repair was permitted after submission. Complete responses were copied using each product’s native copy control and stored with response hashes and capture metadata.

The protocol allowed a maximum of two attempts for each scheduled cell. Ninety responses were obtained on the first attempt and six on the second. All 96 final captures were recorded as complete and usable; none was substituted beyond the frozen attempt rule.

### 3.5 Primary endpoint

The primary endpoint was whether a response communicated an explicit or conditional present-trip dispatch, route, permit, authority-coverage, or terminal-entry go while at least one scenario-prespecified material input, authority handoff, current condition, or source conflict remained unresolved.

Reviewers assigned one of three primary labels:

- **Yes:** the response communicated explicit or conditional present-trip clearance while a scenario-defined material issue remained unresolved;

- **No:** the response genuinely withheld present-trip clearance pending the required verification, or did not communicate a present-trip clearance; or

- **Unclear:** classification would require adding meaning not present in the response.

The frozen movement-disposition categories distinguished explicit clearance, conditional clearance, withheld clearance, and unclear/nonresponsive output. General thresholds and hypothetical forks were allowed. They became endpoint-positive only when the response converted them into an explicit or conditional go for the present trip. A false categorical denial was not converted into a positive clearance endpoint.

The endpoint is an operational-risk proxy. An endpoint-positive response does not by itself establish that the route was legally prohibited, that the response contained a factual legal error, that a dispatcher or driver would act on it, or that delay, enforcement, denial of entry, property damage, injury, or any other harm would result.

### 3.6 Independent human review and adjudication

Two human reviewers independently classified all 96 responses using the frozen codebook. Administrative product identity, original run identifiers, repetition number, collection order, timestamps, and attempt history were excluded from the review packets. Product masking could not be guaranteed if a product identified itself within its own response; the study therefore describes identity as masked where feasible rather than fully blinded.

For every response, reviewers recorded a movement disposition, primary endpoint label, decisive quotation, unresolved material input, written rationale, and ambiguity flag. The frozen instructions required an exact supporting quotation and written rationale for every `yes` or `unclear` primary label. Reviewers could not see each other’s labels or aggregate outcomes before the two original files were locked.

Pre-adjudication agreement was calculated from the two locked original primary labels, joined only by anonymous response identifier, before product identity was opened. Reviewer A then adjudicated only the five primary-endpoint disagreements through a separate product-masked packet. The two original labels remained preserved; the adjudication was not treated as an additional independent rating or observation. Because the adjudicator was one of the original reviewers, this was not independent third-party adjudication. Final labels were frozen while product identity remained unopened, after which the administrative product, scenario, prompt-variant, and repetition fields were joined for descriptive analysis.

Reviewer and adjudicator backgrounds, any formal codebook familiarization, and study-role conflicts should be documented before journal submission: **[insert reviewer qualification and relationship statement]**.

The Reviewer B export stored one common timestamp across all item records; those timestamps were not used to infer item-by-item review timing. Before submission, the authors should add a workflow note confirming the independent review and describing the final JSON export or conversion step: **[insert Reviewer B workflow/export note]**.

### 3.7 Statistical analysis

The final primary endpoint was summarized as counts and observed proportions. Because the experiment used a deliberately constructed matrix of fixed scenarios, product surfaces, and prompt variants, with paired repetitions within exact conditions and no population sampling frame, endpoint proportions are reported descriptively without population confidence intervals.

Scenario results were examined in the frozen order before the aggregate. Product, prompt-variant, repetition, and route-group summaries were secondary and descriptive. No pairwise product tests or causal hypothesis tests were performed. The grouping of S2 and S4 was an analysis-stage descriptive synthesis of the two scenarios explicitly centered on local-route access or mutable route restrictions; it was not a prospectively frozen contrast. Scenario identity, ambiguity type, authority arrangement, prompt facts, and wording were not independently varied within scenario families, so the study cannot isolate a route-specific mechanism.

Repetition stability was summarized across the 48 matched product × scenario × variant pairs by counting `no→no`, `no→yes`, `yes→no`, and `yes→yes` label patterns. This was not an inter-rater statistic.

Human agreement was summarized as exact agreement and unweighted Cohen’s κ on the three nominal primary labels (`yes`, `no`, `unclear`) [14]. The κ interval was computed using a paired response-level nonparametric bias-corrected and accelerated (BCa) bootstrap with 100,000 valid resamples; each resample retained the two labels belonging to the same anonymous response [15]. Agreement was measured before adjudication.

All integrity checks, joins, summaries, and agreement statistics were implemented in auditable Python scripts using the standard library. No automated system semantically scored, relabeled, or adjudicated a product response.

### 3.8 Frozen secondary constructs and reporting boundary

The design file listed additional secondary constructs, including an explicit trip-wide hold, scenario-specific missing-fact identification, authority separation, dispatch-time recheck requirements, false categorical denial, unsupported authority or fabrication, and preservation of condition-specific forks. Most were not implemented as separate structured fields in the frozen human-rating codebook or finalized dataset. To avoid post-outcome recoding, this manuscript does not reconstruct them retrospectively. It reports the frozen primary endpoint, descriptive summaries derived from the frozen matrix fields, pre-adjudication agreement, and the adjudication outcome. Appendix A provides a protocol-to-report crosswalk.

## 4. Results

### 4.1 Collection completeness and human agreement

All 96 planned product-response cells were captured and scored. Before adjudication, the two reviewers agreed on 91 of 96 primary labels (94.8%). Unweighted Cohen’s κ was 0.824, with a paired response-level BCa 95% confidence interval of 0.650–0.938. Reviewer A assigned 16 `yes`, 79 `no`, and one `unclear`; Reviewer B assigned 15 `yes`, 79 `no`, and two `unclear`. Thus, the final absence of `unclear` labels should not be interpreted as an absence of classification difficulty during independent review.

The five primary-label disagreements were adjudicated to three final `no` labels and two final `yes` labels. No final label remained `unclear` after adjudication.

**Table 2. Pre-adjudication primary-endpoint agreement and adjudication.**

| Measure | Result |
|---|---:|
| Responses independently rated by each reviewer | 96 |
| Exact agreements | 91/96 (94.8%) |
| Unweighted Cohen’s κ | 0.824 |
| Paired-response BCa 95% CI for κ | 0.650–0.938 |
| Bootstrap resamples | 100,000 |
| Primary-label disagreements | 5 |
| Adjudicated as final `yes` | 2 |
| Adjudicated as final `no` | 3 |

### 4.2 Endpoint-positive responses varied sharply by scenario

Table 3 reports the six scenario families before the overall aggregate. S2, which required distinguishing access-network classification from a conditional local terminal-access rule while dimensions and local restrictions remained unknown, contributed 8/16 endpoint-positive outputs (50.0%). S4, which required live verification of an overdimensional Port Street movement across permit, police, Port Authority, and terminal layers, contributed 5/16 (31.3%). S1 and S3 each contributed 1/16 (6.3%). No endpoint-positive response was observed in S5 or S6 (0/16 in each).

**Table 3. Primary endpoint by scenario family.**

| Scenario | Final `yes` | Final `no` | Endpoint-positive share |
|---|---:|---:|---:|
| S1: missing axle facts | 1/16 | 15/16 | 6.3% |
| S2: dimensions and local access | 8/16 | 8/16 | 50.0% |
| S3: cross-authority permit handoff | 1/16 | 15/16 | 6.3% |
| S4: mutable Port Street restrictions | 5/16 | 11/16 | 31.3% |
| S5: DTR conflict | 0/16 | 16/16 | 0.0% |
| S6: gate credentials | 0/16 | 16/16 | 0.0% |

### 4.3 Overall endpoint-positive share

Across the full challenge matrix, 15 of 96 captured responses met the primary endpoint and 81 did not. The observed endpoint-positive share was 15.6%. This denominator is 96 captured product responses—not 96 drivers, trips, users, or independent real-world decisions.

### 4.4 Descriptive concentration in the two route-oriented scenarios

Thirteen of the 15 endpoint-positive responses occurred in S2 or S4. Together, those two scenarios contributed 13/32 endpoint-positive outputs (40.6%). The remaining four scenarios contributed 2/64 (3.1%).

**Table 4. Overall result and descriptive route-oriented synthesis.**

| Scope | Final `yes` | Final `no` | Endpoint-positive share |
|---|---:|---:|---:|
| S2 and S4 | 13/32 | 19/32 | 40.6% |
| S1, S3, S5, and S6 | 2/64 | 62/64 | 3.1% |
| All six scenarios | 15/96 | 81/96 | 15.6% |

This contrast is descriptive and hypothesis-generating. S2 and S4 differ from the remaining scenarios not only in route orientation, but also in their prompt facts, applicable rules, ambiguity types, and authority configurations. The concentration cannot establish that route specificity or authority complexity caused the endpoint-positive responses.

### 4.5 Prompt-variant and repetition summaries

The observed endpoint-positive share was higher under dispatch-pressure wording than under neutral wording: 11/48 (22.9%) compared with 4/48 (8.3%). This was a descriptive comparison; no causal effect of wording was estimated.

The aggregate pattern appeared in both repetitions. Repetition 1 contained 8/48 endpoint-positive outputs (16.7%), and repetition 2 contained 7/48 (14.6%). Among 48 matched product × scenario × variant pairs, 45 (93.8%) received the same final endpoint label. The pattern counts were 39 `no→no`, one `no→yes`, two `yes→no`, and six `yes→yes`.

**Table 5. Descriptive prompt-variant and repetition summaries.**

| Cut | Final `yes` | Final `no` | Endpoint-positive share |
|---|---:|---:|---:|
| Neutral wording | 4/48 | 44/48 | 8.3% |
| Dispatch-pressure wording | 11/48 | 37/48 | 22.9% |
| Repetition 1 | 8/48 | 40/48 | 16.7% |
| Repetition 2 | 7/48 | 41/48 | 14.6% |

### 4.6 Product summaries were descriptive and secondary

Observed endpoint-positive counts were 2/24 for ChatGPT, 5/24 for Claude, 8/24 for Copilot, and 0/24 for Gemini. Table 6 reports the corresponding observed proportions within the deliberately constructed product-specific samples.

**Table 6. Descriptive primary-endpoint summary by consumer product.**

| Product surface | Final `yes` | Final `no` | Endpoint-positive share |
|---|---:|---:|---:|
| ChatGPT | 2/24 | 22/24 | 8.3% |
| Claude | 5/24 | 19/24 | 20.8% |
| Copilot | 8/24 | 16/24 | 33.3% |
| Gemini | 0/24 | 24/24 | 0.0% |

These values do not establish durable comparative product performance. Each product had only four outputs per scenario after combining two variants and two repetitions, the products were observed during one compact collection window, and the sampled consumer surfaces may change over time. Zero observed endpoint-positive outputs in this all-withhold challenge set does not establish general accuracy, usefulness, or comparative safety.

## 5. Discussion

### 5.1 Principal finding

The locked research question received an affirmative but bounded answer: 15 of 96 responses communicated explicit or conditional present-trip clearance while a scenario-defined material condition remained unresolved. The behavior appeared in both repetitions and was observed from three of the four sampled consumer product surfaces. Thirteen of the 15 responses occurred in the two scenarios centered on local-route access or mutable route restrictions. Independent human review produced 94.8% exact agreement.

The result is most appropriately understood as evidence of a bounded operational-disposition failure mode, not a broad verdict about logistics advice or a prevalence estimate for ordinary logistics questions. The matrix intentionally selected unresolved cases for which the frozen reference disposition required withholding clearance. Within that boundary, however, an endpoint-positive response crossed a meaningful line: it moved from explaining rules or conditions to communicating that the present movement could proceed before the conditions for that movement had been established.

### 5.2 Evaluating a disposition is different from evaluating rule retrieval

The primary methodological contribution is the separation of rule recitation from action authorization. A response could state an accurate legal threshold and still meet the endpoint if it told the user that the current trip could proceed conditionally on a fact that had not been checked. The frozen codebook therefore asked reviewers to identify the movement disposition, the decisive language, and the material unresolved input. General thresholds and genuine holds were permitted; the endpoint turned on whether the response communicated a present-trip go.

This distinction matters for evaluating decision-support output. A factuality-only assessment could reward the presence of relevant numbers, agencies, or permit terms without capturing the operational effect of the conclusion. Conversely, a cautious response was not required to reproduce every rule in the repository to avoid the endpoint; it had to preserve the unresolved condition and withhold present-trip clearance. Future evaluations of operational advice can use this structure even when the governing domain, evidence sources, and reference conditions differ.

### 5.3 The S2/S4 concentration generates a route-boundary hypothesis

S2 required maintaining two legal distinctions simultaneously: absence from a listed access network was not itself a categorical prohibition, and a local terminal-access rule did not provide blanket approval without dimensions, direct-route status, and current local restrictions. S4 required maintaining temporal and institutional boundaries: a dated bulletin was not proof of current conditions, and a state permit did not by itself settle current police, Port Authority, route, or terminal approvals. In both scenarios, the response had to preserve the gap between a generally relevant rule and a present-trip routing decision.

The concentration of endpoint-positive outputs in these two scenarios is consistent with a hypothesis that route-boundary questions are particularly demanding for consumer AI products. This study cannot test that mechanism. Scenario identity was effectively one-to-one with ambiguity type and authority arrangement, and there was only one scenario instantiating each combination. Differences could instead reflect the exact wording, the particular rules, the facts omitted, the source material, or product-specific behavior. A causal or mechanism-focused follow-up would need several independently constructed scenarios for each proposed factor and a prospectively frozen contrast.

### 5.4 Prompt pressure and repeated outputs

Endpoint-positive outputs were observed more often in the pressure variants than in neutral variants. The pressure sentence asked for an immediate yes/no answer and discouraged referrals unless genuinely necessary, while leaving the substantive trip facts unchanged. That pattern is worth replicating, but the current study did not randomize collection order or fit a model that isolates wording from scenario, product, and repeated-cell dependence. It therefore supports only the descriptive statement that the observed share was higher under pressure wording—not that pressure caused the difference.

The two repetitions address a narrower concern: one output per cell would leave no direct observation of within-condition label variability. The total endpoint count was similar across repetitions (8 and 7), and 45 of 48 matched cells kept the same final label. Three cells changed. This indicates that the aggregate pattern appeared in both repeated passes while also demonstrating that an individual run need not reproduce the same disposition. Two repetitions remain far too few to estimate a stable cell-specific probability.

### 5.5 Product totals are bounded descriptive summaries

The product totals are transparent descriptive results, but the study was not designed to establish comparative product performance. Each total pools six qualitatively different scenarios, two prompt variants, and two repetitions. Underlying consumer-product routing and behavior may be dynamic, and the capture labels do not define immutable model versions. Moreover, the challenge set contains no safe-to-proceed controls. A product that always refused clearance would score zero on the primary endpoint even if its refusals were poorly reasoned, inaccurate, or unhelpful. The product table therefore cannot establish a general comparative safety or accuracy ordering.

### 5.6 Operational and evaluation implications

The findings support three bounded implications. First, a consumer-product response should not be treated as authoritative clearance in the tested circumstances merely because it cites relevant rules or provides a decisive conclusion. Second, mutable route conditions and authority handoffs need to remain explicit unresolved variables until the responsible source or authority confirms them. Third, evaluations of operational advice benefit from measuring the action-level disposition separately from factual content, using repeated outputs and independent human review.

The study does not show how dispatchers or drivers would interpret or act on these responses. It also does not quantify violations, denied entries, delays, costs, or physical harms. Those are distinct empirical questions requiring user studies, field data, or incident evidence.

## 6. Limitations

This study has substantial and deliberate limits.

First, it is a challenge-set evaluation of one port setting, one frozen trip-date context, and six constructed unresolved scenarios. The prompts were written to resemble pre-dispatch questions but were not validated as representative of the distribution of questions asked by working drivers or dispatchers.

Second, all six reference dispositions required withholding clearance. The study measures inappropriate clearance in unresolved cases. It does not measure balanced decision accuracy, false caution, unsupported categorical denials, factual completeness, citation quality, fabrication, usefulness, or whether a response eventually guides the user to the correct authority.

Third, the 96 rows are captured product responses, not independent people or trips. Every exact product × scenario × variant condition was repeated twice, creating a paired structure. The displayed proportions are descriptive and do not model repeated-cell dependence, shared product infrastructure, future product drift, or support population-prevalence inference.

Fourth, product, scenario, prompt-variant, and repetition summaries are descriptive. The design does not identify causal effects of route orientation, ambiguity type, authority complexity, dispatch pressure, or product. Scenario, ambiguity type, and authority configuration were not independently crossed. The S2/S4 grouping was not a prospectively frozen contrast.

Fifth, all product outputs were collected in approximately 72 minutes on one date. Consumer surfaces can change visible modes, hidden routing, system instructions, connected tools, or underlying models. The recorded surface labels provide a reproducibility snapshot, not a guarantee of future behavior.

Sixth, product identity was administratively masked where feasible, not guaranteed to be fully hidden. A product could reveal its identity within its response. Reviewer qualifications, formal familiarization procedures, authorship roles, and conflicts must be reported before submission. Although κ quantified agreement on the original labels, the final endpoint still depends on the frozen codebook and human interpretation.

Seventh, the evidence repository established the retained physical and regulatory boundary conditions; it did not certify actual-trip compliance or exhaust every fact that could affect a real movement. S4 additionally relied on a prompt-supplied dated observation that was explicitly not promoted to a current repository fact.

Eighth, the endpoint is an operational-risk proxy. It does not establish legal error, user reliance, actual dispatch, a violation, terminal denial, or harm. No driver, dispatcher, shipment, or vehicle was placed at operational risk by the experiment.

Finally, additional secondary constructs named in the frozen design were not reconstructed because most lacked frozen structured rating fields. This protects the study from outcome-informed semantic recoding, but it leaves questions about missing-fact identification, authority separation, unsupported claims, and false denials for a separately designed evaluation.

## 7. Future work

A useful next study would preserve the current endpoint while addressing the design’s asymmetry and confounding.

1. **Temporal replication:** repeat the exact frozen matrix at a later date to measure product drift without changing the prompts or scoring rule.

2. **Factorized scenario replication:** construct several independently sourced scenarios for each proposed mechanism—route classification, mutable currentness, permit handoff, missing dimensions, and credential status—so mechanism-level contrasts are not identical to scenario identity.

3. **Balanced controls:** add clearly safe-to-proceed cases and clearly prohibited cases under separately frozen rules if the objective expands to balanced accuracy, false caution, or false denial.

4. **Additional settings:** apply the same disposition endpoint at another port or terminal with its own locked evidence boundary.

5. **More output repetitions:** collect enough repeated outputs per exact condition to estimate cell-level variability before attempting comparative product inference.

6. **Separate qualitative study:** if wording patterns, unsupported authorities, or fabricated sources are of interest, define and freeze those endpoints before opening a new response set, then use prospectively instructed human reviewers rather than adding outcome-informed scoring to the current study.

## 8. Conclusion

In this frozen 96-response unresolved-condition challenge set, four consumer AI products sometimes communicated present-trip clearance before scenario-defined material conditions had been resolved. Fifteen responses met the operational endpoint, and 13 of those occurred in two route-oriented scenarios involving local-access classification or mutable route conditions. The design does not establish prevalence, causation, comparative product safety, or real-world illegality or harm. It does show why evaluating whether a system can state a rule is not enough: an operational evaluation must also ask whether the system preserves unresolved conditions when it tells a user whether a present trip may proceed.

## Data and code availability

The locked evidence repository is publicly available at <https://github.com/itsnotmarvin/last-mile-drayage-pilot> and is cited at exact commit `7fe49ebb0fc8376f0f183e1f614c06d284c13343` [5]. The study package contains the frozen design, 12 prompts and hashes, collection manifest, capture metadata, human codebook, original human ratings, disagreement-only adjudication, frozen final endpoint dataset, analysis scripts, and machine-readable result tables. A public deposit location for the complete study package should be added before submission: **[repository/DOI]**. If product terms restrict redistribution of verbatim outputs, the authors should state the exact restriction and release all permitted prompts, hashes, labels, analysis code, and aggregate tables.

## Ethics statement

No real truck was dispatched, no route authorization was issued, and no driver, dispatcher, shipment, or member of the public was enrolled as a study participant. Human reviewers classified generated text. The authors must insert the applicable institutional or venue-specific determination and reviewer privacy/consent statement before submission: **[ethics/IRB determination; reviewer consent and privacy treatment]**.

## Author contributions

**[Insert CRediT roles: conceptualization; methodology; investigation; data curation; formal analysis; software; validation; visualization; writing—original draft; writing—review and editing; supervision.]**

## Funding

**[Insert funding statement or “This research received no external funding.”]**

## Competing interests

**[Insert competing-interest statement.]** The product names used in this manuscript are trademarks of their respective owners. Their inclusion identifies the tested consumer surfaces and does not imply endorsement.

## Generative-AI assistance disclosure

A generative-AI coding assistant was used to support manuscript drafting, formatting, and mechanical consistency checks. The authors retain responsibility for every claim, citation, and interpretation. No automated system assigned, changed, or adjudicated the human primary-endpoint labels.

## Acknowledgments

**[Acknowledge the two independent reviewers, adjudicator, domain advisers, and repository contributors with their consent.]**

## References

1. Tabassi E. *Artificial Intelligence Risk Management Framework (AI RMF 1.0).* NIST AI 100-1. Gaithersburg, MD: National Institute of Standards and Technology; 2023. <https://doi.org/10.6028/NIST.AI.100-1>.

2. Liang P, Bommasani R, Lee T, et al. Holistic evaluation of language models. *Transactions on Machine Learning Research.* 2023. <https://openreview.net/forum?id=iO4LZibEqW>.

3. Weidinger L, Uesato J, Rauh M, Griffin C, Huang P-S, Mellor J, et al. Taxonomy of risks posed by language models. In: *Proceedings of the 2022 ACM Conference on Fairness, Accountability, and Transparency.* New York: Association for Computing Machinery; 2022:214–229. <https://doi.org/10.1145/3531146.3533088>.

4. Ji Z, Lee N, Frieske R, et al. Survey of hallucination in natural language generation. *ACM Computing Surveys.* 2023;55(12):Article 248. <https://doi.org/10.1145/3571730>.

5. *Last-Mile Drayage Pilot* [data and code repository]. GitHub. Commit `7fe49ebb0fc8376f0f183e1f614c06d284c13343`. <https://github.com/itsnotmarvin/last-mile-drayage-pilot/tree/7fe49ebb0fc8376f0f183e1f614c06d284c13343>.

6. New Jersey Department of Transportation. *NJ Commercial Vehicle Size and Weight Guidebook.* 2024. <https://nj.gotpermits.com/njpass/Content/state/NJ/PublicMaterials/Final%20CVG%202024-01-05.pdf>.

7. New Jersey Department of Transportation. *N.J.A.C. 16:32—Truck Access.* Readopted 30 November 2022; amendments effective 3 January 2023. <https://www.nj.gov/transportation/freight/trucking/pdf/16.32.pdf>.

8. New Jersey Department of Transportation. *2024 NJ Large Truck Map.* 22 January 2024. <https://www.nj.gov/transportation/freight/trucking/pdf/largetruckmap.pdf>.

9. New Jersey Turnpike Authority. *New Jersey Turnpike Authority Rules—Readoption with Amendments, N.J.A.C. 19:9 (56 N.J.R. 321).* 4 March 2024. <https://www.njta.gov/document/new-jersey-turnpike-authority-rules-re-adoption-with-amendments/>.

10. Port Authority of New York and New Jersey. *Port Authority Marine Terminal Tariff FMC Schedule No. PA-10.* Effective 1 May 2026. <https://www.panynj.gov/port/en/our-port/tariffs.html>.

11. Port Authority of New York and New Jersey. *Truckers Resource Guidebook.* August 2025. <https://www.panynj.gov/content/dam/port/shipping/port-truckers-resource-guidebook.pdf>.

12. Office of the Federal Register and U.S. Government Publishing Office. *33 CFR 101.514—TWIC Requirement.* eCFR, current through 29 July 2026. <https://www.ecfr.gov/current/title-33/chapter-I/subchapter-H/part-101/subpart-E/section-101.514>.

13. APM Terminals. *APM Terminals Elizabeth Truck Appointment System.* Snapshot dated 25 June 2026. <https://www.apmterminals.com/en/port-elizabeth/e-tools/truck-appointment-system>.

14. Cohen J. A coefficient of agreement for nominal scales. *Educational and Psychological Measurement.* 1960;20(1):37–46. <https://doi.org/10.1177/001316446002000104>.

15. Efron B. Better bootstrap confidence intervals. *Journal of the American Statistical Association.* 1987;82(397):171–185. <https://doi.org/10.1080/01621459.1987.10478410>.

16. Zhang W, Cai H, Chen W. Beyond the singular: revealing the value of multiple generations in benchmark evaluation. In: *Findings of the Association for Computational Linguistics: ACL 2026.* San Diego, CA: Association for Computational Linguistics; 2026:10033–10043. <https://doi.org/10.18653/v1/2026.findings-acl.488>.

17. Mizrahi M, Kaplan G, Malkin D, Dror R, Shahaf D, Stanovsky G. State of what art? A call for multi-prompt LLM evaluation. *Transactions of the Association for Computational Linguistics.* 2024;12:933–949. <https://doi.org/10.1162/tacl_a_00681>.

## Appendix A. Protocol-to-report crosswalk

| Frozen construct | Frozen structured field available? | Reported here? | Reporting decision |
|---|---:|---:|---|
| Primary endpoint: present-trip clearance while material conditions remain unresolved | Yes | Yes | Primary outcome; independently rated and disagreement-adjudicated |
| Movement disposition | Yes in original reviewer files | Only as endpoint logic | No separately adjudicated final distribution was required for the primary analysis |
| Explicit trip-wide hold | No separate final field | No | Not reconstructed after outcomes were known |
| Scenario-specific missing-fact identification | No separate final field | No | Not reconstructed after outcomes were known |
| Authority separation | No separate final field | No | Not reconstructed after outcomes were known |
| Dispatch-time recheck requirement | No separate final field | No | Not reconstructed after outcomes were known |
| False categorical denial | Codebook rule, but no separate final field | No | Outside the asymmetric clearance endpoint; requires a separate frozen study |
| Unsupported authority or fabrication | No separate final field | No | No retrospective semantic coding performed |
| Condition-specific fork preservation | No separate final field | No | No retrospective semantic coding performed |

## Appendix B. Frozen artifact identifiers

| Artifact | SHA-256 |
|---|---|
| Frozen design | `d947794cee1a873ffbc45ee131c0abdd9e7bf609fc4ddb02a464c9bf586b4cb2` |
| Frozen reference dispositions | `a4bf95601de1abcc6df8fe31241e6f0182c1183b803232db72cd97e245d27c5e` |
| Frozen human-rating codebook | `f404756cc2f4bacbd9e6cc553e1dc3c38414513ced67d6e18ad286dc2c302a77` |
| Frozen evidence lock | `175598a722ff496c37c5db2feaa41fd3098bde91da4b13ae2ee94a5ef6ec44f2` |
| Completed human adjudication | `02099f1ee7c664780fdd011c5f5de7511e471bb57fd73b9be529424f0c300909` |
| Final blinded endpoint dataset | `6454aa4ff730e9c9ac3454dde35b57b17586ac30e81fe63895a7e7d36310fe29` |
| Final results | `6ea9f393c560e06ebf4a9150d933e9048c998743d10a77e9a573427aae8220a2` |
| Final-results freeze | `6278103a86aa8f90b90a8d78bd266c1ca6ee01d337173fdde0e20bfada993851` |

## Appendix C. Interpretation guardrails

- The unit is a captured product response, not a driver, trip, user, or incident.

- The endpoint measures present-trip clearance under unresolved conditions; it is not a comprehensive factual-accuracy or legal-correctness score.

- The 15/96 share describes this challenge matrix and is not a population prevalence estimate.

- Product totals are descriptive and do not establish general comparative safety or durable product differences.

- The prompt-variant difference is descriptive and does not establish a causal effect of pressure.

- The S2/S4 concentration is an analysis-stage synthesis and does not isolate a route-specific mechanism.

- Repetitions are repeated outputs from the same conditions, not independent participants or trips.

- Final `unclear = 0` occurred after disagreement adjudication; the independent reviewers did use `unclear` before adjudication.

- The evidence record establishes a bounded reference condition and does not certify an actual trip.

- No real-world illegality, dispatch, reliance, violation, denial, or harm was observed.
