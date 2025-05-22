import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import random

def check_symbol_validity(ticker_symbol):
    """
    주식 심볼이 유효한지 확인하는 함수
    
    Parameters:
    ticker_symbol (str): 주식 심볼
    
    Returns:
    bool: 심볼이 유효하면 True, 아니면 False
    """
    try:
        # 요청 간 지연 추가
        time.sleep(random.uniform(1, 3))
        
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if info and 'regularMarketPrice' in info:
            return True
        return False
    except Exception as e:
        print(f"심볼 확인 중 오류 발생: {str(e)}")
        return False

def get_stock_data(ticker_symbol, period='1mo', start=None, end=None):
    """
    주식 데이터를 가져오는 함수
    
    Parameters:
    ticker_symbol (str): 주식 심볼 (예: '005930.KS' for 삼성전자)
    period (str): 데이터 기간 ('1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max')
    start (str): 시작 날짜 (YYYY-MM-DD 형식)
    end (str): 종료 날짜 (YYYY-MM-DD 형식)
    """
    try:
        # 요청 간 지연 추가
        time.sleep(random.uniform(2, 4))
        
        # 주식 객체 생성
        stock = yf.Ticker(ticker_symbol)
        
        # 심볼 정보 확인
        info = stock.info
        if not info or 'regularMarketPrice' not in info:
            print(f"경고: {ticker_symbol} 심볼에 대한 정보를 찾을 수 없습니다.")
            print("다른 심볼을 시도해보세요.")
            return None
        
        # 주가 데이터 가져오기
        if start and end:
            df = stock.history(start=start, end=end)
        else:
            df = stock.history(period=period)
        
        if df.empty:
            print(f"경고: {ticker_symbol}에 대한 데이터가 없습니다.")
            return None
        
        # 기본 정보 출력
        print(f"\n=== {ticker_symbol} 주식 정보 ===")
        print(f"회사명: {info.get('longName', '정보 없음')}")
        print(f"현재가: {df['Close'][-1]:,.2f}")
        print(f"시가: {df['Open'][-1]:,.2f}")
        print(f"고가: {df['High'][-1]:,.2f}")
        print(f"저가: {df['Low'][-1]:,.2f}")
        print(f"거래량: {df['Volume'][-1]:,.0f}")
        
        # 일간 변동률 계산
        if len(df) > 1:
            daily_return = ((df['Close'][-1] - df['Close'][-2]) / df['Close'][-2]) * 100
            print(f"일간 변동률: {daily_return:.2f}%")
        
        # CSV 파일로 저장
        filename = f"{ticker_symbol}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename)
        print(f"\n데이터가 {filename}에 저장되었습니다.")
        
        return df
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        if "Too Many Requests" in str(e):
            print("요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
            print("팁: 여러 심볼을 한 번에 테스트하는 대신, 한 번에 하나의 심볼만 테스트해보세요.")
        return None

def test_different_periods(ticker_symbol):
    """
    다양한 기간으로 데이터를 가져오는 테스트 함수
    
    Parameters:
    ticker_symbol (str): 주식 심볼
    """
    periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y']
    
    for period in periods:
        print(f"\n{period} 기간으로 시도 중...")
        df = get_stock_data(ticker_symbol, period=period)
        if df is not None and not df.empty:
            print(f"{period} 기간 데이터 성공!")
            return df
        
        # 요청 간 지연 추가
        time.sleep(random.uniform(3, 5))
    
    # 날짜 범위로 시도
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"\n날짜 범위로 시도 중... ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})")
    df = get_stock_data(ticker_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    return df

def test_single_symbol(symbol):
    """
    단일 심볼에 대한 테스트 함수
    
    Parameters:
    symbol (str): 주식 심볼
    """
    print("\n" + "="*50)
    print(f"{symbol} 심볼 테스트 중...")
    
    # 심볼 유효성 확인
    if check_symbol_validity(symbol):
        print(f"{symbol} 심볼이 유효합니다.")
        
        # 다양한 기간으로 테스트
        df = test_different_periods(symbol)
        
        if df is not None and not df.empty:
            print("\n최근 5일 데이터:")
            print(df.tail())
    else:
        print(f"{symbol} 심볼이 유효하지 않습니다. 다른 심볼을 시도해보세요.")

if __name__ == "__main__":
    # 테스트할 주식 심볼들
    symbols = [
        '005930.KS',  # 삼성전자
        '035720.KS',  # 카카오
        '035420.KS',  # NAVER
        'AAPL',       # 애플
        'MSFT',       # 마이크로소프트
        'GOOGL',      # 구글
        'AMZN',       # 아마존
        'TSLA'        # 테슬라
    ]
    
    # 사용자에게 선택 옵션 제공
    print("=== Yahoo Finance 주식 데이터 테스트 ===")
    print("1. 모든 심볼 테스트 (요청 제한에 걸릴 수 있음)")
    print("2. 단일 심볼 테스트")
    choice = input("선택하세요 (1 또는 2): ")
    
    if choice == "1":
        # 각 주식에 대해 데이터 가져오기
        for symbol in symbols:
            test_single_symbol(symbol)
            # 심볼 간 지연 추가
            time.sleep(random.uniform(5, 10))
    elif choice == "2":
        # 심볼 선택
        print("\n사용 가능한 심볼:")
        for i, symbol in enumerate(symbols, 1):
            print(f"{i}. {symbol}")
        
        try:
            symbol_index = int(input("\n테스트할 심볼 번호를 입력하세요: ")) - 1
            if 0 <= symbol_index < len(symbols):
                test_single_symbol(symbols[symbol_index])
            else:
                print("유효하지 않은 번호입니다.")
        except ValueError:
            print("유효하지 않은 입력입니다.")
    else:
        print("유효하지 않은 선택입니다.") 