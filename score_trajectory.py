from datetime import datetime, date

TODAY = date(2026, 6, 9)


ROLE_RELEVANCE = {
    
    "senior ai engineer":               10,
    "lead ai engineer":                 10,
    "staff machine learning engineer":  10,
    "senior machine learning engineer":  9,
    "principal machine learning engineer": 10,
    "ml engineer":                       8,
    "machine learning engineer":         8,
    "applied ml engineer":               8,
    "ai engineer":                       8,
    "ai research engineer":              9,
    "senior nlp engineer":               9,
    "nlp engineer":                      8,
    "recommendation systems engineer":   9,
    "search engineer":                   8,
    "senior applied scientist":          9,
    "applied scientist":                 7,
    "senior data scientist":             7,
    "data scientist":                    6,
    
    "senior software engineer":          4,
    "software engineer":                 3,
    "backend engineer":                  3,
    "senior backend engineer":           4,
    "data engineer":                     3,
    "analytics engineer":                3,
    "full stack developer":              2,
    "cloud engineer":                    2,
    "devops engineer":                   1,
    
    "hr manager":                        0,
    "accountant":                        0,
    "project manager":                   1,
    "business analyst":                  1,
    "marketing manager":                 0,
}


def score_trajectory(candidate):
    
    career = candidate.get("career_history", [])

    if not career:
        return 0.3

    
    timeline = []
    for job in career:
        title = job.get("title", "").lower()
        sd    = job.get("start_date")
        if not sd:
            continue
        try:
            start = datetime.strptime(sd, "%Y-%m-%d")
        except ValueError:
            continue
        relevance = ROLE_RELEVANCE.get(title, 2)
        timeline.append((start, relevance))

    if len(timeline) < 2:
        if timeline:
            return min(timeline[0][1] / 10.0, 1.0)
        return 0.3

    
    timeline.sort(key=lambda x: x[0])

    
    mid         = len(timeline) // 2
    first_half  = timeline[:mid]
    second_half = timeline[mid:]

    avg_first  = sum(r for _, r in first_half)  / len(first_half)
    avg_second = sum(r for _, r in second_half) / len(second_half)

    
    if avg_second > avg_first:
        trajectory_bonus = (avg_second - avg_first) / 10.0
        direction = 1.0 + trajectory_bonus
    else:
        trajectory_bonus = (avg_first - avg_second) / 10.0
        direction = max(0.5, 1.0 - trajectory_bonus)

   
    latest_relevance = timeline[-1][1] / 10.0

    # Base score
    score = (
        latest_relevance    * 0.5 +
        (avg_second / 10.0) * 0.3 +
        direction           * 0.2
    )

    
    recent_jobs = sorted(
        [j for j in career if j.get("start_date")],
        key=lambda x: x["start_date"],
        reverse=True
    )[:4]

    if len(recent_jobs) >= 3:
        tenures = [j.get("duration_months", 0) for j in recent_jobs]
        avg     = sum(tenures) / len(tenures)
        if avg < 14:
            score = score * 0.7  # 30% penalty for title-chasing pattern

    return min(score, 1.0)