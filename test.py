from managers import Driver
from time import sleep
import time  # Thêm dòng này để nhập thư viện time
from sql import profiles
import random
from handles import login
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

def random_delay(min_time=2, max_time=5):
    """Tạo độ trễ ngẫu nhiên"""
    sleep(random.uniform(min_time, max_time))

def random_scroll(driver):
    """Cuộn trang xuống tận cùng, đến giữa, lên trên cùng và quay lại"""
    # Cuộn xuống tận cùng của trang
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_delay(2, 4)
    
    # Cuộn đến giữa trang
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    random_delay(2, 4)
    
    # Cuộn lên trên cùng của trang
    driver.execute_script("window.scrollTo(0, 0);")
    random_delay(2, 4)
    
    # Quay lại trang trước đó
    driver.back()
    random_delay(2, 4)

def type_like_human(element, text, delay_range=(0.1, 0.3)):
    """Nhập văn bản vào một phần tử với hiệu ứng nhập bằng tay"""
    for char in text:
        element.send_keys(char)
        sleep(random.uniform(*delay_range))

def visit_product_and_back(driver, link):
    """Truy cập vào sản phẩm và quay lại"""
    href = link.get_attribute('href')
    if not href or 'ref=bookmarks' in href:
        print(f"Liên kết không hợp lệ hoặc chứa 'ref=bookmarks', bỏ qua.")
        return False

    # Cuộn đến phần tử trước khi click
    driver.execute_script("arguments[0].scrollIntoView(true);", link)
    random_delay(1, 2)

    # Thực hiện click vào liên kết
    try:
        link.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", link)

    print(f"Lướt qua liên kết: {href}")
    random_delay(10, 15)
    random_scroll(driver)
    random_delay(10, 15)
    random_scroll(driver)
    random_delay(10, 15)
    try:
        driver.back()
    except Exception as e:
        print(f"Không thể quay lại trang trước đó: {e}")
        driver.execute_script("window.history.go(-1)")
    random_delay(3, 6)
    random_scroll(driver)
    random_delay(3, 6)
    return True

def scroll_and_like_posts(driver, duration=60):
    """Lướt và like bài viết trong nhóm trong khoảng thời gian nhất định"""
    start_time = time.time()
    while time.time() - start_time < duration:
        # Tìm các bài viết
        posts = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet^='FeedUnit_']")
        for post in posts:
            try:
                # Cuộn đến bài viết
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                random_delay(2, 4)
                
                # Tìm và click nút like
                like_button = post.find_element(By.CSS_SELECTOR, "div[aria-label='Like']")
                if like_button:
                    like_button.click()
                    print("Đã like bài viết")
                    random_delay(2, 4)
            except Exception as e:
                print(f"Không thể like bài viết: {e}")
                continue
        
        # Cuộn xuống để tải thêm bài viết
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        random_delay(5, 7)

# Khởi tạo trình duyệt với proxy
profile = profiles.show(2)
driver = Driver(profile=profile)
# Mở trang Facebook
driver.get('https://www.facebook.com')
checkLogin = login({}, driver, profile.get('account'))
if checkLogin:
    print('Đăng nhập thành công')
# Đợi một chút để đăng nhập thành công
random_delay(5, 7)
search_box = driver.find("input[type='search']", type_query='css', wait=10)
if search_box:
    type_like_human(search_box, "Đồ chơi gỗ\n")
    random_delay(5, 7)
    search_box.send_keys(Keys.ENTER)
    random_delay(5, 7)

    # Tìm các liên kết đến nhóm từ thẻ div có thuộc tính role="main"
    group_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='https://www.facebook.com/groups']")
    print("Group links:", len(group_links))
    for link in group_links:
        href = link.get_attribute('href')
        if 'ref=bookmarks' in href:
            continue
        print(href)
    if group_links:
        # Truy cập vào nhóm đầu tiên không chứa 'ref=bookmarks'
        for link in group_links:
            href = link.get_attribute('href')
            if 'ref=bookmarks' not in href:
                group_link = link
                break
        print(group_link.get_attribute('href'))
        try:
            group_link.click()
            random_delay(5, 7)

            # Lướt và like bài viết trong nhóm trong 1 phút
            scroll_and_like_posts(driver, duration=60)

            # Quay lại trang tìm kiếm
            driver.back()
            random_delay(5, 7)

            # Lướt qua danh sách kết quả tìm kiếm một cách chậm rãi
            for _ in range(5):  # Lướt qua 5 lần
                random_scroll(driver)
                random_delay(5, 7)
        except Exception as e:
            print(f"Không thể truy cập nhóm: {e}")

driver.execute_script("window.open('https://www.google.com', '_blank');")
driver.switch_to.window(driver.window_handles[-1])

# Tìm và nhập từ khóa vào ô tìm kiếm
search_box = driver.find("textarea[name='q']", type_query='css', wait=10)
if search_box:
    type_like_human(search_box, "Đồ chơi gỗ\n")

# Đợi một chút để xem kết quả
random_delay(5, 7)

# Tìm và truy cập vào 5 liên kết đầu tiên có thuộc tính jsname="UWckNb"
links = driver.find_all("a[jsname='UWckNb']", type_query='css', wait=10)
if links:
    valid_links_count = 0
    for index in range(len(links)):
        if valid_links_count >= 5:
            break
        try:
            link = links[index]
            href = link.get_attribute('href')
            if not href:
                print(f"Liên kết không có thuộc tính href, bỏ qua.")
                continue

            # Cuộn đến phần tử trước khi click
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            random_delay(1, 2)

            # Thực hiện click vào liên kết
            try:
                link.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", link)

            print(f"Lướt qua liên kết {valid_links_count + 1}: {href}")
            random_delay(10, 15)  # Lướt trang từ 10-15s
            random_scroll(driver)
            random_delay(10, 15)  # Lướt trang từ 10-15s
            random_scroll(driver)
            random_delay(10, 15)  # Lướt trang từ 10-15s
            driver.back()
            random_delay(3, 6)
            random_scroll(driver)
            random_delay(3, 6)
            valid_links_count += 1
        except StaleElementReferenceException:
            print(f"Liên kết đã thay đổi hoặc không còn tồn tại, bỏ qua.")
            continue
        except Exception as e:
            print(f"Không thể lấy thuộc tính href của liên kết: {e}")
            continue
driver.quit()