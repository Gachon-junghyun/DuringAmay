import requests
from io import BytesIO
from PIL import Image
import os

def get_company_logo(symbol):
    """주식 심볼을 이용하여 회사 로고 이미지를 가져옵니다."""
    base_url = "https://logo.clearbit.com/"
    # 더 많은 도메인 패턴 추가
    domains = [
        f"{symbol.lower()}.com",
        f"{symbol.lower()}.co.kr",
        f"{symbol.upper()}.com",
        f"{symbol.upper()}.co.kr",
        f"www.{symbol.lower()}.com",
        f"www.{symbol.upper()}.com",
        # 특정 회사들의 실제 도메인 추가
        "tesla.com" if symbol.upper() == "TSLA" else None,
        "apple.com" if symbol.upper() == "AAPL" else None,
        "microsoft.com" if symbol.upper() == "MSFT" else None,
        "google.com" if symbol.upper() == "GOOGL" else None,
        "amazon.com" if symbol.upper() == "AMZN" else None,
        "meta.com" if symbol.upper() == "META" else None,
        "netflix.com" if symbol.upper() == "NFLX" else None,
    ]
    # None 값 제거
    domains = [d for d in domains if d is not None]

    for domain in domains:
        url = base_url + domain
        try:
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()

            if response.headers['Content-Type'].startswith('image'):
                image = Image.open(BytesIO(response.content))
                return image
        except requests.exceptions.RequestException as e:
            print(f"Error fetching logo for {domain}: {e}")
        except Exception as e:
            print(f"Unexpected error for {domain}: {e}")

    return None

def save_logo(symbol, image):
    """로고 이미지를 파일로 저장합니다."""
    # 로고를 저장할 디렉토리 생성
    save_dir = "company_logos"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 파일 경로 설정
    file_path = os.path.join(save_dir, f"{symbol}_logo.png")
    
    # 이미지 저장
    image.save(file_path)
    return file_path

if __name__ == "__main__":
    stock_symbol = input("주식 심볼을 입력하세요: ")
    logo_image = get_company_logo(stock_symbol)

    if logo_image:
        saved_path = save_logo(stock_symbol, logo_image)
        print(f"로고가 성공적으로 저장되었습니다: {saved_path}")
    else:
        print(f"{stock_symbol}에 대한 로고를 찾을 수 없습니다.")



