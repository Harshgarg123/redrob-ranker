import json
import csv
import argparse
from pathlib import Path
from datetime import date

from confidence      import compute_confidence
from skill_gap       import get_skill_gap, gap_summary
from hiring_risk     import compute_hiring_risk
from score_trajectory import score_trajectory
from honeypot        import is_honeypot
from score_skills    import score_skills
from score_career    import score_career
from score_behavioral import score_behavioral

TODAY = date(2026, 6, 9)

WEIGHTS = {
    "skills":      0.32,
    "career":      0.26,
    "behavioral":  0.18,
    "trajectory":  0.12,
    "location":    0.08,
    "education":   0.04,
}

LOCATION_SCORES = {
    "Noida, Uttar Pradesh":    1.0,
    "Pune, Maharashtra":       1.0,
    "Gurgaon, Haryana":        0.85,
    "Delhi, Delhi":            0.85,
    "Bangalore, Karnataka":    0.75,
    "Hyderabad, Telangana":    0.75,
    "Mumbai, Maharashtra":     0.75,
    "Chennai, Tamil Nadu":     0.60,
    "Ahmedabad, Gujarat":      0.45,
    "Jaipur, Rajasthan":       0.35,
    "Chandigarh, Chandigarh":  0.35,
    "Kolkata, West Bengal":    0.35,
    "Indore, Madhya Pradesh":  0.30,
    "Kochi, Kerala":           0.25,
    "Vizag, Andhra Pradesh":   0.25,
    "Coimbatore, Tamil Nadu":  0.20,
}


def score_location(candidate):
    sig      = candidate["redrob_signals"]
    location = candidate["profile"].get("location", "")
    willing  = sig.get("willing_to_relocate", False)
    base     = LOCATION_SCORES.get(location)
    if base is not None:
        return base
    if willing:
        return 0.40
    return 0.15


def score_education(candidate):
    edu = candidate.get("education", [])
    if not edu:
        return 0.3
    best = 0.0
    for e in edu:
        field  = e.get("field_of_study", "").lower()
        tier   = e.get("tier", "tier_3")
        degree = e.get("degree", "").lower()
        if any(kw in field for kw in
               ["computer", "software", "machine learning",
                "data", "electrical", "math", "statistics"]):
            field_score = 1.0
        elif any(kw in field for kw in ["physics", "engineering"]):
            field_score = 0.7
        else:
            field_score = 0.3
        tier_score   = {"tier_1": 1.0, "tier_2": 0.75,
                        "tier_3": 0.5}.get(tier, 0.4)
        degree_score = 1.0 if any(
            d in degree for d in ["m.tech", "ms", "m.s.", "phd"]
        ) else 0.7
        score = field_score * 0.5 + tier_score * 0.3 + degree_score * 0.2
        best  = max(best, score)
    return best


def build_reasoning(candidate, skill_matches):
    """
    Specific, honest, actionable reasoning per candidate.
    Includes: career path, strengths, availability,
    skill gaps, salary flag, and real concerns.
    """
    profile = candidate["profile"]
    sig     = candidate["redrob_signals"]
    career  = candidate["career_history"]

    title  = profile.get("current_title", "")
    yoe    = profile.get("years_of_experience", 0)
    loc    = profile.get("location", "")
    notice = sig.get("notice_period_days", 90)
    rr     = sig.get("recruiter_response_rate", 0)
    otw    = sig.get("open_to_work_flag", False)

    # Career path — most recent 3 companies oldest first
    companies = []
    for job in sorted(career, key=lambda x: x.get("start_date", ""),
                      reverse=True)[:3]:
        co = job.get("company", "")
        if co:
            companies.append(co)
    company_str = " > ".join(reversed(companies)) if companies else ""

    # Skills
    skills_str = ", ".join(skill_matches[:3]) if skill_matches else "limited AI skills"

    # Skill gap
    gaps    = get_skill_gap(candidate)
    gap_str = gap_summary(gaps)

    # Sentence 1: who they are
    if company_str:
        sentence1 = f"{title} ({company_str}), {yoe:.1f}yrs; strong in {skills_str}."
    else:
        sentence1 = f"{title}, {yoe:.1f}yrs; strong in {skills_str}."

    # Sentence 2: availability
    if otw and notice <= 30:
        avail = f"Actively looking, {notice}d notice, {loc}."
    elif otw:
        avail = f"Open to work, {notice}d notice, {loc}."
    else:
        avail = f"Not actively looking, {notice}d notice, {loc}."

    # Concerns
    concerns = []
    if rr < 0.25:
        concerns.append(f"low response rate ({rr:.0%})")
    if notice > 90:
        concerns.append(f"{notice}d notice is a risk")
    if loc not in {
        "Noida, Uttar Pradesh", "Pune, Maharashtra",
        "Gurgaon, Haryana", "Delhi, Delhi",
        "Bangalore, Karnataka", "Hyderabad, Telangana",
    }:
        if sig.get("willing_to_relocate"):
            concerns.append(f"in {loc} but willing to relocate")
        else:
            concerns.append(f"location {loc} not preferred")

    # Salary flag
    salary = sig.get("expected_salary_range_inr_lpa", {})
    if isinstance(salary, dict):
        sal_min = salary.get("min", 0)
        if sal_min > 45:
            concerns.append(f"expects {sal_min}L+ which may stretch budget")

    concern_str = ("Concerns: " + "; ".join(concerns) + ".") if concerns else ""

    return f"{sentence1} {avail} {gap_str}. {concern_str}".strip()

def jd_match_boost(candidate):
    """
    Small boost for candidates who perfectly match the JD description
    even if behavioral signals are weak.

    The JD says: 5-9 years, applied ML at product companies,
    shipped real ranking/search/recommendation systems.
    These candidates should always appear in the top 100.
    """
    profile = candidate["profile"]
    career  = candidate["career_history"]

    yoe   = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "").lower()

    # Must be in YoE sweet spot
    if not (4.5 <= yoe <= 10):
        return 0.0

    # Must have AI/ML title
    if not any(kw in title for kw in
               ["ml", "ai", "machine learning", "nlp",
                "recommendation", "search", "applied scientist"]):
        return 0.0

    # Must have shipped real ML work in job descriptions
    shipped = False
    for job in career:
        desc = job.get("description", "").lower()
        if any(kw in desc for kw in
               ["deployed", "production", "real user",
                "at scale", "recommendation", "ranking",
                "retrieval", "search", "served"]):
            shipped = True
            break

    if not shipped:
        return 0.0

    
    return 0.06
def rank_candidates(candidates_path, output_path, top_n=100):
    print(f"Loading candidates from {candidates_path}...")
    candidates = []
    with open(candidates_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    print(f"Loaded {len(candidates):,} candidates")

    print("Scoring...")
    results        = []
    honeypot_count = 0

    for c in candidates:
        
        flag, reason = is_honeypot(c)
        if flag:
            honeypot_count += 1
            continue

       
        skill_score,     matched  = score_skills(c)
        career_score              = score_career(c)
        behavioral_score          = score_behavioral(c)
        location_score            = score_location(c)
        education_score           = score_education(c)
        trajectory_score          = score_trajectory(c)   # ← was missing from composite

        
        composite = (
            skill_score      * WEIGHTS["skills"]      +
            career_score     * WEIGHTS["career"]       +
            behavioral_score * WEIGHTS["behavioral"]   +
            trajectory_score * WEIGHTS["trajectory"]   +  # ← now included
            location_score   * WEIGHTS["location"]     +
            education_score  * WEIGHTS["education"]      
        )
        boost = jd_match_boost(c)
        if boost > 0:
            composite = composite + boost * (1.0 - composite)

        
        composite = min(composite, 1.0)

        
        _, conf_label, _ = compute_confidence(c, matched)
        _, risk_label, _ = compute_hiring_risk(c)

        
        reasoning = build_reasoning(c, matched)
        reasoning += f" [Confidence: {conf_label}]"
        if risk_label != "LOW":
            reasoning += f" [Risk: {risk_label}]"

        results.append({
            "candidate_id": c["candidate_id"],
            "score":        composite,
            "reasoning":    reasoning,
        })

    print(f"Honeypots removed: {honeypot_count}")
    print(f"Candidates scored: {len(results):,}")

    
    results.sort(key=lambda x: (-x["score"], x["candidate_id"]))

    
    top = results[:top_n]
    for i, r in enumerate(top):
        r["rank"] = i + 1

    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in top:
            writer.writerow([
                r["candidate_id"],
                r["rank"],
                f"{r['score']:.6f}",
                r["reasoning"],
            ])

    print(f"\nSubmission written to {output_path}")
    print(f"\nTop 10:")
    print(f"{'Rank':<5} {'ID':<15} {'Score':<10} Reasoning")
    print("-" * 80)
    for r in top[:10]:
        print(f"{r['rank']:<5} {r['candidate_id']:<15} {r['score']:<10.4f} "
              f"{r['reasoning'][:60]}...")

    
    print("\n--- FULL REASONING PREVIEW ---")
    for r in top[:3]:
        print(f"\nRank {r['rank']} | {r['candidate_id']}")
        print(f"  {r['reasoning']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="./candidates.jsonl")
    parser.add_argument("--out",        default="./submission.csv")
    args = parser.parse_args()
    rank_candidates(args.candidates, args.out)

