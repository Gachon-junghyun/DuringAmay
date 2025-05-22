import spacy

# spaCy 영어 모델 로드
nlp = spacy.load("en_core_web_sm")

# 브랜드 및 키워드 예시 세트
BRAND_KEYWORDS = {"Samsung", "Apple", "Sony", "Lamborghini", "Nike", "Adidas"}
PRODUCT_HINT_WORDS = {"Pro", "Max", "Ultra", "Plus", "Series", "Model", "Edition"}

def classify_description(text: str) -> dict:
    doc = nlp(text.strip())

    # 전처리된 토큰 및 품사 추출
    tokens = [token.text for token in doc]
    pos_tags = [token.pos_ for token in doc]
    num_tokens = len(tokens)

    # 모두 고유명사(NNP)이고 단어 수가 1~3이면 상품명일 가능성 높음
    if all(pos in ("PROPN", "NOUN") for pos in pos_tags) and 1 <= num_tokens <= 3:
        # 브랜드 이름과 겹치지 않으면서 제품 힌트 단어 포함 시
        if any(word in PRODUCT_HINT_WORDS for word in tokens):
            return {
                "classification": "상품명",
                "reason": "2~3개 단어의 명사/고유명사로 구성되며, 제품 힌트 단어가 포함되어 상품명일 가능성이 높습니다."
            }
        elif any(token in BRAND_KEYWORDS for token in tokens):
            return {
                "classification": "브랜드명",
                "reason": "단어가 알려진 브랜드 키워드와 일치합니다."
            }
        else:
            return {
                "classification": "상품명",
                "reason": "짧은 명사/고유명사 조합으로 구성되어 있으며 제품명일 가능성이 높습니다."
            }

    # 단어 수가 많고 동사/형용사/부사가 포함되어 설명형이면 기술 설명
    if any(pos in ("VERB", "ADJ", "ADV") for pos in pos_tags) or num_tokens >= 5:
        return {
            "classification": "기술 설명",
            "reason": "동사나 형용사 등이 포함된 복합 문장으로, 기능이나 동작 설명일 가능성이 높습니다."
        }

    # 하나의 단어이며 브랜드와 일치 시 브랜드명
    if num_tokens == 1 and tokens[0] in BRAND_KEYWORDS:
        return {
            "classification": "브랜드명",
            "reason": "입력된 단어가 알려진 브랜드 키워드와 일치합니다."
        }

    # 기본값
    return {
        "classification": "기술 설명",
        "reason": "설명형 구조로 판단되며 명확한 브랜드명이나 제품명으로 보기 어렵습니다."
    }

print(classify_description("Galaxy Buds Pro"))
print(classify_description("자동으로 작동하는 무선 커튼"))
print(classify_description("Lamborghini"))
