import requests

def search_semantic_scholar(query, limit=5):
    print(f"🔍 Semantic Scholar에서 '{query}' 검색 중... (최대 {limit}개)")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,url,abstract,authors"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("❌ 요청 실패:", e)
        return []

    data = res.json()
    return data.get("data", [])


def display_results(papers):
    if not papers:
        print("😢 결과가 없습니다.")
        return

    print(f"\n📦 총 {len(papers)}개의 논문 결과:")
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "제목 없음")
        url = paper.get("url", "URL 없음")
        abstract = paper.get("abstract")
        authors = [author['name'] for author in paper.get("authors", [])]

        abstract_text = abstract if isinstance(abstract, str) else "초록 없음"

        print(f"\n{i}. 📘 {title}")
        print(f"   👨‍🔬 저자: {', '.join(authors) if authors else '없음'}")
        print(f"   🔗 링크: {url}")
        print(f"   📝 초록:\n   {abstract_text[:400]}{'...' if len(abstract_text) > 400 else ''}")

# 🎯 실행용
if __name__ == "__main__":
    query = "brain-computer interface"
    papers = search_semantic_scholar(query, limit=5)
    display_results(papers)
