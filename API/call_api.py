import requests

# Địa chỉ API
api_address='http://192.168.143.54:8668'

# API lấy các link đã crawl của 1 id
def get_links(table_name, object_id):
    url = f"{api_address}/get-links/{table_name}/{object_id}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

# API insert link đã crawl vào db
def insert(table_name, object_id, links):
    if isinstance(links, list):
        links = ",".join(links)
    url = f"{api_address}/insert/{table_name}/{object_id}?new_links={links}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

if __name__=="__main__":
    # Gọi API và lấy kết quả
    links=['qqqqqq','aaaaa']
    result = insert("youtube_video", "@test",links)
    print(result)
