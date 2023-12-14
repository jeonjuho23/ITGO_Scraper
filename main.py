from dotenv import load_dotenv
import os
from scrapping import PostScraper

## DB 세팅값
load_dotenv()
host_ = os.environ.get('DB_HOST')
user_ = os.environ.get('DB_USER')
password_ = os.environ.get('DB_PASSWORD')
db_name_ = os.environ.get('DB_NAME')
charset_ = os.environ.get('DB_CHARSET')
port_ = int(os.environ.get('DB_PORT'))


if __name__ == "__main__":

    scraper = PostScraper(host_, user_, password_, db_name_, charset_, port_)

    # 각 사이트 스크래핑 실행
    scraper.run_scraper('joongna')
    # scraper.run_scraper('dangn')
    # scraper.run_scraper('bunjang')

    ## DB 연결 해제
    scraper.conn.close()