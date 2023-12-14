from datetime import datetime
from dataclasses import dataclass



## DB에 게시글 데이터를 저장하기 위한 데이터 클래스
@dataclass
class SecondhandPost:
    post_id: int
    member_id: int
    post_title: str
    post_content: str
    post_time: datetime
    post_update_time: datetime
    post_like_count: int
    post_view_count: int
    img_folder_address: str
    device_name: str
    secondhand_price: int
    post_url: str
    city: str
    street: str
    zipcode: str
    device_id: int

## DB에 Device 데이터를 저장하기 위한 데이터 클래스
@dataclass
class Device:
    device_name: str
    detail_id: int
    launch_price: int
    category: int
    release_date: datetime
    manufacturer: str