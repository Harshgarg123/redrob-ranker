from datetime import datetime, date
import json
TODAY = date(2026, 6, 9)

def is_honeypot(candidate):
    
    profile  = candidate["profile"]
    career   = candidate["career_history"]
    skills   = candidate["skills"]

    
    start_dates = []
    for job in career:
        sd = job.get("start_date")
        if sd:
            try:
                start_dates.append(
                    datetime.strptime(sd, "%Y-%m-%d").date()
                )
            except ValueError:
                pass

    if start_dates:
        earliest       = min(start_dates)
        actual_years   = (TODAY - earliest).days / 365.25
        claimed_years  = profile.get("years_of_experience", 0)
        if claimed_years > actual_years + 2.5:
            return True, f"claimed {claimed_years}yrs but career spans only {actual_years:.1f}yrs"

    
    for job in career:
        sd = job.get("start_date")
        ed = job.get("end_date")
        if sd and ed:
            try:
                s = datetime.strptime(sd, "%Y-%m-%d").date()
                e = datetime.strptime(ed, "%Y-%m-%d").date()
                if e < s:
                    return True, f"job end {e} is before start {s}"
            except ValueError:
                pass

    
    zero_expert = [
        s for s in skills
        if s.get("proficiency") in ("expert", "advanced")
        and s.get("duration_months", 1) == 0
        and s.get("endorsements", 0) > 10
    ]
    if len(zero_expert) >= 3:
        return True, f"{len(zero_expert)} expert skills with 0 months usage"

    return False, ""
if __name__ == "__main__":
    import json

    print("Testing honeypot detection...")
    candidates = []
    with open("candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    honeypots = []
    for c in candidates:
        flag, reason = is_honeypot(c)
        if flag:
            honeypots.append((c["candidate_id"], reason))

    print(f"Honeypots found: {len(honeypots)}")
    print("\nFirst 10:")
    for cid, reason in honeypots[:10]:
        print(f"  {cid}: {reason}")


        import json

with open("candidates.jsonl") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] == "CAND_0018499":
            print("Title:", c["profile"]["current_title"])
            print("YoE:", c["profile"]["years_of_experience"])
            print("Location:", c["profile"]["location"])
            print("Skills:", [s["name"] for s in c["skills"]])
            print("Companies:")
            for job in c["career_history"]:
                print(f"  {job['company']} | {job['title']} | {job.get('industry','')} | {job.get('duration_months',0)}mo")
            print("Signals:")
            sig = c["redrob_signals"]
            print(f"  open_to_work: {sig['open_to_work_flag']}")
            print(f"  notice: {sig['notice_period_days']} days")
            print(f"  response_rate: {sig['recruiter_response_rate']}")
            print(f"  last_active: {sig['last_active_date']}")
            break