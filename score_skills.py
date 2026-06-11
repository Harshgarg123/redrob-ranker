# Skills that the JD explicitly requires
MUST_HAVE = {
    "embeddings", "sentence-transformers", "sentence transformers",
    "openai embeddings", "bge", "e5", "bi-encoder", "cross-encoder",
    "vector search", "vector database", "faiss", "pinecone", "weaviate",
    "qdrant", "milvus", "opensearch", "elasticsearch",
    "hybrid search", "dense retrieval", "semantic search",
    "rag", "retrieval augmented generation", "llamaindex", "langchain",
    "llm", "large language models", "prompt engineering",
    "information retrieval", "ranking", "re-ranking", "reranking",
    "learning to rank", "ndcg", "mrr", "a/b testing",
    "nlp", "transformers", "bert",
    "fine-tuning", "fine-tuning llms", "lora", "qlora", "peft",
    "recommendation system", "recommender systems",
    "search engineering",
}

# Good supporting skills — worth partial credit
NICE_TO_HAVE = {
    "pytorch", "tensorflow", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "spark", "kafka", "airflow",
    "docker", "kubernetes", "aws", "gcp", "azure",
    "python", "fastapi", "mlflow",
}


def score_skills(candidate):
   
    skills = candidate["skills"]
    total_weighted = 0.0
    matched = []

    for skill in skills:
        name         = skill["name"].lower()
        endorsements = skill.get("endorsements", 0)
        duration     = skill.get("duration_months", 0)
        proficiency  = skill.get("proficiency", "beginner")

       
        endorse_trust = min(endorsements / 20.0, 1.0)
        duration_trust = min(duration / 24.0, 1.0)
        trust = 0.3 + 0.35 * endorse_trust + 0.35 * duration_trust

        
        prof_mult = {
            "expert":       1.0,
            "advanced":     0.9,
            "intermediate": 0.7,
            "beginner":     0.4,
        }.get(proficiency, 0.5)

        if name in MUST_HAVE:
            matched.append(skill["name"])
            total_weighted += trust * prof_mult
        elif name in NICE_TO_HAVE:
            total_weighted += trust * prof_mult * 0.3

    
    normalized = min(total_weighted / 4.5, 1.0)

    return normalized, matched
if __name__ == "__main__":
    import json
    from collections import Counter

    candidates = []
    with open("candidates.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    # Score everyone
    scores = []
    for c in candidates:
        score, matched = score_skills(c)
        scores.append((score, matched, c["profile"]["current_title"], c["candidate_id"]))

    scores.sort(reverse=True)

    print("Top 10 by skill score:")
    for score, matched, title, cid in scores[:10]:
        print(f"  {cid} | {title} | score={score:.3f} | {matched[:4]}")

    print(f"\nCandidates with score > 0.5: {sum(1 for s,_,_,_ in scores if s > 0.5)}")
    print(f"Candidates with score > 0.3: {sum(1 for s,_,_,_ in scores if s > 0.3)}")
    print(f"Candidates with score = 0.0: {sum(1 for s,_,_,_ in scores if s == 0.0)}")