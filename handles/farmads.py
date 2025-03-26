from sql import profiles, posts
from managers import Driver
from .login import login
from time import sleep
from selenium.webdriver.common.by import  By
from stores import farm_ads
import pyperclip
import time
import random
import json
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def dd(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def start_crawl_up(id):
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
            "Wood toys"
        ]
        try:
            tab['status'] = 'Đang khởi tạo trình duyệt....'
            driver = Driver(profile) # Khởi tạo
            
            tab['check'] = 1
            tab['status_process'] = 1
            tab['status'] = 'Đã khởi tạo trình duyệt'

            driver.get('https://facebook.com', e_wait=3)
            get_first_ads(driver, account, stop_event)

            # tab['status'] = 'Đang lấy id library dựa theo từ khóa'
            # listIdBrary = getLibraryId(driver, keywords)
            # print(json.dumps(listIdBrary, indent=4))
            # tab['status'] = 'Đang lấy nội dung bài quảng cáo tại library'
            # dataContent = getContentInLibrary(driver, listIdBrary)
            # tab['status'] = 'Thực hiện gửi dữ liệu lên serve'
            # print(json.dumps(dataContent, indent=4))
            # driver.get('https://facebook.com', e_wait=3)

            # while not stop_event.is_set():
            #     status_login = login(tab, driver, account)
            #     if status_login == False:
            #         print('Login succes')
            #         tab['status'] == 'Tài khoản hiện không thể login, thử lại sau 15p',
            #         raise Exception('Login failed')
            #     else: 
            #         break
            # tab['status'] = 'Số từ khoá cần search: ' + str(len(keywords))

            # for key in keywords:
            #     print('Xử lý từ khoá: ', key)
            #     tab['status'] = f"Đang xử lý từ khoá: '{key}'"
            #     try:
            #         print('Search: ', key)
            #         search_box = driver.find("input[type='search']", type_query='css', wait=10)
            #         search_box.send_keys(Keys.CONTROL + "a")  # Chọn toàn bộ nội dung
            #         search_box.send_keys(Keys.DELETE)         # Xóa nội dung đã chọn
            #         search_box.send_keys(key)
            #         search_box.send_keys(Keys.ENTER)
            #         driver.random_delay(5, 7)
            #         index = 0
            #         while not stop_event.is_set():
            #             try:
            #                 index = index + 1
            #                 if index > 3:
            #                     break
            #                 group_link = getLinkFanpage(driver, index)
            #                 actions = driver.action_chains()
            #                 if group_link is None:
            #                     print(f"Từ khoá: {key} no {index}, bỏ qua.")
            #                     break
            #                 print(f'Fanpage: {group_link.text}')
            #                 actions.move_to_element(group_link)
            #                 driver.random_delay(2, 3)
            #                 group_link.click()
            #                 driver.random_delay(5, 7)
            #                 print('Scroll fanpage')
            #                 scroll_and_like_posts(driver, duration=60)
            #                 driver.back()
            #                 driver.random_delay(3, 5)
            #             except Exception as e:
            #                 print(f'Lỗi click page: {e}')
            #                 continue
            #     except Exception as e:
            #         print(f'Lỗi xảy ra: {e}')

            # print('Fanapge trang chu')
            # tab['status'] = f"Bắt đầu lướt trang chủ lấy bài viết!"
            # try:
            #     driver.get('https://facebook.com/home.php', e_wait=2)
            #     print('Chuyển hướng facebook')
            #     driver.clickOk()
            #     sleep(1)

            #     post_list = create_browser_link_spy_fb(driver, account, stop_event, tab)
            #     print('Số bài viết lấy được: ', len(post_list))
            #     tab['status'] = f"Đã lấy được {len(post_list)} bài viết!"
            #     for p in post_list:
            #         try:
            #             data = getContentPost(driver, p)
            #             # print(json.dumps(data, indent=4))
            #             res = posts.create(data)
            #             print(f'Res: {res}')
            #             tab['status'] = 'Đã thêm dữ liệu!'
            #             print(f'======================================')
            #         except Exception as e:
            #             print(f'Lỗi khi thêm bài viết: {e}')
            #     sleep(1)
            # except Exception as e:
            #     tab['status'] = f"Lỗi: {e}"
            #     print(f'Lỗi khi cào bài viết: {e}')
        except Exception as e:
            tab['status'] = 'Đã xảy ra lỗi....'
            print(f"Errorr: {e}")
        finally:
            tab['status'] = 'Đang đóng....'
            driver.quit()
            print('Close browser')
        
        for i in range(3600, 0, -1):
            if stop_event.is_set():
                break
            tab['status'] = f'Chờ: {i}s để tiếp tục'
            sleep(1)

def get_first_ads(driver, account, stop_event):
    from handles import getContentPost
    listId = set()
    count = 0
    while not stop_event.is_set():
        if count >= 5:
            return
        listPosts = driver.find_all('[aria-posinset]','css')
        print(f'Count post get success: {len(listPosts)}')

        if len(listPosts) == 0:
            driver.execute_script("window.scrollBy(0, 300);")
            continue

        for p in listPosts:
            try:
                isSponsored = checkAds(driver,p)

                stt = p.get_attribute('aria-posinset')
                print(f"{stt} - {isSponsored}")
                if isSponsored == False:
                    sleep(2)
                    continue
                if stt not in listId:
                    listId.add(stt)
                    try:
                        try:
                            data = getContentPost(driver, p)
                            data['post']['account_id'] = account.get('id')
                            res = posts.create(data)
                            print(f"=> Res insert data: ")
                            # dd(res)
                            count += 1
                        except Exception as e:
                            print(f'Error when get content: {e}')
                        driver.closeModal(last=True)
                    except Exception as e:
                        print(f'Error click share {stt}: {e}')
            except Exception as e:
                print(e)
        driver.execute_script("window.scrollBy(0, 200);")
        driver.randomSleep()
        


def checkAds(driver, p):
    actions_chains = driver.action_chains()
    as_links = p.find_elements(By.CSS_SELECTOR, 'a[role="link"][target="_blank"]')
    print(f"Len link: {len(as_links)}")
    for a in as_links:
        if not a.is_displayed():
            print("Next: tag <a> not view.")
            continue
        try:
            actions_chains.move_to_element(a).perform()  # Hover vào thẻ <a>
        except Exception as e:
            print(f"Error when hover tag <a>: {e}")
            continue  # Nếu lỗi thì bỏ qua phần tử này
        
    # Lọc lại danh sách link sau khi hover
    is_sponsored = False

    as_links = [
        link for link in as_links
        if (href := link.get_attribute("href")) and 
        ("__cft__[0]=" in href or "/ads/" in href) and 
        link.text.strip() != ''
    ]


    # Kiểm tra xem bài viết có được tài trợ không
    for a in as_links:
        spans = a.find_elements(By.CSS_SELECTOR, 'span > span > span > span')
        content = [
            span.text.strip()
            for span in spans
            if span.text.strip() and span.value_of_css_property("position") != "absolute"
        ]
        if not is_sponsored:
            is_sponsored = sorted(content) == sorted("Sponsored")
        
        if not is_sponsored:
            is_sponsored = sorted(content) == sorted("Đượctàitrợ")
    return is_sponsored

def getLibraryId(driver, keywords):
    libraryId = []
    
    for key in keywords:
        link = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q={key}&search_type=keyword_unordered"
        driver.get(link)
        
        elements = driver.find_elements("xpath", "//*[contains(text(), 'Library ID:')]")
        
        for element in elements:
            text = element.text
            if "Library ID:" in text:
                id_part = text.split("Library ID:")[-1].strip()
                if not any(entry["library_id"] == id_part for entry in libraryId):
                    libraryId.append({
                        "library_id": id_part,
                        "keyword": key
                    })
    
    return libraryId
            
def getContentInLibrary(driver, listIdBrary):
    contents = []

    for item in listIdBrary:
        link = f"https://www.facebook.com/ads/library/?id={item['library_id']}" 
        driver.get(link, e_wait=10)
        
        # lấy ra phạm vi lớn nhất của content
        modal = driver.find_element("xpath", "//div[@role='dialog' and @tabindex='-1']")
        print("modal: ", modal)
        # Đi vào thẻ div thứ 2
        scope = modal
        for _ in range(2):
            scope = scope.find_element("xpath", ".//div")
        # lấy ra thẻ div thứ 2 ở trong scope
        scope = scope.find_element("xpath", "./div[2]")
        # Tìm thẻ <hr> trong scope
        hr_element = scope.find_element("xpath", ".//hr")
        # Tìm thẻ <div> ngay dưới <hr>
        scope_content = hr_element.find_element("xpath", "./following-sibling::div")

        # lấy ra pange
        elementPange = scope_content.find_element("xpath", './/a[@target="_blank"]')
        linkpage = elementPange.get_attribute("href")
        namepage = elementPange.text
        
        # lấy ra nội dung quảng cáo
        elementContent = scope_content.find_element("xpath", ".//div[@role='button' and @tabindex='0']")
        content = elementContent.text
        
        # lấy ra video image
        scope_content_video_img = elementContent.find_element("xpath", "./ancestor::div[2]")

        images = scope_content_video_img.find_elements("xpath", ".//img")
        image_sources = [img.get_attribute("src") for img in images if img.get_attribute("src")]
        videos = scope_content_video_img.find_elements("xpath", ".//video")
        video_sources = [video.get_attribute("src") for video in videos if video.get_attribute("src")]
        
        # lưu lại dữ liệu và thực hiện công việc tiếp theo
        data = {
            "library_id": item["library_id"],
            "keyword": item["keyword"],
            'name_page': namepage,
            'link_page': linkpage,
            'content': content,
            'link': link,
            'image': image_sources,
            'video': video_sources,
        }
        
        contents.append(data)
        sleep(2)
    
    return contents

def stop_crawl_up(id):
    thread = farm_ads[id]['thread']
    thread.join()
    farm_ads[id]['check'] = 1
    del farm_ads[id]

def create_browser_link_spy_fb(driver, account, stop_event, tab):
    list_posts = []
    listId = set()
    tab['status'] = 'Room nhỏ màn hình!'
    print('Room small windown')
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
                                        # fb_id = extract_post_id(fb_link)
                                        list_posts.append({
                                            'account_id': account.get('id'),
                                            'fb_link': fb_link,
                                            'fb_id': '',
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
    print("duration",time.time() - start_time < duration )
    while time.time() - start_time < duration:
        # Tìm các bài viết
        posts = driver.find_elements(By.CSS_SELECTOR, "div[data-pagelet^='FeedUnit_']")
        for post in posts:
            try:
                # Cuộn đến bài viết
                driver.execute_script("arguments[0].scrollIntoView(true);", post)
                driver.random_delay(30, 60)
                # Tìm và click nút like
                print("Bắt đầu like bài viết")
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

