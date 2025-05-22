from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import requests
import json
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = 'stock_monitoring_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/company_logos'

# 로고 이미지 관련 경로 설정
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 사용자 관심 종목 데이터 (실제로는 DB에 저장해야 함)
default_stocks = [
    {"code": "005930", "name": "삼성전자", "change": "+2.1%", "logo": "samsung.png"},
    {"code": "035420", "name": "네이버", "change": "-0.8%", "logo": "naver.png"},
    {"code": "035720", "name": "카카오", "change": "+1.5%", "logo": "kakao.png"},
    {"code": "005380", "name": "현대차", "change": "+0.7%", "logo": "hyundai.png"},
    {"code": "066570", "name": "LG전자", "change": "-1.2%", "logo": "lg.png"},
    {"code": "000660", "name": "SK하이닉스", "change": "+3.2%", "logo": "skhynix.png"},
    {"code": "068270", "name": "셀트리온", "change": "-0.5%", "logo": "celltrion.png"},
]

# 뉴스 데이터 (실제로는 API 또는 DB에서 가져와야 함)
news_data = [
    {
        "category": "경제 일반",
        "title": "미국 기준금리 동결, 국내 주식시장 영향은?",
        "summary": "미 연준이 기준금리를 동결했지만 하반기 금리 인하 가능성을 시사했습니다. 국내 증시는...",
        "date": "2025.04.08",
        "image": "news1.jpg"
    },
    {
        "category": "테크 산업",
        "title": "반도체 업계, 2분기 실적 전망 밝아",
        "summary": "AI 수요 증가로 메모리 반도체 가격이 상승세를 지속하면서 반도체 업계의 2분기 실적...",
        "date": "2025.04.08",
        "image": "news2.jpg"
    }
]

# 시장 브리핑 데이터
market_briefing = [
    "다우지수 +0.8%, S&P500 +1.2%, 나스닥 +1.5%로 상승 마감",
    "배럴당 유가 75.20달러로 1.2% 상승",
    "미국 국채 10년물 금리 소폭 하락",
    "글로벌 주요국 중앙은행 회의 일정 주목",
    "국내 수출 호조 지속, 7개월 연속 증가세"
]

# 로고 이미지 검색 및 저장 함수
def get_company_logo(company_code, company_name):
    """
    회사 로고를 찾거나 다운로드하는 함수
    실제 구현에서는 회사 코드/이름으로 로고를 찾아 다운로드하는 로직 필요
    """
    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{company_code}.png")
    
    # 이미 로고 파일이 있는지 확인
    if os.path.exists(logo_path):
        return f"{company_code}.png"
    
    # 로고 파일이 없으면 다운로드 시도
    try:
        # 여기에 실제 로고 다운로드 로직 구현
        # 예: API 호출, 웹 크롤링 등
        pass
        
        # 임시로 대체 이미지 생성 (실제 구현에서는 제거)
        placeholder_image = Image.new('RGB', (120, 80), color=(73, 109, 137))
        placeholder_image.save(logo_path)
        
        return f"{company_code}.png"
    except Exception as e:
        print(f"로고 다운로드 실패: {e}")
        return "default_logo.png"

# 차트 데이터 생성 함수
def generate_stock_chart(company_code, period='1m'):
    """
    주식 차트 데이터를 생성하는 함수
    실제 구현에서는 외부 API에서 실제 데이터를 가져와야 함
    """
    # 기간에 따른 데이터 포인트 수 설정
    if period == '1d':
        days = 1
        points = 390  # 1분 간격 (6.5시간 거래)
    elif period == '1w':
        days = 7
        points = 7
    elif period == '1m':
        days = 30
        points = 30
    elif period == '3m':
        days = 90
        points = 90
    elif period == '1y':
        days = 365
        points = 250  # 연간 거래일 수
    else:
        days = 30
        points = 30
    
    # 날짜 범위 생성
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 임의의 주가 데이터 생성 (실제로는 API에서 가져와야 함)
    base_price = random.randint(50000, 100000)  # 기본 주가
    volatility = random.uniform(0.01, 0.05)     # 변동성
    
    dates = pd.date_range(start=start_date, end=end_date, periods=points)
    prices = [base_price]
    
    # 랜덤 워크 모델로 주가 시뮬레이션
    for i in range(1, points):
        change = prices[-1] * volatility * random.normalvariate(0, 1)
        new_price = max(prices[-1] + change, 100)  # 최소 가격 100원
        prices.append(new_price)
    
    # 차트 생성
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, '-', color='#253f5b')
    plt.title(f'{company_code} 주가 차트 ({period})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # 그래프를 이미지로 변환
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    
    # 이미지를 base64로 인코딩
    chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    chart_data = f'data:image/png;base64,{chart_base64}'
    
    return chart_data

@app.route('/')
def index():
    # 로고 이미지 업데이트
    stocks = []
    for stock in default_stocks:
        # 로고 확인 및 업데이트
        logo = get_company_logo(stock["code"], stock["name"])
        stock_data = {
            "code": stock["code"],
            "name": stock["name"],
            "change": stock["change"],
            "logo": logo
        }
        stocks.append(stock_data)
    
    # 시장 현황 데이터 (실제로는 API에서 가져와야 함)
    market_data = {
        "kospi": "+1.2%",
        "kosdaq": "-0.3%",
        "dow": "+0.8%",
        "dollar": "1,320.50 ▼",
        "oil": "75.20 ▲",
        "gold": "2,340.10 ▲"
    }
    
    # 현재 날짜
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    return render_template('moniter.html', 
                          stocks=stocks, 
                          news=news_data, 
                          market_briefing=market_briefing,
                          market_data=market_data,
                          current_date=current_date)

@app.route('/add_stock', methods=['POST'])
def add_stock():
    """종목 추가 기능"""
    code = request.form.get('code')
    name = request.form.get('name')
    
    if not code or not name:
        flash('종목 코드와 이름을 모두 입력해주세요.')
        return redirect(url_for('index'))
    
    # 중복 체크 (실제로는 DB에서 확인)
    for stock in default_stocks:
        if stock['code'] == code:
            flash('이미 추가된 종목입니다.')
            return redirect(url_for('index'))
    
    # 로고 가져오기
    logo = get_company_logo(code, name)
    
    # 임의의 변동률 설정 (실제로는 API에서 가져와야 함)
    change_value = random.uniform(-3.0, 3.0)
    change = f"{'+' if change_value > 0 else ''}{change_value:.1f}%"
    
    # 새 종목 추가 (실제로는 DB에 저장)
    new_stock = {
        "code": code,
        "name": name,
        "change": change,
        "logo": logo
    }
    
    default_stocks.append(new_stock)
    flash('종목이 성공적으로 추가되었습니다.')
    return redirect(url_for('index'))

@app.route('/upload_logo', methods=['POST'])
def upload_logo():
    """회사 로고 업로드 기능"""
    if 'logo' not in request.files:
        flash('로고 파일이 없습니다.')
        return redirect(url_for('index'))
    
    file = request.files['logo']
    code = request.form.get('code')
    
    if file.filename == '':
        flash('선택된 파일이 없습니다.')
        return redirect(url_for('index'))
    
    if not code:
        flash('종목 코드가 필요합니다.')
        return redirect(url_for('index'))
    
    # 파일 확장자 검증
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
        filename = f"{code}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 이미지 크기 조정 및 저장
        try:
            img = Image.open(file)
            img = img.resize((120, 80), Image.LANCZOS)
            img.save(file_path)
            flash('로고가 성공적으로 업로드되었습니다.')
        except Exception as e:
            flash(f'로고 처리 중 오류 발생: {e}')
    else:
        flash('이미지 파일만 업로드 가능합니다. (PNG, JPG, JPEG, GIF)')
    
    return redirect(url_for('index'))

@app.route('/stock_chart/<code>')
def stock_chart(code):
    """종목 차트 조회 API"""
    period = request.args.get('period', '1m')
    chart_data = generate_stock_chart(code, period)
    return jsonify({"chart": chart_data})

@app.route('/remove_stock/<code>')
def remove_stock(code):
    """종목 제거 기능"""
    global default_stocks
    default_stocks = [stock for stock in default_stocks if stock['code'] != code]
    flash('종목이 제거되었습니다.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)