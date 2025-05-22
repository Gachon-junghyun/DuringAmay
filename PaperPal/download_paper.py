import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.messages import HumanMessage
import json
import re
from pathlib import Path

# ✅ 환경변수 불러오기 (.env에서 OPENAI_API_KEY 설정 필요)
load_dotenv()

# ✅ PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

# ✅ LangChain을 이용한 요약 함수
def summarize_text_with_langchain(text: str) -> dict:
    """
    논문 텍스트를 입력받아 핵심 정보와 근거를 포함한 구조화된 요약을 반환합니다.
    
    Args:
        text (str): 요약할 논문 텍스트
        
    Returns:
        dict: 논문의 제목, 기관, 연도, 핵심 발견, 적용 상황, 관련 카테고리 등을 포함한 딕셔너리
    """
    prompt_template = PromptTemplate.from_template("""
당신은 논문 정보를 구조화하여 정리하는 전문가입니다. 주어진 논문 텍스트를 분석하여 다음 정보를 추출해주세요.
결론과 그 근거를 명확하게 포함하는 것이 매우 중요합니다.

다음 정보를 JSON 형식으로 추출해주세요:

1. 논문 제목: 텍스트에서 추론 가능한 제목 또는 주제
2. 연구 기관: 논문을 발표한 대학교나 연구소 (텍스트에서 언급되지 않은 경우 가장 적합한 기관 추론)
3. 발표 연도: 논문이 발표된 연도 (언급되지 않은 경우 최근 연도로 추정)
4. 핵심 발견:
   - 주요 결론 (구체적인 수치나 통계 포함)
   - 이 결론을 뒷받침하는 근거
5. 적용 상황:
   - 이 논문 정보가 유용할 수 있는 일상 상황들
   - 각 상황에 적용할 수 있는 구체적인 조언
6. 카테고리: 이 논문이 속한 학문 분야들
7. 키워드: 이 논문과 관련된 주요 키워드

입력 텍스트:
{text}

출력 형식 (반드시 유효한 JSON 형식으로 반환):
{{
  "title": "논문 제목",
  "institution": "연구 기관",
  "year": "발표 연도",
  "key_findings": [
    {{
      "conclusion": "핵심 결론 1 (구체적인 수치 포함)",
      "evidence": "이 결론의 근거"
    }},
    {{
      "conclusion": "핵심 결론 2 (구체적인 수치 포함)",
      "evidence": "이 결론의 근거"
    }}
  ],
  "applicable_situations": [
    {{
      "situation": "적용 가능한 상황 1",
      "advice": "이 상황에 대한 구체적인 조언"
    }},
    {{
      "situation": "적용 가능한 상황 2",
      "advice": "이 상황에 대한 구체적인 조언"
    }}
  ],
  "categories": ["분야1", "분야2"],
  "keywords": ["키워드1", "키워드2", "키워드3"]
}}

참고 사항:
1. 핵심 결론은 반드시 구체적인 수치나 통계를 포함하도록 해주세요.
2. 근거는 결론을 뒷받침하는 방법론이나 데이터를 포함해야 합니다.
3. 적용 상황은 실생활에서 이 논문 정보가 유용하게 활용될 수 있는 구체적인 상황이어야 합니다.
4. 모든 정보는 텍스트에서 직접 추출하거나, 텍스트 내용을 기반으로 합리적으로 추론해야 합니다.
5. 반드시 위에 지정된 JSON 형식을 지켜주세요.
""")

    # 토큰 제한을 고려하여 텍스트 길이 제한 (필요시 조정)
    max_tokens = 5000
    truncated_text = text[:max_tokens] if len(text) > max_tokens else text
    
    prompt = prompt_template.format(text=truncated_text)
    chat = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)  # 더 큰 컨텍스트 모델 사용
    response = chat([HumanMessage(content=prompt)])
    
    # JSON 추출 (응답에서 JSON 부분만 추출)
    json_match = re.search(r'({[\s\S]*})', response.content)
    if json_match:
        try:
            result_json = json.loads(json_match.group(1))
            return result_json
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 형태로 반환
            return {"error": "JSON 파싱 실패", "raw_content": response.content}
    else:
        # 구조화된 형식이 아닌 경우 원본 텍스트 반환
        return {"error": "구조화된 응답 형식 추출 실패", "raw_content": response.content}

# ✅ JSON을 파일로 저장
def save_summary_to_file(summary_dict, output_path):
    # 출력 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # dict를 JSON 문자열로 변환하여 저장
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, ensure_ascii=False, indent=2)

# ✅ 사용자 친화형 출력 메시지 (dict를 입력으로 받도록 수정)
def friendly_message(summary_dict):
    try:
        # 제목과 제일 유용한 상황 추출
        title = summary_dict.get("title", "알 수 없는 제목")
        
        # 적용 가능한 상황이 있는 경우 첫 번째 상황 가져오기
        situation = "일반적인 상황"
        if summary_dict.get("applicable_situations") and len(summary_dict["applicable_situations"]) > 0:
            situation = summary_dict["applicable_situations"][0].get("situation", "일반적인 상황")
        
        # 핵심 결론 추출
        conclusion = "구체적인 결론을 찾을 수 없습니다"
        if summary_dict.get("key_findings") and len(summary_dict["key_findings"]) > 0:
            conclusion = summary_dict["key_findings"][0].get("conclusion", "구체적인 결론을 찾을 수 없습니다")
        
        # 조언 추출
        advice = "구체적인 조언을 찾을 수 없습니다"
        if summary_dict.get("applicable_situations") and len(summary_dict["applicable_situations"]) > 0:
            advice = summary_dict["applicable_situations"][0].get("advice", "구체적인 조언을 찾을 수 없습니다")
        
        return f"""
📚 오늘의 논문 요약 드릴게요!

이건요, "{title}"라는 논문이에요.
주로 {situation} 같은 상황에서 유용하게 쓰이죠.

결론은 간단해요! 👉 {conclusion}
그래서 우리가 취할 수 있는 해결방안은? ✅ {advice}

궁금한 점 있으면 또 물어보세요~ 😊
"""
    except Exception as e:
        return f"""
📚 논문 요약을 제공하지 못했습니다. (오류: {str(e)})

요약 처리 중 문제가 발생했습니다. 다시 시도해 주세요.
"""

# ✅ 전체 파이프라인 실행
def run_pipeline(pdf_path, output_path):
    try:
        # PDF → 텍스트 추출
        print(f"\n📄 {Path(pdf_path).name} 텍스트 추출 중...")
        text = extract_text_from_pdf(pdf_path)
        
        # LangChain으로 구조화된 dict 요약 생성
        print(f"💬 요약 생성 중...")
        summary_dict = summarize_text_with_langchain(text)
        
        # 오류 확인
        if "error" in summary_dict:
            print(f"\n❌ 요약 중 오류 발생: {summary_dict['error']}")
            return
        
        # JSON 파일로 저장
        print(f"💾 JSON 파일 저장 중...")
        save_summary_to_file(summary_dict, output_path)
        
        # 완료 메시지
        print(f"\n✅ {Path(pdf_path).name} 처리 완료!")
        
        # 사용자 친화적 메시지 출력 (dict를 입력으로 받음)
        print(friendly_message(summary_dict))
        
    except Exception as e:
        print(f"\n❌ {Path(pdf_path).name} 처리 중 오류 발생: {str(e)}")


# 🏁 실행 시작
if __name__ == "__main__":
    paper_folder = "C:/Users/onepe/PycharmProjects/DuringAmay/PaperPal/paper"  # PDF 파일이 있는 폴더
    summary_folder = "C:/Users/onepe/PycharmProjects/DuringAmay/PaperPal/summary_folder"  # 요약 파일을 저장할 폴더
    
    # paper 폴더가 없으면 생성
    os.makedirs(paper_folder, exist_ok=True)
    # summary 폴더가 없으면 생성
    os.makedirs(summary_folder, exist_ok=True)
    
    # PDF 파일 목록 가져오기
    pdf_files = [f for f in os.listdir(paper_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ {paper_folder} 폴더에 PDF 파일이 없습니다.")
    else:
        print(f"📚 총 {len(pdf_files)}개의 PDF 파일을 처리합니다...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(paper_folder, pdf_file)
            # 확장자를 .json으로 변경하여 저장
            output_path = os.path.join(summary_folder, f"{os.path.splitext(pdf_file)[0]}_summary.json")
            print(f"\n🔍 {pdf_file} 처리 시작...")
            run_pipeline(pdf_path, output_path)