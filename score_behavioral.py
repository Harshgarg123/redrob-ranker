from datetime import datetime, date

TODAY = date(2026, 6, 9)


def score_behavioral(candidate):
    
    sig = candidate["redrob_signals"]

    # --- Recency: when did they last use the platform? ---
    last_active = sig.get("last_active_date")
    if last_active:
        try:
            days = (TODAY - datetime.strptime(
                last_active, "%Y-%m-%d").date()).days
            recency = max(0.0, 1.0 - days / 180.0)
        except ValueError:
            recency = 0.3
    else:
        recency = 0.2

    
    open_to_work = 1.0 if sig.get("open_to_work_flag") else 0.5

    
    response_rate = sig.get("recruiter_response_rate", 0.0)

    
    notice = sig.get("notice_period_days", 90)
    if notice <= 15:
        notice_score = 1.0
    elif notice <= 30:
        notice_score = 0.9
    elif notice <= 60:
        notice_score = 0.7
    elif notice <= 90:
        notice_score = 0.45
    elif notice <= 120:
        notice_score = 0.25
    else:
        notice_score = 0.1

   
    icr = sig.get("interview_completion_rate", 0.5)

    
    github = sig.get("github_activity_score", -1)
    github_score = max(0.0, min(github / 80.0, 1.0)) if github >= 0 else 0.3

    
    saved = min(sig.get("saved_by_recruiters_30d", 0) / 10.0, 1.0)

    
    verified_email = 1.0 if sig.get("verified_email") else 0.0
    verified_phone = 1.0 if sig.get("verified_phone") else 0.0
    linkedin       = 1.0 if sig.get("linkedin_connected") else 0.0
    verification   = (verified_email + verified_phone + linkedin) / 3.0

    
    work_mode = sig.get("preferred_work_mode", "flexible")
    if work_mode == "remote":
        mode_score = 0.75   # mild penalty, not 0.4
    elif work_mode in ("hybrid", "flexible", "onsite"):
        mode_score = 1.0
    else:
        mode_score = 0.85

   
    behavioral = (
        recency       * 0.22 +
        open_to_work  * 0.13 +
        response_rate * 0.22 +
        notice_score  * 0.13 +
        icr           * 0.10 +
        github_score  * 0.05 +
        saved         * 0.05 +
        verification  * 0.05 +
        mode_score    * 0.05
    )
    return behavioral