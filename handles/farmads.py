from sql import profiles, posts
from managers import Driver
from .login import login
from time import sleep
from selenium.webdriver.common.by import  By
from stores import farm_ads
import pyperclip
import time
import random
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def start_crawl_up(id):
    from handles import getContentPost
    tab = farm_ads[id]
    profile = profiles.show(id)

    if not tab or not profile:
        return
    stop_event = tab['stop_event']
    while not stop_event.is_set():
        tab['status'] = 'Bắt đầu khời tạo trình duyệt'
        account = profile.get('account')
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
        try:
            tab['status'] = 'Đang khởi tạo trình duyệt....'
            driver = Driver(profile) # Khởi tạo
            
            tab['check'] = 1
            tab['status_process'] = 1
            tab['status'] = 'Đã khởi tạo trình duyệt'

            tab['status'] = 'Đang chuyển hướng facebook...'
            driver.get('https://facebook.com', e_wait=3)

            while not stop_event.is_set():
                status_login = login(tab, driver, account)
                if status_login == False:
                    print('Login succes')
                    tab['status'] == 'Tài khoản hiện không thể login, thử lại sau 15p',
                    raise Exception('Login failed')
                    sleep(900)
                    continue
                else: 
                    break
            tab['status'] = 'Số từ khoá cần search: ' + str(len(keywords))

            for key in keywords:
                print('Xử lý từ khoá: ', key)
                tab['status'] = f"Đang xử lý từ khoá: '{key}'"
                try:
                    print('Search: ', key)
                    search_box = driver.find("input[type='search']", type_query='css', wait=10, send_keys=key)
                    search_box.send_keys(Keys.ENTER)
                    driver.random_delay(5, 7)
                    index = 0
                    while not stop_event.is_set():
                        try:
                            index = index + 1
                            if index > 3:
                                break
                            group_link = getLinkFanpage(driver, index)
                            actions = driver.action_chains()
                            if group_link is None:
                                print(f"Từ khoá: {key} no {index}, bỏ qua.")
                                break
                            print(f'Fanpage: {group_link.text}')
                            actions.move_to_element(group_link)
                            driver.random_delay(2, 3)
                            group_link.click()
                            driver.random_delay(5, 7)
                            print('Scroll fanpage')
                            scroll_and_like_posts(driver, duration=60)
                            driver.back()
                            driver.random_delay(3, 5)
                        except Exception as e:
                            print(f'Lỗi click page: {e}')
                            continue
                except Exception as e:
                    print(f'Lỗi xảy ra: {e}')

            print('Fanapge trang chu')
            tab['status'] = f"Bắt đầu lướt trang chủ lấy bài viết!"
            try:
                driver.get('https://facebook.com/home.php', e_wait=2)
                print('Chuyển hướng facebook')
                driver.clickOk()
                sleep(1)

                post_list = create_browser_link_spy_fb(driver, account, stop_event, tab)
                print('Số bài viết lấy được: ', len(post_list))
                tab['status'] = f"Đã lấy được {len(post_list)} bài viết!"
                for p in post_list:
                    try:
                        data = getContentPost(driver, p)
                        # print(json.dumps(data, indent=4))
                        res = posts.create(data)
                        print(f'Res: {res}')
                        tab['status'] = 'Đã thêm dữ liệu!'
                        print(f'======================================')
                    except Exception as e:
                        print(f'Lỗi khi thêm bài viết: {e}')
                sleep(1)
            except Exception as e:
                tab['status'] = f"Lỗi: {e}"
                print(f'Lỗi khi cào bài viết: {e}')
        except Exception as e:
            tab['status'] = 'Đã xảy ra lỗi....'
            print(f"Đã có lỗi xảy ra: {e}")
        finally:
            tab['status'] = 'Đang đóng....'
            driver.quit()
            print('Trình duyệt đã bị đóng')
        sleep(3600)

def stop_crawl_up(id):
    thread = farm_ads[id]['thread']
    thread.join()
    farm_ads[id]['check'] = 1
    del farm_ads[id]

def extract_post_id(url):
    match = re.search(r'/(p|v)/([a-zA-Z0-9]+)', url)
    return match.group(2) if match else ''

def create_browser_link_spy_fb(driver, account, stop_event, tab):
    list_posts = []
    listId = set()
    tab['status'] = 'Room nhỏ màn hình!'
    print('Room nhỏ màn hình')
    sleep(3)
    while not stop_event.is_set():
        tab['status'] = 'Bắt đầu cào bài viết!'
        listPosts = driver.find_all('//*[@aria-posinset]') 
        print(f'Số bài viết lấy được: {len(listPosts)}')

        if len(listPosts) == 0:
            raise RuntimeError('Không tìm thấy bài viết nào để duyệt.')

        actions = driver.action_chains()
        for p in listPosts:
            try:
                stt = p.get_attribute('aria-posinset')
                if stt not in listId:
                    listId.add(stt)
                    links = p.find_elements(By.XPATH, ".//a")
                    for link in links:
                        if link.is_displayed() and link.size['width'] > 0 and link.size['height'] > 0:
                            actions.move_to_element(link).perform()
                            href = link.get_attribute('href')
                            if '/ads/' in href:
                                try:
                                    share = p.find_element(By.XPATH, './/*[@aria-label="Send this to friends or post it on your profile."]')
                                    actions.move_to_element(share).perform()
                                    share.click()
                                    sleep(10)
                                    parent_element = driver.find(".//*[@aria-label='List of available \"share to\" options in the unified share sheet.']")
                                    if parent_element:
                                        list = parent_element.find_elements(By.XPATH, "./div/div/div")
                                        for item in list:
                                            item_text = item.text.lower()
                                            if "copy link" in item_text:
                                                item.click()
                                                sleep(2)
                                                break
                                        
                                        fb_link = pyperclip.paste()
                                        fb_id = extract_post_id(fb_link)
                                        list_posts.append({
                                            'account_id': account.get('id'),
                                            'fb_link': fb_link,
                                            'fb_id': fb_id,
                                        })
                                        print(f"Bài số: {len(list_posts)} - {fb_link}")
                                        tab['status'] = f'Đã thêm bài viết {len(list_posts)}/20!'
                                except Exception as e:
                                    print(f'Lỗi click share {stt}: {e}')
                                break
            except Exception as e:
                print(e)
        if len(list_posts) >= 20:
            print('Đã thu thập đủ 20 bài viết, trả về danh sách.')
            return list_posts
        driver.randomSleep()
        tab['status'] = 'Cuộn chuột xuống!'
        driver.execute_script("window.scrollBy(0, 200);")
        sleep(5)
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

def getLinkFanpage(driver, index=0):
    """ Lấy link nhóm trên Facebook. Nếu danh sách trống, cuộn xuống và thử lại. """
    
    def extract_unique_groups():
        """ Trích xuất danh sách nhóm hợp lệ (lọc trùng) """
        group_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='https://www.facebook.com/groups']")
        print("Tổng số link nhóm tìm thấy:", len(group_links))
        valid_groups = [link for link in group_links if 'ref=bookmarks' not in link.get_attribute('href') and '?' not in link.get_attribute('href')]
        return valid_groups

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

