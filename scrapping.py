from scraper.joongna_scraper import Joongna
from scraper.dangn_scraper import Dangn
from scraper.bunjang_scraper import Bunjang

import pymysql


class PostScraper:
    def __init__(self, host, user, password, db_name, charset, port):
        ## DB 세팅값
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.charset = charset
        self.port = port
        self._initialize_db()

    ## DB connection 세팅
    def _initialize_db(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password,
                        database=self.db_name, charset=self.charset, port=self.port)
        self.cursor = self.conn.cursor()

    ## base 사이트 세팅
    def _initialize_site(self, platform):
        _platform = None
        if platform == 'joongna':
            _platform = Joongna(self.cursor)
        elif platform == 'dangn':
            _platform = Dangn(self.cursor)
        elif platform == 'bunjang':
            _platform = Bunjang(self.cursor)
        self.base_platform = _platform
        self._new_post_urls = []
        self._new_post_texts = []
        self._locations = {}

    ## device_name 으로 device_id 가져오기
    def _fetch_device_id(self, device_name):
        print('_fetch_device_id\n')
        sql = 'select device_id from device where device_name = %s'
        self.cursor.execute(sql, device_name)
        device_id = int(self.cursor.fetchone()[0])
        print(device_id)
        return device_id

    ## DB에서 게시글 데이터 가져오기
    def _fetch_recent_post(self, category_num):
        print('fetch_recent_post\n')
        # 최근 게시글 5개 가져오기
        recent_posts = []
        lst = [self.base_platform.name, category_num]
        sql = ("select post_url from secondhand_scraped_post as s join post on s.post_id = post.post_id "
               "where post.member_id = (select member_id from member where name = %s) "
               "and (select category_id_by_site from category_by_site "
               "where category_id = (select category_id from device where device_id = s.device_id)) = %s "
               "order by post_time desc limit 80;")
        try:
            self.cursor.execute(sql, lst)
            recent_posts = self.cursor.fetchall()
            # 데이터 처리 로직 추가
        except pymysql.Error as e:
            print(f"데이터베이스 조회 중 오류 발생: {e}")
            # 예외 처리 또는 프로그램 종료 등을 수행
        finally:
            res = []
            for post in recent_posts:
                res.append(post[0])
            return res


    ## 스크래핑 후 새로운 게시글만 반환
    def scrape_new_post(self, recent_posts, scrapped_posts):
        print('scrape_new_post\n')
        new_posts = []

        for post in scrapped_posts:
            if post in recent_posts:
                break
            new_posts.append(post)

        print('new post : '+str(len(new_posts)))
        print('\nscrapped post : '+str(len(scrapped_posts)))
        # 새로운 게시글만 반환
        return new_posts

    ## 새롭게 올라온 게시글 추출
    def extract_new_posts(self, category_num):
        print('extract_new_posts\n')
        page = 1
        recent_posts = self._fetch_recent_post(category_num)

        while True:
            scrapped_posts, locations = self.base_platform.extract_link(category_num=category_num, page_num=page)
            new_posts = self.scrape_new_post(recent_posts, scrapped_posts)
            self._new_post_urls.extend(new_posts)
            self._locations.update(locations)

            ## 추출한 게시글의 수와 디비 확인을 걸친 게시글의 수가 같으면
            ## 디비에 어느것도 존재하지 않으므로 다음 페이지를 반복해서 탐색한다.
            ##### (*임시*) 너무 많이 가져와지는 것을 방지하기 위해 페이지는 5까지
            if len(new_posts) != len(scrapped_posts) or page >= 1:
                return
            page += 1

    ## 리스트에서 중복 제거
    def _remove_duplicate(self, lst):
        print('_remove_duplicate\n')
        keys = dict.fromkeys(lst)
        result = list(keys)
        return result

    ## DB에 게시글 본문 저장
    def _save_new_post_text(self, new_post_texts):
        print('_save_new_post_text\n')
        self.cursor.execute('select coalesce(MAX(post_id), 0) from post')
        idx = int(self.cursor.fetchone()[0])
        post_data = []
        post_query = ("insert into post (post_id, post_title, post_content, post_time, post_update_time, "
                      "post_like_count, post_view_count, member_id, "
                      "d_type, img_folder_address)"
                      "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        secondhand_post_data = []
        secondhand_post_query = ("insert into secondhand_scraped_post (post_id, device_id, "
                                 "post_url, secondhand_price, city, street, zipcode)"
                                 "values (%s, %s, %s, %s, %s, %s, %s)")

        ## 각각의 테이블에 삽입할 형식을 맞춰 저장
        for text in new_post_texts:
            text.device_id = 0
            try:
                text.device_id = self._fetch_device_id(text.device_name)
            except Exception as e:
                print(f'fetch_device_id error  :  {e}')
            idx += 1
            post_tup = (idx, text.post_title, text.post_content, text.post_time, text.post_update_time,
                   text.post_like_count, text.post_view_count, text.member_id,
                   'secondhand_scraped', text.img_folder_address)
            secondhand_tup = (idx, text.device_id, text.post_url, text.secondhand_price,
                              text.city, text.street, text.zipcode)

            post_data.append(post_tup)
            secondhand_post_data.append(secondhand_tup)

        self.cursor.executemany(post_query, post_data)

        self.cursor.executemany(secondhand_post_query, secondhand_post_data)


    ## DB에 알람 데이터 저장
    def _save_new_notification(self):
        pass

    ## FCM으로 알람 전송
    def send_notification(self):
        pass


    ## 게시글 스크래핑을 위한 프로세스
    def process_posts(self):
        # 새로운 url 스크래핑
        ### 카테고리 데이터를 DB에서 가져오는 방향으로 수정 필요!!
        category_nums = self.base_platform.category_nums
        for category_num in category_nums:
            self.extract_new_posts(category_num)

        ## 혹시 모를 중복 제거
        temp = self._remove_duplicate(self._new_post_urls)
        self._new_post_urls.clear()
        self._new_post_urls.extend(temp)

        # 본문 스크래핑
        for post_url in self._new_post_urls:
            try:
                text_dataclass = self.base_platform.extract_text(post_url, self._locations[post_url])
                self._new_post_texts.append(text_dataclass)
            except Exception as e:
                print(f'extract_new_post_text -  {e}')
        # 게시글 데이터 저장
        self._save_new_post_text(self._new_post_texts)

    ## 새로운 게시글 알람을 위한 프로세스
    def process_notification(self):
        pass


    ## 실행
    def run_scraper(self, site_name):
        self._initialize_site(site_name)
        try:
            self.process_posts()
            self.process_notification()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'why!!:  {e}')





# if __name__ == "__main__":
#     ## DB 세팅값
# load_dotenv()
# host_ = os.environ.get('DB_HOST')
# user_ = os.environ.get('DB_USER')
# password_ = os.environ.get('DB_PASSWORD')
# db_name_ = os.environ.get('DB_NAME')
# charset_ = os.environ.get('DB_CHARSET')
# port_ = int(os.environ.get('DB_PORT'))
#
# scraper = PostScraper(host_, user_, password_, db_name_, charset_, port_)
# print(scraper._fetch_device_id('기타'))
#     # 각 사이트 스크래핑 실행
#     scraper.run_scraper('joongna')
#     # scraper.run_scraper('dangn')
#     # scraper.run_scraper('bunjang')
#
#     ## DB 연결 해제
#     scraper.conn.close()

