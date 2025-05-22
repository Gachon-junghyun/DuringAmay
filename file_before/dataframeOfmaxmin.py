import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from datetime import timedelta

# MSFT 데이터 다운로드
symbol = 'MSFT'
data = yf.download(symbol, start="2020-01-01", end="2024-12-31")

# 로컬 극댓값/극솟값 찾기
order = 8
max_idx = argrelextrema(data['Close'].values, np.greater_equal, order=order)[0]
min_idx = argrelextrema(data['Close'].values, np.less_equal, order=order)[0]

# 극댓값과 극솟값 데이터를 리스트로 수집
max_dates = []
max_prices = []
min_dates = []
min_prices = []

for idx in max_idx:
    max_dates.append(data.index[idx])
    max_prices.append(data['Close'].iloc[idx])

for idx in min_idx:
    min_dates.append(data.index[idx])
    min_prices.append(data['Close'].iloc[idx])

# 극댓값 데이터프레임 생성
max_df = pd.DataFrame({
    'Date': max_dates,
    'Price': max_prices,
    'Type': 'Max'
})

# 극솟값 데이터프레임 생성
min_df = pd.DataFrame({
    'Date': min_dates,
    'Price': min_prices,
    'Type': 'Min'
})

# 두 데이터프레임 합치기
extrema_df = pd.concat([max_df, min_df])
extrema_df = extrema_df.sort_values('Date').reset_index(drop=True)

# 이전 극값 대비 일수 계산
extrema_df['Days_Since_Last'] = extrema_df['Date'].diff().dt.days

# 이전 극값 대비 가격 변동 퍼센트 계산
extrema_df['Price_Change_Pct'] = extrema_df['Price'].pct_change() * 100

# NaN 값 처리 (첫 행은 이전 값이 없으므로)
extrema_df['Days_Since_Last'] = extrema_df['Days_Since_Last'].fillna(0).astype(int)
extrema_df['Price_Change_Pct'] = extrema_df['Price_Change_Pct'].fillna(0)

# 결과 보기
print(extrema_df)

# 시각화
plt.figure(figsize=(15, 10))
plt.subplot(211)
plt.plot(data['Close'], label='Close Price', color='blue')
plt.scatter(extrema_df[extrema_df['Type'] == 'Max']['Date'], 
            extrema_df[extrema_df['Type'] == 'Max']['Price'], 
            color='red', label='Local Max', marker='^', s=100)
plt.scatter(extrema_df[extrema_df['Type'] == 'Min']['Date'], 
            extrema_df[extrema_df['Type'] == 'Min']['Price'], 
            color='green', label='Local Min', marker='v', s=100)
plt.title(f"{symbol} Close Price - Local Highs and Lows")
plt.legend()
plt.grid(True)

plt.subplot(212)
for i, row in extrema_df.iterrows():
    if i > 0:  # 첫 번째 행 제외
        if row['Type'] == 'Max':
            color = 'red'
            marker = '^'
        else:
            color = 'green'
            marker = 'v'
        plt.bar(row['Date'], row['Days_Since_Last'], color='blue', alpha=0.5, width=20)
        plt.annotate(f"{row['Days_Since_Last']}d\n{float(row['Price_Change_Pct']):.2f}%", 
                    (row['Date'], row['Days_Since_Last']+5), 
                    ha='center', fontsize=9)

plt.title('Days Since Last Extrema Point')
plt.tight_layout()
plt.show()

# 추가 통계
print("\n통계:")
print(f"평균 극값 간격: {extrema_df['Days_Since_Last'][1:].mean():.2f} 일")
print(f"최대 상승률: {extrema_df['Price_Change_Pct'].max():.2f}%")
print(f"최대 하락률: {extrema_df['Price_Change_Pct'].min():.2f}%")