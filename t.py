data = {}
import re
url_post = "/profile.php?id=100064178014446&sk=reels_tab&__cft__[0]=AZUjURtF0Tjn5Thi2mWVadp6meWLVsFQUuokUYtllOWKMWADrxIroKZoQQgKtpLt5IRpCX2Q28PJOhy-5n3YDDN6awEpCKltnOcwuIjUr-hboP2l5b31UUasLkmqtdXm__0RT7w0j0AmaFjPFqmQLRkTOL-JYjihlT_rSHmFeT9ppA"


def get_id_from_url(url: str) -> str:
    """Trích xuất giá trị của 'id' từ URL."""
    match = re.search(r"id=(\d+)", url)
    return match.group(1) if match else None

def extract_video_path(url):
    # Regex để bắt đoạn "page/videos/ID"
    match = re.search(r'([^/]+)/(videos|posts)/\d+', url)
    return match.group(0).replace('posts', 'videos') if match else None

print(extract_video_path("https://www.facebook.com/100064713214655/videos/28486223917658365/"))