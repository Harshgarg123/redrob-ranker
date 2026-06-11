# The complete set of skills the JD requires
JD_REQUIRED_SKILLS = {
    # Retrieval & search
    "vector search", "semantic search", "hybrid search",
    "dense retrieval", "information retrieval",
    # Vector databases
    "faiss", "pinecone", "weaviate", "qdrant", "milvus",
    "opensearch", "elasticsearch",
    # Embeddings & models
    "embeddings", "sentence-transformers", "bge", "e5",
    "bi-encoder", "cross-encoder",
    # RAG & LLM pipelines
    "rag", "retrieval augmented generation",
    "llamaindex", "langchain", "llm",
    # Ranking & evaluation
    "ranking", "re-ranking", "reranking",
    "learning to rank", "ndcg", "mrr",
    # Fine-tuning
    "fine-tuning", "lora", "qlora", "peft",
    # Core NLP
    "nlp", "transformers",
    # Recommendation
    "recommendation system", "recommender systems",
}

# Group skills into themes for cleaner gap reporting
SKILL_THEMES = {
    "vector search":    {"vector search", "semantic search", "hybrid search",
                         "dense retrieval", "information retrieval"},
    "vector databases": {"faiss", "pinecone", "weaviate", "qdrant",
                         "milvus", "opensearch", "elasticsearch"},
    "embeddings":       {"embeddings", "sentence-transformers", "bge",
                         "e5", "bi-encoder", "cross-encoder"},
    "RAG/LLM":          {"rag", "retrieval augmented generation",
                         "llamaindex", "langchain", "llm"},
    "ranking/eval":     {"ranking", "re-ranking", "reranking",
                         "learning to rank", "ndcg", "mrr"},
    "fine-tuning":      {"fine-tuning", "lora", "qlora", "peft"},
    "NLP":              {"nlp", "transformers"},
    "recommendations":  {"recommendation system", "recommender systems",
                     "recommendation systems", "recommendations"},
}


def get_skill_gap(candidate):
    
    cand_skills = candidate.get("skills", [])

    
    trusted_skills = set()
    for s in cand_skills:
        name         = s["name"].lower()
        endorsements = s.get("endorsements", 0)
        duration     = s.get("duration_months", 0)

        
        if endorsements > 5 or duration > 6:
            trusted_skills.add(name)

    
    missing_themes = []
    for theme, theme_skills in SKILL_THEMES.items():
        covered = trusted_skills & theme_skills
        if not covered:
            missing_themes.append(theme)

    return missing_themes


def gap_summary(missing_themes):
    
    if not missing_themes:
        return "Full JD coverage"
    return "Gaps: " + ", ".join(missing_themes)
# if __name__ == "__main__":
    import json

    candidates = []
    with open("candidates.jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    # Check gap distribution across all candidates
    from collections import Counter
    gap_counts = Counter()

    for c in candidates:
        gaps = get_skill_gap(c)
        gap_counts[len(gaps)] += 1

    print("Skill gap distribution (number of missing themes):")
    for n_gaps in sorted(gap_counts.keys()):
        print(f"  {n_gaps} missing themes: {gap_counts[n_gaps]} candidates")

    # Show gaps for a few specific candidates
    check_ids = [
        "CAND_0018499",  # your rank 1
        "CAND_0046525",  # rank 2
        "CAND_0052328",  # rank 3
    ]

    print("\nGap analysis for your top 3:")
    for c in candidates:
        if c["candidate_id"] in check_ids:
            gaps  = get_skill_gap(c)
            print(f"\n  {c['candidate_id']} — {c['profile']['current_title']}")
            print(f"  Skills: {[s['name'] for s in c['skills']]}")
            print(f"  Gap summary: {gap_summary(gaps)}")