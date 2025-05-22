import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tqdm import tqdm

# 섹터별 티커 정의
sectors = {
    "SPY": ["SPY"],
    "IT": ["AAPL", "MSFT", "ORCL", "CRM", "ADBE", "IBM", "CSCO", "ACN", "NOW", "INTU", "PLTR", "ANET", "PANW", "SAP", "UBER", "SNOW", "DELL", "HPQ", "HPE"],
    "Communication Services": ["GOOGL", "META", "NFLX", "TMUS", "DIS", "T", "VZ", "CMCSA", "CHTR", "EA", "TTWO", "LYV", "WBD", "FOXA", "NWS", "OMC", "IPG", "MTCH", "PARA", "SNAP"],
    "Consumer Discretionary": ["HD", "MCD", "NKE", "SBUX", "BKNG", "TGT", "LOW", "TJX", "CMG", "YUM", "MAR", "HLT", "EL", "ROST", "DG", "ULTA", "ORLY", "LVS", "EBAY"],
    "Consumer Staples": ["WMT", "COST", "PG", "KO", "PM", "PEP", "MO", "MDLZ", "CL", "KHC", "KMB", "GIS", "WBA", "KR", "UL", "BUD", "DEO", "BTI", "ADM", "TSN"],
    "Financials": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "MS", "AXP", "GS", "BX", "SPGI", "C", "PGR", "BLK", "SCHW", "CB", "MMC", "CME", "AIG", "PYPL"],
    "Healthcare": ["UNH", "CVS", "ELV", "CI", "HUM", "MDT", "ABT", "TMO", "DHR", "MCK", "ABC", "CAH", "ISRG", "SYK", "BDX", "HCA", "BSX", "EW", "GEHC", "LH"],
    "Pharmaceuticals & Biotechnology": ["JNJ", "LLY", "NVO", "ABBV", "MRK", "PFE", "AMGN", "BMY", "AZN", "NVS", "GSK", "SNY", "MRNA", "GILD", "REGN", "VRTX", "BIIB", "ZTS", "TAK"],
    "Industrials": ["GE", "CAT", "RTX", "UNP", "HON", "BA", "DE", "LMT", "UPS", "FDX", "MMM", "ITW", "GD", "NOC", "WM", "CSX", "NSC", "DAL", "LUV", "AAL"],
    "Energy": ["XOM", "CVX", "COP", "SHEL", "BP", "EOG", "OXY", "SLB", "MPC", "VLO", "PSX", "KMI", "WMB", "ET", "LNG", "DVN", "PXD", "HAL", "BKR", "ENB"],
    "Materials": ["LIN", "SHW", "APD", "ECL", "DOW", "DD", "NEM", "FCX", "SCCO", "NUE", "RIO", "BHP", "VALE", "CTVA", "PPG", "LYB", "ALB", "GOLD", "NTR", "STLD"],
    "Utilities": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "EXC", "XEL", "ED", "PCG", "PEG", "WEC", "ES", "EIX", "ETR", "DTE", "FE", "AES", "NGG"],
    "Real Estate": ["PLD", "AMT", "EQIX", "WELL", "SPG", "CCI", "PSA", "O", "DLR", "SBAC", "AVB", "EQR", "WY", "VICI", "EXR", "ARE", "BXP", "INVH", "KIM", "IRM"],
    "Semiconductors": ["NVDA", "TSM", "AVGO", "ASML", "INTC", "AMD", "QCOM", "TXN", "AMAT", "ADI", "MU", "LRCX", "KLAC", "MRVL", "CDNS", "SNPS", "ON", "MCHP", "STM", "GFS"],
    "Automotive & EV": ["TSLA", "TM", "BYDDF", "VWAGY", "MBGAF", "BMWYY", "GM", "F", "STLA", "HMC", "RACE", "RIVN", "LCID", "NIO", "LI", "XPEV", "TTM", "NSANY", "PSNY", "HYMTF"],
    "Retail & E-commerce": ["AMZN", "WMT", "BABA", "COST", "HD", "TGT", "JD", "LOW", "EBAY", "WBA", "CVS", "MELI", "TJX", "DG", "DLTR", "PDD", "SHOP", "KR", "SVNDY"]
}

# 결과를 저장할 데이터프레임 초기화
sector_pers = []

# 각 섹터별로 PER 수집
for sector_name, tickers in tqdm(sectors.items()):
    valid_pers = []
    
    for ticker in tickers:
        try:
            # ticker가 BRK.B 처럼 . 이 포함된 경우 yfinance에서는 - 으로 변경해야 함
            ticker = ticker.replace('.', '-')
            stock = yf.Ticker(ticker)
            
            # 기본 정보 가져오기
            info = stock.info
            
            # PER 추출 (forwardPE 또는 trailingPE 사용)
            per = info.get('forwardPE', info.get('trailingPE', np.nan))
            
            # 극단적인 값은 제외 (PER이 0 이하이거나 1000 초과인 경우)
            if per and per > 0 and per < 1000:
                valid_pers.append(per)
                # 개별 주식의 PER도 저장
                sector_pers.append({
                    'Sector': sector_name,
                    'Ticker': ticker,
                    'PER': per
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    # 섹터별 평균 PER 추가
    if valid_pers:
        sector_pers.append({
            'Sector': sector_name,
            'Ticker': 'SECTOR_AVG',
            'PER': np.mean(valid_pers)
        })

# 결과를 데이터프레임으로 변환
df_pers = pd.DataFrame(sector_pers)

# 섹터별 평균 PER만 선택
sector_avg_df = df_pers[df_pers['Ticker'] == 'SECTOR_AVG'].copy()
sector_avg_df = sector_avg_df.sort_values('PER')

# 1. 섹터별 평균 PER 막대 그래프
plt.figure(figsize=(14, 10))
sns.barplot(x='PER', y='Sector', data=sector_avg_df, palette='viridis')
plt.title('Average P/E Ratio by Sector', fontsize=16)
plt.xlabel('P/E Ratio', fontsize=14)
plt.ylabel('Sector', fontsize=14)
plt.tight_layout()
plt.savefig('sector_avg_per.png')
plt.show()

# 2. 섹터별 개별 주식의 PER 분포 boxplot
plt.figure(figsize=(16, 12))
individual_stocks_df = df_pers[df_pers['Ticker'] != 'SECTOR_AVG'].copy()
sns.boxplot(x='Sector', y='PER', data=individual_stocks_df, palette='Set3')
plt.xticks(rotation=90)
plt.title('Distribution of P/E Ratios by Sector', fontsize=16)
plt.xlabel('Sector', fontsize=14)
plt.ylabel('P/E Ratio', fontsize=14)
plt.ylim(0, 100)  # 보기 좋게 y축 조정
plt.tight_layout()
plt.savefig('sector_per_distribution.png')
plt.show()

# 3. 히트맵으로 섹터별 top 5 PER 시각화
top_per_tickers = []
for sector in sectors.keys():
    sector_data = individual_stocks_df[individual_stocks_df['Sector'] == sector].copy()
    top5 = sector_data.nsmallest(5, 'PER')  # PER이 낮은 것이 저평가로 볼 수 있음
    top_per_tickers.extend(top5.to_dict('records'))

top_per_df = pd.DataFrame(top_per_tickers)

# 더 보기 좋은 피벗 테이블 만들기
pivot_df = pd.pivot_table(
    top_per_df, 
    values='PER', 
    index='Sector',
    columns='Ticker',
    aggfunc='first'
)

plt.figure(figsize=(18, 12))
sns.heatmap(pivot_df, annot=True, cmap='YlGnBu', fmt='.2f')
plt.title('Top 5 Lowest P/E Ratio Stocks by Sector', fontsize=16)
plt.tight_layout()
plt.savefig('sector_top_per_heatmap.png')
plt.show()

# 4. 섹터별 PER 분포 밀도 그래프
plt.figure(figsize=(16, 10))
for sector in sectors.keys():
    sector_data = individual_stocks_df[individual_stocks_df['Sector'] == sector]
    if len(sector_data) > 3:  # 데이터가 충분한 경우만
        sns.kdeplot(sector_data['PER'], label=sector)
        
plt.title('P/E Ratio Distribution by Sector', fontsize=16)
plt.xlabel('P/E Ratio', fontsize=14)
plt.ylabel('Density', fontsize=14)
plt.xlim(0, 80)  # 보기 좋게 x축 조정
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('sector_per_density.png')
plt.show()

# 5. 테이블 형태로도 결과 출력
print("\n===== 섹터별 평균 PER =====")
print(sector_avg_df[['Sector', 'PER']].sort_values('PER').reset_index(drop=True))

# CSV 파일로 저장
df_pers.to_csv('sector_per_analysis.csv', index=False)
sector_avg_df.to_csv('sector_avg_per.csv', index=False)