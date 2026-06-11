def compute_confidence(candidate, skill_matches):
    
    profile = candidate["profile"]
    sig     = candidate["redrob_signals"]
    career  = candidate["career_history"]
    skills  = candidate["skills"]

    signals = []
    score   = 0.0

    # --- Signal 1: Skill verification depth ---
    # Are matched skills actually endorsed or just listed?
    verified_matches = 0
    for s in skills:
        name = s["name"].lower()
        if name in {m.lower() for m in skill_matches}:
            if s.get("endorsements", 0) > 10 or s.get("duration_months", 0) > 12:
                verified_matches += 1

    if len(skill_matches) == 0:
        signals.append("no JD skill matches")
    elif verified_matches == len(skill_matches):
        score += 0.30
        signals.append(f"all {len(skill_matches)} matched skills verified")
    elif verified_matches > 0:
        score += 0.15
        signals.append(f"{verified_matches}/{len(skill_matches)} matched skills verified")
    else:
        signals.append("matched skills have no endorsements or usage")

   
    jobs_with_desc = sum(
        1 for j in career
        if len(j.get("description", "")) > 50
    )
    if len(career) == 0:
        signals.append("no career history")
    elif jobs_with_desc >= 2:
        score += 0.25
        signals.append(f"{jobs_with_desc} jobs with detailed descriptions")
    elif jobs_with_desc == 1:
        score += 0.12
        signals.append("only 1 job with description")
    else:
        signals.append("no job descriptions — hard to verify work")

    
    from datetime import datetime, date
    TODAY = date(2026, 6, 9)
    last_active = sig.get("last_active_date")
    if last_active:
        try:
            days = (TODAY - datetime.strptime(
                last_active, "%Y-%m-%d").date()).days
            if days <= 14:
                score += 0.20
                signals.append("active in last 14 days")
            elif days <= 60:
                score += 0.12
                signals.append(f"active {days} days ago")
            else:
                signals.append(f"inactive for {days} days — profile may be stale")
        except ValueError:
            signals.append("unknown last active date")

    
    assessments = sig.get("skill_assessment_scores", {})
    if assessments:
        avg = sum(assessments.values()) / len(assessments)
        if avg >= 75:
            score += 0.15
            signals.append(f"assessed on platform (avg {avg:.0f}/100)")
        else:
            score += 0.05
            signals.append(f"assessed but low scores (avg {avg:.0f}/100)")
    else:
        signals.append("no platform assessments taken")

    # --- Signal 5: Profile completeness ---
    completeness = sig.get("profile_completeness_score", 0)
    if completeness >= 80:
        score += 0.10
        signals.append(f"complete profile ({completeness}%)")
    elif completeness >= 60:
        score += 0.05
        signals.append(f"partial profile ({completeness}%)")
    else:
        signals.append(f"thin profile ({completeness}%)")

    # Clamp to 0-1
    score = min(score, 1.0)

    # Label
    if score >= 0.75:
        label = "HIGH"
    elif score >= 0.45:
        label = "MEDIUM"
    else:
        label = "LOW"

    return score, label, signals
if __name__ == "__main__":
    import json
    from score_skills import score_skills

    candidates = []
    with open("candidates.jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    check_ids = ["CAND_0018499", "CAND_0046525", "CAND_0052328"]

    for c in candidates:
        if c["candidate_id"] in check_ids:
            _, matched = score_skills(c)
            conf_score, label, signals = compute_confidence(c, matched)
            print(f"\n{c['candidate_id']} — {c['profile']['current_title']}")
            print(f"  Confidence: {label} ({conf_score:.2f})")
            print(f"  Signals:")
            for s in signals:
                print(f"    - {s}")