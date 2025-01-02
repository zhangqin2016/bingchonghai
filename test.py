import requests
import json
import time

# 城市数据请求 URL
countries = {
    "NP": "http://api.geonames.org/citiesJSON?lang=zh&country=NP&username=zhangqinqin&north=30.5&south=26.3&east=88.2&west=80.0&maxRows=20",
    "BD": "http://api.geonames.org/citiesJSON?lang=zh&country=BD&username=zhangqinqin&north=26.7&south=20.9&east=92.6&west=88.0&maxRows=20",
    "VN": "http://api.geonames.org/citiesJSON?lang=zh&country=VN&username=zhangqinqin&north=23.4&south=8.1&east=109.5&west=102.1&maxRows=20",
    "MM": "http://api.geonames.org/citiesJSON?lang=zh&country=MM&username=zhangqinqin&north=28.6&south=9.5&east=101.2&west=92.2&maxRows=20",
    "KZ": "http://api.geonames.org/citiesJSON?lang=zh&country=KZ&username=zhangqinqin&north=55.4&south=40.0&east=87.0&west=46.0&maxRows=20"
}

# 最大重试次数
MAX_RETRIES = 6
RETRY_DELAY = 1  # 延迟时间（秒）


# 发送请求并获取城市数据（加入重试机制）
def fetch_cities(country_code, url):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            response = requests.get(url)
            response.raise_for_status()  # 如果响应错误会抛出异常
            data = response.json()

            # 检查返回数据是否符合预期结构
            if 'geonames' in data:
                return data['geonames']
            else:
                print(f"错误：返回的数据不包含 'geonames' 字段，重试 {attempt + 1}/{MAX_RETRIES}...")

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"请求或解析出错: {e}, 重试 {attempt + 1}/{MAX_RETRIES}...")

        # 等待一段时间再重试
        attempt += 1
        time.sleep(RETRY_DELAY)

    raise Exception(f"请求失败，已达到最大重试次数 {MAX_RETRIES} 次。")


# 生成插入语句
def generate_insert_statements(cities, country_code):
    insert_cites_sql = []
    insert_latlng_sql = []

    for city in cities:
        # fff_cites 表的插入语句
        code = city['geonameId']
        name = city['name']
        province_code = country_code  # 根据需要填写
        insert_cites_sql.append(
            f"INSERT INTO `split_table_info` (`split_key`, `split_table`) VALUES ('NP_{code}', 'fff_address_weather_log_split_guowai');")

        # fff_address_latlng 表的插入语句
        lat = city['lat']
        lng = city['lng']
        address_code = code  # 假设使用 geonameId 作为地址代码
        address_level = 2  # 假设为城市级别
        insert_latlng_sql.append(
            f"INSERT INTO `fff_address_latlng` (`address_code`, `lat`, `lng`, `address_level`) VALUES ('NP_{address_code}', '{lat}', '{lng}', {address_level});")

    return insert_cites_sql, insert_latlng_sql


# 主程序
def main():
    all_insert_cites_sql = []
    all_insert_latlng_sql = []

    for country_code, url in countries.items():
        try:
            cities = fetch_cities(country_code, url)
            insert_cites_sql, insert_latlng_sql = generate_insert_statements(cities, country_code)
            all_insert_cites_sql.extend(insert_cites_sql)
            all_insert_latlng_sql.extend(insert_latlng_sql)
        except Exception as e:
            print(f"错误：无法获取或解析 {country_code} 的城市数据: {e}")

    # 打印所有的 INSERT 语句
    print("插入 fff_cites fff_address_latlng 表的 SQL 语句：")
    for sql in all_insert_cites_sql:
        print(sql)

    for sql in all_insert_latlng_sql:
        print(sql)


if __name__ == "__main__":
    main()
