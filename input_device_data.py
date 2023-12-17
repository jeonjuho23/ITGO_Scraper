from data import Device
from datetime import datetime
import pymysql
from dotenv import load_dotenv
import os

##== DB에 새로운 Device 데이터를 입력하기 위한 Python 파일  ==##


## DB에 디바이스 데이터를 삽입하는 함수
def insert_new_device(device_data:Device):

    device_tup = (device_data.device_name, device_data.detail_id,
                  device_data.launch_price, device_data.category, device_data.release_date,
                  device_data.manufacturer)

    ## db 세팅값
    load_dotenv()
    host = os.environ.get('DB_HOST')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')
    charset = os.environ.get('DB_CHARSET')
    port = int(os.environ.get('DB_PORT'))

    with pymysql.connect(host=host, user=user, password=password,
                         database=db_name, charset=charset, port=port) as conn:
        # Create a cursor object to interact with the database
        with conn.cursor() as cursor:
            cursor.execute('SET @max_device_id = (SELECT coalesce(MAX(device_id), 0) FROM device);')
            # Define the SQL query for insertion
            query = ('INSERT INTO device (device_id, device_name, detail_id, launch_price, category_id, release_date, manufacturer) '
                     'VALUES (@max_device_id + 1, %s, %s, %s, %s, %s, %s)')

            # Execute the query with the provided data
            cursor.execute(query, device_tup)

        # Commit the changes to the database
        conn.commit()


## 삽입할 데이터를 입력받는 함수
def input_data():
    # 키보드 입력을 통해 데이터 입력 받기
    device_name = input("Enter device name: ")
    detail_id_input = input("Enter detail ID: ")
    if detail_id_input:
        detail_id = int(detail_id_input)
    else:
        detail_id = 0
    launch_price = int(input("Enter launch price: "))
    category = int(input("Enter category: "))
    release_date_str = input("Enter release date (YYYY-MM-DD): ")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
    manufacturer = input("Enter manufacturer: ")

    # 데이터 클래스 객체 생성
    new_device = Device(
        device_name=device_name,
        detail_id=detail_id,
        launch_price=launch_price,
        category=category,
        release_date=release_date,
        manufacturer=manufacturer
    )

    # 생성된 객체 확인
    print("New Device:")
    print(new_device)

    insert_new_device(new_device)



is_true = True

while is_true:
    con = input("continue? (y or n)  ")
    if con == 'y' or con == 'yes' or con == 'Y' or con == 'Yes':
        input_data()
    elif con == 'n' or con == 'no' or con == 'N' or con == 'No':
        break
