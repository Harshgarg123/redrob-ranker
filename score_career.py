IDEAL_TITLES = {
    "senior ai engineer", "lead ai engineer",
    "senior machine learning engineer", "staff machine learning engineer",
    "lead machine learning engineer", "principal machine learning engineer",
    "senior applied scientist", "applied scientist",
    "senior nlp engineer", "nlp engineer",
    "recommendation systems engineer",
    "search engineer", "ai research engineer",
}

STRONG_TITLES = {
    "ml engineer", "machine learning engineer", "applied ml engineer",
    "ai engineer", "ai specialist", "ai research engineer",
    "senior data scientist", "data scientist",
}

WEAK_TITLES = {
    "software engineer", "senior software engineer",
    "backend engineer", "senior backend engineer",
    "full stack developer", "data engineer",
    "senior data engineer", "analytics engineer",
}


SERVICES_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "mphasis", "tech mahindra",
    "hexaware", "ltimindtree", "persistent systems",
}


PRODUCT_INDUSTRIES = {
    "technology", "software", "internet", "saas", "fintech",
    "edtech", "healthtech", "e-commerce", "ecommerce",
    "marketplace", "ai", "social media", "gaming",
    "analytics", "startup", "enterprise software",
}


def score_career(candidate):
    
    profile = candidate["profile"]
    career  = candidate["career_history"]

    
    title = profile.get("current_title", "").lower()
    if title in IDEAL_TITLES:
        title_score = 1.0
    elif title in STRONG_TITLES:
        title_score = 0.75
    elif title in WEAK_TITLES:
        title_score = 0.45
    else:
        title_score = 0.10

    
    yoe = profile.get("years_of_experience", 0)
    if 5 <= yoe <= 9:
        yoe_score = 1.0
    elif 4 <= yoe < 5 or 9 < yoe <= 11:
        yoe_score = 0.75
    elif 3 <= yoe < 4 or 11 < yoe <= 13:
        yoe_score = 0.5
    else:
        yoe_score = 0.25

    
    product_months = 0
    all_services   = True

    for job in career:
        industry = job.get("industry", "").lower()
        company  = job.get("company",  "").lower()
        duration = job.get("duration_months", 0)

        is_services = any(kw in company for kw in SERVICES_COMPANIES)
        is_product  = any(kw in industry for kw in PRODUCT_INDUSTRIES)

        if is_product and not is_services:
            product_months += duration
            all_services = False

    if all_services:
        product_score = 0.2   # heavy penalty for pure services background
    else:
        product_score = min(product_months / 48.0, 1.0)  # 4+ years = 1.0

    # --- Combine ---
    career_score = (
        title_score   * 0.40 +
        yoe_score     * 0.30 +
        product_score * 0.30
    )

    return career_score
if __name__ == "__main__":
    import json

    candidates = []
    with open("candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    scores = []
    for c in candidates:
        score = score_career(c)
        scores.append((
            score,
            c["profile"]["current_title"],
            c["profile"]["years_of_experience"],
            c["profile"]["location"],
            c["candidate_id"]
        ))

    scores.sort(reverse=True)

    print("Top 10 by career score:")
    for score, title, yoe, loc, cid in scores[:10]:
        print(f"  {cid} | {title} | {yoe:.1f}yrs | {loc} | score={score:.3f}")

    print(f"\nCandidates with career score > 0.7: {sum(1 for s,*_ in scores if s > 0.7)}")
    print(f"Candidates with career score > 0.5: {sum(1 for s,*_ in scores if s > 0.5)}")