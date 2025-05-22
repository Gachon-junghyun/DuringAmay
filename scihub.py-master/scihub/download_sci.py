import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import logging

# 필요하면 pip install retrying
from retrying import retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaptchaNeedException(Exception):
    pass

class SciHub:
    def __init__(self):
        self.available_base_url_list = [
            "https://sci-hub.se",
            "https://sci-hub.st",
            "https://sci-hub.ru",
        ]
        self.base_url = self.available_base_url_list[0]
        self.sess = requests.Session()

    def _change_base_url(self):
        self.available_base_url_list.append(self.available_base_url_list.pop(0))
        self.base_url = self.available_base_url_list[0]
        logger.warning(f"🔁 Sci-Hub URL 변경됨 → {self.base_url}")

    def _classify(self, identifier):
        if identifier.startswith("http") and identifier.endswith(".pdf"):
            return 'url-direct'
        elif identifier.startswith("10."):
            return 'doi'
        else:
            return 'url'

    def _search_direct_url(self, identifier):
        url = f"{self.base_url}/{quote(identifier)}"
        logger.info(f"🔍 Sci-Hub 검색 중: {url}")
        res = self.sess.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        iframe = soup.find("iframe")

        if iframe:
            src = iframe.get("src")
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = self.base_url + src
            return src
        else:
            raise CaptchaNeedException("CAPTCHA 또는 PDF iframe 없음")

    def _generate_name(self, res):
        cd = res.headers.get('Content-Disposition', '')
        if 'filename=' in cd:
            return cd.split('filename=')[-1].strip('"; ')
        return "downloaded_paper.pdf"

    def _save(self, content, filepath):
        with open(filepath, 'wb') as f:
            f.write(content)
        logger.info(f"✅ 저장 완료: {filepath}")

    @retry(wait_random_min=1000, wait_random_max=3000, stop_max_attempt_number=5)
    def download(self, identifier, destination='pdfs', path=None):
        data = self.fetch(identifier)

        if 'err' not in data:
            filename = path if path else data['name']
            os.makedirs(destination, exist_ok=True)
            filepath = os.path.join(destination, filename)
            self._save(data['pdf'], filepath)

        return data

    def fetch(self, identifier):
        try:
            url = self._get_direct_url(identifier)
            res = self.sess.get(url, verify=False, timeout=10)

            if res.headers['Content-Type'] != 'application/pdf':
                logger.warning("❌ CAPTCHA 또는 잘못된 응답")
                self._change_base_url()
                raise CaptchaNeedException("PDF 응답이 아님")

            return {
                'pdf': res.content,
                'url': url,
                'name': self._generate_name(res)
            }

        except Exception as e:
            logger.warning(f"❗ 요청 실패: {e}")
            return {
                'err': str(e)
            }

    def _get_direct_url(self, identifier):
        id_type = self._classify(identifier)
        return identifier if id_type == 'url-direct' else self._search_direct_url(identifier)
    
import requests

def get_doi_from_semantic_url(semantic_id):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{semantic_id}"
    params = {
        "fields": "title,doi"
    }

    res = requests.get(url)
    if res.status_code != 200:
        print("❌ DOI 조회 실패:", res.status_code)
        return None

    data = res.json()
    doi = data.get("doi")
    print(f"📄 제목: {data.get('title')}")
    print(f"🔗 DOI: {doi}")
    return doi


if __name__ == "__main__":
    
    semantic_id = "e27073dfe39bed1e9e0e059cddccb351f3df059a"
    doi = get_doi_from_semantic_url(semantic_id)

    print(doi)

    scihub = SciHub()
    # DOI 또는 논문 URL 입력
    identifier = "10.1109/5.771073"  # 또는 Semantic Scholar 등에서 가져온 DOI

    result = scihub.download(identifier, destination="pdfs")

    if 'err' in result:
        print(f"❌ 다운로드 실패: {result['err']}")
    else:
        print(f"✅ 다운로드 성공: {result['name']}")

