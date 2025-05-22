import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from datetime import timedelta

# MSFT 데이터 다운로드
symbol = 'SPY'
data = yf.download(symbol, start="2024-01-01", end="2026-12-31")

# RSI 계산 함수
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# CCI 계산 함수
def calculate_cci(data, window=20):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    moving_avg = typical_price.rolling(window=window).mean()
    mean_deviation = abs(typical_price - moving_avg).rolling(window=window).mean()
    cci = (typical_price - moving_avg) / (0.015 * mean_deviation)
    return cci

# 기술적 지표 계산
data['RSI_14'] = calculate_rsi(data['Close'], window=14)
data['CCI_20'] = calculate_cci(data, window=20)

# 로컬 극댓값/극솟값 찾기
order = 8
max_idx = argrelextrema(data['Close'].values, np.greater_equal, order=order)[0]
min_idx = argrelextrema(data['Close'].values, np.less_equal, order=order)[0]

# 극댓값과 극솟값 데이터를 리스트로 수집
max_dates = []
max_prices = []
max_rsi = []
max_cci = []

min_dates = []
min_prices = []
min_rsi = []
min_cci = []

for idx in max_idx:
    max_dates.append(data.index[idx])
    max_prices.append(data['Close'].iloc[idx])
    max_rsi.append(data['RSI_14'].iloc[idx])
    max_cci.append(data['CCI_20'].iloc[idx])

for idx in min_idx:
    min_dates.append(data.index[idx])
    min_prices.append(data['Close'].iloc[idx])
    min_rsi.append(data['RSI_14'].iloc[idx])
    min_cci.append(data['CCI_20'].iloc[idx])

# 극댓값 데이터프레임 생성
max_df = pd.DataFrame({
    'Date': max_dates,
    'Price': max_prices,
    'RSI': max_rsi,
    'CCI': max_cci,
    'Type': 'Max'
})

# 극솟값 데이터프레임 생성
min_df = pd.DataFrame({
    'Date': min_dates,
    'Price': min_prices,
    'RSI': min_rsi,
    'CCI': min_cci,
    'Type': 'Min'
})

# 두 데이터프레임 합치기
extrema_df = pd.concat([max_df, min_df])
extrema_df = extrema_df.sort_values('Date').reset_index(drop=True)

# 이전 극값 대비 일수 계산
extrema_df['Days_Since_Last'] = extrema_df['Date'].diff().dt.days

# 이전 극값 대비 가격, RSI, CCI 변동 계산
extrema_df['Price_Change_Pct'] = extrema_df['Price'].pct_change() * 100
extrema_df['RSI_Change'] = extrema_df['RSI'].diff()
extrema_df['CCI_Change'] = extrema_df['CCI'].diff()

# 이전 극값의 RSI, CCI 값 추가
extrema_df['Previous_RSI'] = extrema_df['RSI'].shift(1)
extrema_df['Previous_CCI'] = extrema_df['CCI'].shift(1)

# NaN 값 처리 (첫 행은 이전 값이 없으므로)
extrema_df['Days_Since_Last'] = extrema_df['Days_Since_Last'].fillna(0).astype(int)
extrema_df['Price_Change_Pct'] = extrema_df['Price_Change_Pct'].fillna(0)
extrema_df['RSI_Change'] = extrema_df['RSI_Change'].fillna(0)
extrema_df['CCI_Change'] = extrema_df['CCI_Change'].fillna(0)
extrema_df['Previous_RSI'] = extrema_df['Previous_RSI'].fillna(extrema_df['RSI'].iloc[0])
extrema_df['Previous_CCI'] = extrema_df['Previous_CCI'].fillna(extrema_df['CCI'].iloc[0])

# 결과 보기
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print("\n극값 데이터 (RSI, CCI 포함):")
print(extrema_df[['Date', 'Type', 'Price', 'RSI', 'Previous_RSI', 'RSI_Change', 
                  'CCI', 'Previous_CCI', 'CCI_Change', 
                  'Days_Since_Last', 'Price_Change_Pct']])

# 기존 시각화 코드를 수정
plt.figure(figsize=(15, 15))

# 서브플롯 생성 - 모두 동일한 x축 공유
fig, axs = plt.subplots(4, 1, figsize=(15, 15), sharex=True)

# 첫 번째 그래프: 가격 및 극값 포인트
axs[0].plot(data['Close'], label='Close Price', color='blue')
axs[0].scatter(extrema_df[extrema_df['Type'] == 'Max']['Date'], 
            extrema_df[extrema_df['Type'] == 'Max']['Price'], 
            color='red', label='Local Max', marker='^', s=100)
axs[0].scatter(extrema_df[extrema_df['Type'] == 'Min']['Date'], 
            extrema_df[extrema_df['Type'] == 'Min']['Price'], 
            color='green', label='Local Min', marker='v', s=100)
axs[0].set_title(f"{symbol} Close Price - Local Highs and Lows")
axs[0].legend()
axs[0].grid(True)

# 두 번째 그래프: RSI 시각화
axs[1].plot(data.index, data['RSI_14'], color='purple', label='RSI 14')
axs[1].axhline(y=70, color='r', linestyle='--', alpha=0.5)
axs[1].axhline(y=30, color='g', linestyle='--', alpha=0.5)
axs[1].scatter(extrema_df[extrema_df['Type'] == 'Max']['Date'], 
            extrema_df[extrema_df['Type'] == 'Max']['RSI'], 
            color='red', marker='^', s=100)
axs[1].scatter(extrema_df[extrema_df['Type'] == 'Min']['Date'], 
            extrema_df[extrema_df['Type'] == 'Min']['RSI'], 
            color='green', marker='v', s=100)
axs[1].set_title('RSI (14) at Extrema Points')
axs[1].set_ylim(0, 100)
axs[1].grid(True)

# 세 번째 그래프: CCI 시각화
axs[2].plot(data.index, data['CCI_20'], color='orange', label='CCI 20')
axs[2].axhline(y=100, color='r', linestyle='--', alpha=0.5)
axs[2].axhline(y=-100, color='g', linestyle='--', alpha=0.5)
axs[2].scatter(extrema_df[extrema_df['Type'] == 'Max']['Date'], 
            extrema_df[extrema_df['Type'] == 'Max']['CCI'], 
            color='red', marker='^', s=100)
axs[2].scatter(extrema_df[extrema_df['Type'] == 'Min']['Date'], 
            extrema_df[extrema_df['Type'] == 'Min']['CCI'], 
            color='green', marker='v', s=100)
axs[2].set_title('CCI (20) at Extrema Points')
axs[2].grid(True)

# 네 번째 그래프: 극값 간 일수 시각화
for i, row in extrema_df.iterrows():
    if i > 0:  # 첫 번째 행 제외
        if row['Type'] == 'Max':
            color = 'red'
            marker = '^'
        else:
            color = 'green'
            marker = 'v'
        axs[3].bar(row['Date'], row['Days_Since_Last'], color='blue', alpha=0.5, width=20)
        axs[3].annotate(f"{row['Days_Since_Last']}d\n{float(row['Price_Change_Pct']):.2f}%", 
                    (row['Date'], row['Days_Since_Last']+5), 
                    ha='center', fontsize=9)

axs[3].set_title('Days Since Last Extrema Point')

# x축 레이블이 겹치지 않도록 조정
fig.autofmt_xdate()

# 서브플롯 간 간격 조정
plt.tight_layout()
plt.show()

# RSI 영역 분포 분석
rsi_bins = {'0-30': 0, '30-50': 0, '50-70': 0, '70-100': 0}
for rsi in extrema_df[extrema_df['Type'] == 'Max']['RSI']:
    if rsi < 30:
        rsi_bins['0-30'] += 1
    elif rsi < 50:
        rsi_bins['30-50'] += 1
    elif rsi < 70:
        rsi_bins['50-70'] += 1
    else:
        rsi_bins['70-100'] += 1

for rsi in extrema_df[extrema_df['Type'] == 'Min']['RSI']:
    if rsi < 30:
        rsi_bins['0-30'] += 1
    elif rsi < 50:
        rsi_bins['30-50'] += 1
    elif rsi < 70:
        rsi_bins['50-70'] += 1
    else:
        rsi_bins['70-100'] += 1

# CCI 영역 분포 분석
cci_bins = {'<-200': 0, '-200 to -100': 0, '-100 to 0': 0, '0 to 100': 0, '100 to 200': 0, '>200': 0}
for cci in extrema_df[extrema_df['Type'] == 'Max']['CCI']:
    if cci < -200:
        cci_bins['<-200'] += 1
    elif cci < -100:
        cci_bins['-200 to -100'] += 1
    elif cci < 0:
        cci_bins['-100 to 0'] += 1
    elif cci < 100:
        cci_bins['0 to 100'] += 1
    elif cci < 200:
        cci_bins['100 to 200'] += 1
    else:
        cci_bins['>200'] += 1

for cci in extrema_df[extrema_df['Type'] == 'Min']['CCI']:
    if cci < -200:
        cci_bins['<-200'] += 1
    elif cci < -100:
        cci_bins['-200 to -100'] += 1
    elif cci < 0:
        cci_bins['-100 to 0'] += 1
    elif cci < 100:
        cci_bins['0 to 100'] += 1
    elif cci < 200:
        cci_bins['100 to 200'] += 1
    else:
        cci_bins['>200'] += 1

# 추가 통계
print("\n통계:")
print(f"평균 극값 간격: {extrema_df['Days_Since_Last'][1:].mean():.2f} 일")
print(f"최대 상승률: {extrema_df['Price_Change_Pct'].max():.2f}%")
print(f"최대 하락률: {extrema_df['Price_Change_Pct'].min():.2f}%")

print("\nRSI 분포:")
for bin_name, count in rsi_bins.items():
    print(f"RSI {bin_name}: {count}개 극값 포인트")

print("\nCCI 분포:")
for bin_name, count in cci_bins.items():
    print(f"CCI {bin_name}: {count}개 극값 포인트")

# RSI 상태 변화 분석
rsi_transitions = {'Oversold to Normal': 0, 'Normal to Overbought': 0, 
                  'Overbought to Normal': 0, 'Normal to Oversold': 0,
                  'Within Normal': 0, 'Within Overbought': 0, 'Within Oversold': 0}

for i in range(1, len(extrema_df)):
    prev_rsi = extrema_df['Previous_RSI'].iloc[i]
    curr_rsi = extrema_df['RSI'].iloc[i]
    
    # 이전 RSI 상태
    if prev_rsi < 30:
        prev_state = 'Oversold'
    elif prev_rsi > 70:
        prev_state = 'Overbought'
    else:
        prev_state = 'Normal'
    
    # 현재 RSI 상태
    if curr_rsi < 30:
        curr_state = 'Oversold'
    elif curr_rsi > 70:
        curr_state = 'Overbought'
    else:
        curr_state = 'Normal'
    
    # 전이 상태 계산
    if prev_state == curr_state:
        transition = f'Within {curr_state}'
    else:
        transition = f'{prev_state} to {curr_state}'
    
    # 추적되는 전이 상태만 카운트
    if transition in rsi_transitions:
        rsi_transitions[transition] += 1

print("\nRSI 상태 변화:")
for transition, count in rsi_transitions.items():
    print(f"{transition}: {count}회")

# CCI 상태 변화 분석
cci_transitions = {'Oversold to Normal': 0, 'Normal to Overbought': 0, 
                  'Overbought to Normal': 0, 'Normal to Oversold': 0,
                  'Within Normal': 0, 'Within Overbought': 0, 'Within Oversold': 0}

for i in range(1, len(extrema_df)):
    prev_cci = extrema_df['Previous_CCI'].iloc[i]
    curr_cci = extrema_df['CCI'].iloc[i]
    
    # 이전 CCI 상태
    if prev_cci < -100:
        prev_state = 'Oversold'
    elif prev_cci > 100:
        prev_state = 'Overbought'
    else:
        prev_state = 'Normal'
    
    # 현재 CCI 상태
    if curr_cci < -100:
        curr_state = 'Oversold'
    elif curr_cci > 100:
        curr_state = 'Overbought'
    else:
        curr_state = 'Normal'
    
    # 전이 상태 계산
    if prev_state == curr_state:
        transition = f'Within {curr_state}'
    else:
        transition = f'{prev_state} to {curr_state}'
    
    # 추적되는 전이 상태만 카운트
    if transition in cci_transitions:
        cci_transitions[transition] += 1

print("\nCCI 상태 변화:")
for transition, count in cci_transitions.items():
    print(f"{transition}: {count}회")