# Redrob Ranker — India RUNS Hackathon
**Track:** Data & AI Challenge — Intelligent Candidate Discovery  
**Team:** Harsh Garg  
**Event:** India RUNS × Hack2Skill × Redrob AI

---

## Reproduce in one command

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

That's it. No GPU. No API calls. No setup beyond Python 3.9+.  
Runtime: ~30 seconds on a standard laptop.

---

## The problem I was solving

Recruiters at fast-growing AI companies receive thousands of candidate profiles. The standard approach — keyword search for "ML Engineer" or "Python" — surfaces HR Managers with Python in their skills section and misses the actual AI engineers buried in the pool.

I looked at the data before writing a single line of scoring logic. What I found:

- **100,000 candidates total**
- **62% have completely irrelevant titles** — HR Managers, Accountants, Civil Engineers, Content Writers
- **Only 631 candidates have explicit AI/ML titles** — that's 0.6% of the pool
- **4,800+ candidates in the relevant pool are behaviorally unavailable** — inactive for months, response rate under 10%

The real pool worth ranking is about 6,900 candidates. My system filters the rest before scoring even begins.

---

## What I built

Nine files, each with one job:

| File | What it does |
|---|---|
| `explore.py` | Data analysis — run this first to understand the pool |
| `honeypot.py` | Detects 25 fake profiles with impossible career histories |
| `score_skills.py` | Scores skills by endorsement × duration trust, not raw count |
| `score_career.py` | Career quality — product company vs services, title, YoE |
| `score_behavioral.py` | 9 availability signals — is this person actually hirable now? |
| `score_trajectory.py` | Career direction — are they growing into AI or drifting away? |
| `skill_gap.py` | Which JD skill themes is each candidate missing? |
| `confidence.py` | How much should we trust this ranking for each candidate? |
| `hiring_risk.py` | Flags job hoppers, offer collectors, slow responders |
| `rank.py` | Combines everything, outputs the final ranked CSV |

---

## How the scoring works

```
Final Score = 0.32 × skills
            + 0.26 × career
            + 0.18 × behavioral
            + 0.12 × trajectory
            + 0.08 × location
            + 0.04 × education
            + JD match boost (if perfect fit)
```

### Skills (32%)
Most systems count skills. This one weights each skill by how much we can trust the claim.

A skill with 0 endorsements and 2 months of use gets trust score 0.38.  
A skill with 30 endorsements and 36 months gets trust score 1.0.  
This kills keyword stuffers automatically — no special logic needed.

### Career quality (26%)
Three things: title seniority, years of experience in the 5-9 year sweet spot, and product company vs IT services background. The JD explicitly says consulting backgrounds are a poor fit. Any career spent entirely at TCS, Infosys, Wipro, Accenture etc. gets a heavy penalty.

### Behavioral availability (18%)
Nine signals from the Redrob platform: recency of last login, open-to-work flag, recruiter response rate, notice period, interview completion rate, GitHub activity, saved by recruiters in last 30 days, identity verification, and work mode preference. A perfect-on-paper candidate who hasn't logged in for 6 months with a 5% response rate is not actually hirable — this scorer captures that.

### Career trajectory (12%)
This is the insight nobody else will have. I score each job in a candidate's history by how relevant it is to the AI Engineer role. Then I compare the first half of their career against the second half.

A candidate who went Junior Dev → ML Engineer → Senior ML Engineer is growing into the role.  
A candidate who went Senior ML Engineer → ML Engineer → Data Analyst is drifting away.

The JD explicitly says title-chasers who switch companies every 1.5 years are not a fit. This scorer catches that pattern and applies a 30% penalty.

### Skill gap analysis
Every candidate in the top 100 has a gap summary in their reasoning string. Instead of listing every missing skill, I group the JD into 8 themes: vector search, vector databases, embeddings, RAG/LLM pipelines, ranking/evaluation, fine-tuning, NLP, and recommendations. The reasoning tells the recruiter which themes are completely uncovered.

### Confidence scoring
For each candidate, I measure how reliable the scoring is — not just how good they are. A candidate with all skills verified by endorsements, detailed job descriptions, recent platform activity, and platform assessment scores gets HIGH confidence. A candidate with thin profile and no endorsements gets LOW confidence. This tells recruiters when to trust the ranking and when to verify manually.

### Hiring risk flags
Candidates who complete 80%+ of interviews but accept fewer than 25% of offers are flagged as offer collectors. Job hoppers with average tenure under 10 months in recent roles are flagged. Slow responders with average response time over 72 hours are flagged. These appear as [Risk: MEDIUM] or [Risk: HIGH] in the reasoning column.

---

## What the output looks like

Each row in submission.csv has four columns:

```
candidate_id, rank, score, reasoning
```

Sample reasoning for rank 1:

```
Senior Machine Learning Engineer (Flipkart > Google > Zomato), 7.2yrs; 
strong in Weaviate, Pinecone, Information Retrieval. Actively looking, 
15d notice, Noida, Uttar Pradesh. Gaps: NLP. [Confidence: HIGH]
```

That single line tells a recruiter: who they are, where they've worked, 
what they're strong in, whether they're available, where they're located, 
what's missing, and how much to trust this assessment.

---

## Honeypot detection

The dataset contains ~25 fake profiles with impossible histories. I check three things:

1. Claimed years of experience more than 2.5 years greater than actual career span
2. Job end date before start date
3. Three or more expert-endorsed skills with zero months of usage

All 25 are removed before scoring begins.

---

## Why not LLMs or embeddings?

The constraint is 5 minutes on CPU for 100,000 candidates. A sentence-transformer over 100,000 profiles takes 15-30 minutes on CPU. Beyond the time constraint, the signals that matter most — title, career context, behavioral availability, skill depth — are all structured fields. Scoring them directly is faster, fully explainable, and completely reproducible. A structured ranker over interpretable features also produces reasoning strings that a human recruiter can understand and trust.

---

## What I would improve with more time

- **Learning-to-rank model** trained on actual recruiter decisions. When a recruiter accepts or rejects a shortlisted candidate, that feedback trains the model to improve weights automatically. The current system has fixed weights — that's the biggest limitation.
- **Company tier scoring** — right now Zomato and an unknown 3-person startup both count as product companies. A tier system (FAANG, tier-1 Indian product cos, known startups, unknown) would improve top-10 quality.
- **Semantic search on job descriptions** using sentence-transformers offline to build embeddings, then similarity matching at ranking time within the 5-minute window.
- **A/B testing framework** to validate weight choices against recruiter feedback rather than intuition.

---

## Files

```
redrob-ranker/
  explore.py
  honeypot.py
  score_skills.py
  score_career.py
  score_behavioral.py
  score_trajectory.py
  skill_gap.py
  confidence.py
  hiring_risk.py
  rank.py
  submission.csv
  validate_submission.py
  requirements.txt
  README.md
```

`candidates.jsonl` is not included — download from the hackathon portal and place in the same folder.

---

## Requirements

```
Python 3.9+
No external packages — pure standard library only
json, csv, datetime, argparse, pathlib, collections
```

---

*Built for India RUNS Hackathon — Data & AI Challenge*  
*Hack2Skill × Redrob AI, June 2026*
