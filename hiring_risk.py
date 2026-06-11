from datetime import datetime, date

TODAY = date(2026, 6, 9)


def compute_hiring_risk(candidate):
    
    profile = candidate["profile"]
    sig     = candidate["redrob_signals"]
    career  = candidate["career_history"]

    risk  = 0.0
    flags = []

    
    recent_jobs = sorted(
        [j for j in career if j.get("start_date")],
        key=lambda x: x["start_date"],
        reverse=True
    )[:3]

    if len(recent_jobs) >= 3:
        tenures    = [j.get("duration_months", 0) for j in recent_jobs]
        avg_tenure = sum(tenures) / len(tenures)
        if avg_tenure < 10:
            risk += 0.30
            flags.append(
                f"job hopper — avg {avg_tenure:.0f}mo tenure in last 3 roles"
            )
        elif avg_tenure < 14:
            risk += 0.15
            flags.append(
                f"short tenures — avg {avg_tenure:.0f}mo in last 3 roles"
            )

    
    icr = sig.get("interview_completion_rate", 0)
    oar = sig.get("offer_acceptance_rate",     -1)
    if icr > 0.75 and oar != -1 and oar < 0.25:
        risk += 0.25
        flags.append(
            f"offer collector — completes {icr:.0%} of interviews "
            f"but accepts only {oar:.0%} of offers"
        )

    
    apps_30d = sig.get("applications_submitted_30d", 0)
    if apps_30d > 25:
        risk += 0.20
        flags.append(
            f"applied to {apps_30d} roles in 30 days — "
            f"not selective, likely using multiple offers"
        )
    elif apps_30d > 15:
        risk += 0.10
        flags.append(f"high application volume ({apps_30d} in 30 days)")

    
    avg_response = sig.get("avg_response_time_hours", 0)
    if avg_response > 72:
        risk += 0.15
        flags.append(
            f"slow responder — avg {avg_response:.0f}hrs response time"
        )
    elif avg_response > 48:
        risk += 0.08
        flags.append(f"moderate response time ({avg_response:.0f}hrs avg)")

    
    salary_range = sig.get("expected_salary_range_inr_lpa", "")
    if salary_range:
        try:
           
            parts = str(salary_range).replace(" ", "").split("-")
            if len(parts) == 2:
                expected_min = float(parts[0])
                if expected_min > 45:
                    risk += 0.15
                    flags.append(
                        f"salary expectation {salary_range}L "
                        f"may exceed budget"
                    )
        except (ValueError, AttributeError):
            pass

    
    if len(career) == 1:
        duration = career[0].get("duration_months", 0)
        if duration > 84:
            risk += 0.20
            flags.append(
                f"single employer for {duration//12}yrs — "
                f"may struggle adapting to startup pace"
            )

    
    title = profile.get("current_title", "").lower()
    yoe   = profile.get("years_of_experience", 0)
    if any(t in title for t in
           ["staff", "principal", "vp ", "head of", "director"]):
        if yoe > 12:
            risk += 0.15
            flags.append(
                "likely overqualified — may leave quickly "
                "if scope is limited"
            )

    risk = min(risk, 1.0)

    if risk >= 0.45:
        label = "HIGH"
    elif risk >= 0.20:
        label = "MEDIUM"
    else:
        label = "LOW"

    return risk, label, flags

# if __name__ == "__main__":
#     import json
#     from score_skills import score_skills
#     from score_career import score_career

#     candidates = []
#     with open("candidates.jsonl") as f:
#         for line in f:
#             line = line.strip()
#             if line:
#                 candidates.append(json.loads(line))

#     risky_but_skilled = []
#     for c in candidates:
#         skill_score, matched = score_skills(c)
#         career_score         = score_career(c)
#         if skill_score > 0.5 and career_score > 0.5:
#             risk, label, flags = compute_hiring_risk(c)
#             if label in ("HIGH", "MEDIUM"):
#                 risky_but_skilled.append((risk, label, flags, c))

#     risky_but_skilled.sort(key=lambda x: x[0], reverse=True)

#     print(f"Skilled candidates with hiring risks: {len(risky_but_skilled)}")
#     print("\nTop 10:")
#     for risk, label, flags, c in risky_but_skilled[:10]:
#         print(f"\n  {c['candidate_id']} — {c['profile']['current_title']}")
#         print(f"  Risk: {label} ({risk:.2f})")
#         for f in flags:
#             print(f"    - {f}")

#     # Check your current top 10 for risks
#     top_ids = [
#         "CAND_0018499", "CAND_0046525", "CAND_0052328",
#         "CAND_0064326", "CAND_0041669", "CAND_0027691",
#         "CAND_0068351", "CAND_0066999", "CAND_0061265",
#         "CAND_0006418",
#     ]
#     print("\n--- RISK CHECK ON YOUR CURRENT TOP 10 ---")
#     for c in candidates:
#         if c["candidate_id"] in top_ids:
#             risk, label, flags = compute_hiring_risk(c)
#             print(f"\n  {c['candidate_id']} — Risk: {label} ({risk:.2f})")
#             for f in flags:
#                 print(f"    - {f}")
# import json
# from collections import Counter

# candidates = []
# with open("candidates.jsonl") as f:
#     for line in f:
#         line = line.strip()
#         if line:
#             candidates.append(json.loads(line))

# oar_values = [c["redrob_signals"].get("offer_acceptance_rate") for c in candidates]
# print("Sample values:", oar_values[:20])
# print("Min:", min(v for v in oar_values if v is not None))
# print("Max:", max(v for v in oar_values if v is not None))