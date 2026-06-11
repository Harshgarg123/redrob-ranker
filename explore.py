import json

print("Loading candidates...")

candidates = []
with open("candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            candidates.append(json.loads(line))

print(f"Total candidates loaded: {len(candidates)}")
from collections import Counter


titles = Counter(c["profile"]["current_title"] for c in candidates)

print("\n--- TOP 20 JOB TITLES ---")
for title, count in titles.most_common(20):
    print(f"  {title}: {count}")


AI_RELEVANT_TITLES = {
    "ml engineer", "machine learning engineer", "senior machine learning engineer",
    "ai engineer", "senior ai engineer",
    "data scientist", "senior data scientist",
    "nlp engineer", "senior nlp engineer",
    "recommendation systems engineer",
    "search engineer",
    "ai research engineer",
    "applied ml engineer",
}

relevant = [
    c for c in candidates
    if c["profile"]["current_title"].lower() in AI_RELEVANT_TITLES
]

print(f"\n--- RELEVANT POOL ---")
print(f"  Total AI/ML titled candidates: {len(relevant)}")
print(f"  That is {len(relevant)/len(candidates)*100:.1f}% of the full pool")

relevant_titles = Counter(c["profile"]["current_title"] for c in relevant)
print("\n  Breakdown:")
for title, count in relevant_titles.most_common():
    print(f"    {title}: {count}")


WIDER_TITLES = {
    "software engineer", "senior software engineer",
    "backend engineer", "senior backend engineer",
    "full stack developer", "data engineer",
    "senior data engineer", "analytics engineer",
    "cloud engineer", "devops engineer",
}


AI_SKILLS = {
    "machine learning", "deep learning", "nlp", "embeddings",
    "vector search", "faiss", "pinecone", "rag",
    "transformers", "pytorch", "tensorflow", "llm",
    "recommendation system", "information retrieval",
    "fine-tuning", "semantic search",
}

wider_with_skills = []
for c in candidates:
    title = c["profile"]["current_title"].lower()
    if title in WIDER_TITLES:
        cand_skills = {s["name"].lower() for s in c["skills"]}
        if cand_skills & AI_SKILLS:  # has at least one AI skill
            wider_with_skills.append(c)

print(f"\n--- WIDER NET ---")
print(f"  Engineers with non-AI title but AI skills: {len(wider_with_skills)}")


real_pool = relevant + wider_with_skills
print(f"  Total real pool to rank: {len(real_pool)}")
print(f"  This is what our ranker actually scores")

from datetime import datetime, date

TODAY = date(2026, 6, 9)

print("\n--- SIGNALS INSIDE THE REAL POOL ---")


open_to_work = sum(
    1 for c in real_pool
    if c["redrob_signals"]["open_to_work_flag"]
)
print(f"  Open to work: {open_to_work} of {len(real_pool)}")


notice_periods = [
    c["redrob_signals"]["notice_period_days"]
    for c in real_pool
]
under_30 = sum(1 for n in notice_periods if n <= 30)
under_60 = sum(1 for n in notice_periods if n <= 60)
over_90  = sum(1 for n in notice_periods if n > 90)
print(f"  Notice period under 30 days: {under_30}")
print(f"  Notice period under 60 days: {under_60}")
print(f"  Notice period over 90 days:  {over_90}")


inactive = 0
for c in real_pool:
    last = c["redrob_signals"]["last_active_date"]
    if last:
        days = (TODAY - datetime.strptime(last, "%Y-%m-%d").date()).days
        if days > 180:
            inactive += 1
print(f"  Inactive over 180 days: {inactive} of {len(real_pool)}")

# Location
locations = Counter(c["profile"]["location"] for c in real_pool)
print(f"\n  Top 10 locations in real pool:")
for loc, count in locations.most_common(10):
    print(f"    {loc}: {count}")

# Response rate
low_response = sum(
    1 for c in real_pool
    if c["redrob_signals"]["recruiter_response_rate"] < 0.2
)
print(f"\n  Low recruiter response rate (under 20%): {low_response}")