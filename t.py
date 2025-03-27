# data = {}
# import re
# url_post = "/profile.php?id=100064178014446&sk=reels_tab&__cft__[0]=AZUjURtF0Tjn5Thi2mWVadp6meWLVsFQUuokUYtllOWKMWADrxIroKZoQQgKtpLt5IRpCX2Q28PJOhy-5n3YDDN6awEpCKltnOcwuIjUr-hboP2l5b31UUasLkmqtdXm__0RT7w0j0AmaFjPFqmQLRkTOL-JYjihlT_rSHmFeT9ppA"


# def get_id_from_url(url: str) -> str:
#     """Trích xuất giá trị của 'id' từ URL."""
#     match = re.search(r"id=(\d+)", url)
#     return match.group(1) if match else None

# def extract_video_path(url):
#     # Regex để bắt đoạn "page/videos/ID"
#     match = re.search(r'([^/]+)/(videos|posts)/\d+', url)
#     return match.group(0).replace('posts', 'videos') if match else None

# print(extract_video_path("https://www.facebook.com/100064713214655/videos/28486223917658365/"))

# tim = [
#     {
#         "index": 2,
#         "text": "O"
#     },
#     {
#         "index": 11,
#         "text": "c"
#     },
#     {
#         "index": 16,
#         "text": "t"
#     },
#     {
#         "index": 17,
#         "text": "o"
#     },
#     {
#         "index": 18,
#         "text": "b"
#     },
#     {
#         "index": 19,
#         "text": "e"
#     },
#     {
#         "index": 25,
#         "text": "r"
#     },
#     {
#         "index": 33,
#         "text": ""
#     },
#     {
#         "index": 35,
#         "text": "2"
#     },
#     {
#         "index": 36,
#         "text": "3"
#     },
#     {
#         "index": 37,
#         "text": ","
#     },
#     {
#         "index": 42,
#         "text": ""
#     },
#     {
#         "index": 52,
#         "text": "2"
#     },
#     {
#         "index": 53,
#         "text": "0"
#     },
#     {
#         "index": 57,
#         "text": "2"
#     },
#     {
#         "index": 59,
#         "text": "4"
#     }
# ]

# result_string = "".join(item['text'] if item['text'] else " " for item in tim)
# from helpers import convert_to_db_format
# print(f"Result: {result_string}")
# print(f"DB: {convert_to_db_format(result_string)}")

import re

def extract_facebook_id(url):
    match = re.search(r'(?:/posts/|story_fbid=)(pfbid[a-zA-Z0-9]+)', url)  
    return match.group(1) if match else None  

# Test với hai trường hợp
urls = [
    "https://www.facebook.com/owl.vietnam/posts/pfbid02NZE2GpqjrPcMAZEiDXKoEMj2vfgKKXkxQFUCroY3LReqJmJT8g2p1vyKoJoYYF5vl?rdid=OjzpUYF4M8jTlulz#",
    "https://www.facebook.com/permalink.php?story_fbid=pfbid0Ns8tXHWwY8uVrjNUr63fExjEEWaaUYM7qcJtMB2McFpA8LuWhq1adKn6wLdqWAAfl&id=100012050298643"
]

for url in urls:
    print(f"URL: {url}")
    print(f"Extracted ID: {extract_facebook_id(url)}\n")
