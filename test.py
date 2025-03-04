from managers import Driver
from time import sleep
import time  # Thêm dòng này để nhập thư viện time
from sql import profiles
import random
from handles import login
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException


def random_scroll(driver):
    """Cuộn trang xuống tận cùng, đến giữa, lên trên cùng và quay lại"""
    # Cuộn xuống tận cùng của trang
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.random_delay(2, 4)
    
    # Cuộn đến giữa trang
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    driver.random_delay(2, 4)
    
    # Cuộn lên trên cùng của trang
    driver.execute_script("window.scrollTo(0, 0);")
    driver.random_delay(2, 4)
    
    # Quay lại trang trước đó
    driver.back()
    driver.random_delay(2, 4)

def type_like_human(element, text, delay_range=(0.1, 0.3)):
    element.send_keys(Keys.CONTROL + "a")  
    element.send_keys(Keys.DELETE)
    time.sleep(0.5)

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
    driver.random_delay(1, 2)

    # Thực hiện click vào liên kết
    try:
        link.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", link)

    print(f"Lướt qua liên kết: {href}")
    driver.random_delay(10, 15)
    random_scroll(driver)
    driver.random_delay(10, 15)
    random_scroll(driver)
    driver.random_delay(10, 15)
    try:
        driver.back()
    except Exception as e:
        print(f"Không thể quay lại trang trước đó: {e}")
        driver.execute_script("window.history.go(-1)")
    driver.random_delay(3, 6)
    random_scroll(driver)
    driver.random_delay(3, 6)
    return True

def scroll_and_like_posts(driver, duration=180):
    """Lướt và like bài viết trong nhóm trong khoảng thời gian nhất định"""
    start_time = time.time()
    while time.time() - start_time < duration:
        # Tìm các bài viết
        posts = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet^='FeedUnit_']")
        for post in posts:
            try:
                # Cuộn đến bài viết
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                driver.random_delay(30, 60)
                
                # Tìm và click nút like
                like_button = post.find_element(By.CSS_SELECTOR, "div[aria-label='Like']")
                if like_button:
                    like_button.click()
                    print("Đã like bài viết")
                    driver.random_delay(2, 4)
            except Exception as e:
                print(f"Không thể like bài viết: {e}")
                continue
        
        # Cuộn xuống để tải thêm bài viết
        driver.execute_script("window.scrollBy(0, 600);")
        driver.random_delay(5, 7)
import re
import json
def getLinkFanpage(driver, index=0):
    """ Lấy link nhóm trên Facebook. Nếu danh sách trống, cuộn xuống và thử lại. """
    
    def extract_unique_groups():
        """ Trích xuất danh sách nhóm hợp lệ (lọc trùng) """
        group_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='https://www.facebook.com/groups']")
        print("Tổng số link nhóm tìm thấy:", len(group_links))

        valid_groups = [link for link in group_links if 'ref=bookmarks' not in link.get_attribute('href')]
        unique_groups = []
        seen_group_ids = set()

        for link in valid_groups:
            href = link.get_attribute('href')
            match = re.search(r"https://www\.facebook\.com/groups/([\w\d]+)", href)
            if match:
                group_id = match.group(1)
                if group_id not in seen_group_ids:
                    seen_group_ids.add(group_id)
                    unique_groups.append(link)

        return unique_groups

    # Lấy danh sách nhóm lần đầu
    unique_groups = extract_unique_groups()

    # Nếu không tìm thấy nhóm, cuộn chuột xuống và thử lại
    if not unique_groups:
        print("Không tìm thấy nhóm nào, cuộn chuột xuống thử lại...")
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(2)  # Chờ trang tải lại

        unique_groups = extract_unique_groups()  # Lấy danh sách nhóm sau khi cuộn

    # Trả về nhóm theo index nếu có, nếu không thì trả về None
    if 0 <= index < len(unique_groups):
        return unique_groups[index]

    print("Không tìm thấy nhóm nào sau khi cuộn. Trả về None.")
    return None

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def click_element_safely(driver, element):
    """ Cuộn phần tử vào giữa màn hình và click an toàn """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element)).click()

profile = profiles.show(2)
driver = Driver(profile=profile)

driver.get('https://www.facebook.com')
checkLogin = login({}, driver, profile.get('account'))
if checkLogin:
    print('Đăng nhập thành công')

keywords = [
    "Wooden toys",
    "Wood toys",
    "Toys made of wood",
    "Children's wooden toys",
    "Kids wooden toys",
    "Natural wooden toys",
    "Eco-friendly wooden toys",
    "Handmade wooden toys",
    "Wooden toy shop",
    "Wooden toy store",
    "Wooden building blocks",
    "Wooden puzzles",
    "Wooden stacking toys",
    "Wooden pull toys",
    "Wooden toy cars",
    "Wooden toy trains",
    "Wooden dollhouses",
    "Wooden kitchen toys",
    "Wooden educational toys",
    "Montessori wooden toys",
    "Safe wooden toys",
    "Non-toxic wooden toys",
    "Sustainable wooden toys",
    "Wooden toy gifts",
    "Wooden toy for toddlers",
    "Wooden toy for preschoolers"
]

driver.random_delay(5, 7)
search_box = driver.find("input[type='search']", type_query='css', wait=10)
if search_box:
    for key in keywords:
        type_like_human(search_box, key)
        driver.random_delay(1, 2)
        search_box.send_keys(Keys.ENTER)
        driver.random_delay(5, 7)

        # for _ in range(3):  # Lặp 3 lần để cuộn xuống nhiều hơn
        #     driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        #     driver.random_delay(10, 20)

        # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)

        # Tìm các liên kết đến nhóm từ thẻ div có thuộc tính role="main"

        for i in range(3):  # Chạy từ index 0 đến index 1
            group_link = getLinkFanpage(driver, i)
            if group_link is None:
                print(f"Không tìm thấy nhóm hợp lệ ở index {i}, bỏ qua.")
                continue

            try:
                # Đóng popup nếu có
                try:
                    close_popup = driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] button")
                    close_popup.click()
                    print("Đã đóng popup.")
                except:
                    pass  # Không có popup thì bỏ qua

                click_element_safely(driver, group_link)

                driver.random_delay(5, 7)
                scroll_and_like_posts(driver, duration=60)
                driver.back()
                driver.random_delay(3, 5)

            except Exception as e:
                print(f"Không thể truy cập nhóm {i}: {e}")
driver.quit()
