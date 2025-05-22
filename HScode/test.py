import spacy

try:
    print("✅ spaCy version:", spacy.__version__)
    
    # 모델 로드 테스트
    nlp = spacy.load("en_core_web_sm")
    print("✅ Model 'en_core_web_sm' loaded successfully!")

    # 실제 처리 테스트
    doc = nlp("Apple is looking to acquire OpenAI in San Francisco for $10 billion.")
    for ent in doc.ents:
        print(f"📌 '{ent.text}' → {ent.label_}")

except Exception as e:
    print("❌ Something went wrong:", e)
