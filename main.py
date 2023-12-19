from dotenv import load_dotenv
import os
from scrapping import PostScraper
import schedule
import time

## DB 세팅값
load_dotenv()
host_ = os.environ.get('DB_HOST')
user_ = os.environ.get('DB_USER')
password_ = os.environ.get('DB_PASSWORD')
db_name_ = os.environ.get('DB_NAME')
charset_ = os.environ.get('DB_CHARSET')
port_ = int(os.environ.get('DB_PORT'))

def _run():
    scraper = PostScraper(host_, user_, password_, db_name_, charset_, port_)

    scraper.run_scraper('joongna')
    # scraper.run_scraper('dangn')
    # scraper.run_scraper('bunjang')

    ## DB 연결 해제
    scraper.conn.close()

# if __name__ == "__main__":


    # 각 사이트 스크래핑 실행
    # 10분에 한번씩 함수 실행
schedule.every(5).minutes.do(_run)

while True:
    schedule.run_pending()
    time.sleep(1)
    print('...')




