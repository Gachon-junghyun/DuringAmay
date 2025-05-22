import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

class NewsFetcher:
    def __init__(self):
        self.bigkinds_url = "https://www.bigkinds.or.kr/v2/news/search.do"
        self.economic_calendar_url = "https://www.investing.com/economic-calendar/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_economic_calendar(self):
        try:
            response = requests.get(self.economic_calendar_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'economicCalendarData'})
            if not table:
                raise Exception("경제 캘린더 테이블을 찾을 수 없습니다.")

            events = []
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    event = {
                        '시간': cols[0].text.strip(),
                        '통화': cols[1].text.strip(),
                        '영향': cols[2].text.strip(),
                        '이벤트': cols[3].text.strip(),
                        '실제': cols[4].text.strip(),
                        '예측': cols[5].text.strip(),
                        '이전': cols[6].text.strip()
                    }
                    events.append(event)

            return pd.DataFrame(events)

        except Exception as e:
            print(f"[경제 캘린더] 에러 발생: {str(e)}")
            return pd.DataFrame()

    def fetch_bigkinds_news(self):
        try:
            # BigKinds는 실제로는 POST 요청 및 로그인/세션 등이 필요할 수 있음. 여기서는 단순 GET 사용 예시.
            response = requests.get(self.bigkinds_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 예시 - BigKinds 메인 페이지에서 주요 뉴스 타이틀을 가져온다고 가정
            titles = soup.find_all('div', class_='news-item')  # 실제 클래스는 다를 수 있음
            news_data = []
            for title in titles:
                headline = title.get_text(strip=True)
                news_data.append({'headline': headline, 'source': 'BigKinds'})

            return pd.DataFrame(news_data)

        except Exception as e:
            print(f"[BigKinds 뉴스] 에러 발생: {str(e)}")
            return pd.DataFrame()

    def fetch_all(self):
        calendar_df = self.fetch_economic_calendar()
        news_df = self.fetch_bigkinds_news()

        return {
            'economic_calendar': calendar_df,
            'news': news_df
        }

if __name__ == "__main__":
    fetcher = NewsFetcher()
    data = fetcher.fetch_all()
    print("\n[경제 캘린더 요약]")
    print(data['economic_calendar'].head())
    print("\n[BigKinds 뉴스 요약]")
    print(data['news'].head())
