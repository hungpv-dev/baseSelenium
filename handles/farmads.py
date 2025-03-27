from sql import profiles, posts
from managers import Driver
from .login import login
from time import sleep, time as time_time
from selenium.webdriver.common.by import  By
from stores import farm_ads
import pyperclip
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
            "Áo nam",
            "Wooden toys",
        ]
        try:
            tab['status'] = 'Đang khởi tạo trình duyệt....'
            driver = Driver(profile) # Khởi tạo
            
            tab['check'] = 1
            tab['status_process'] = 1
            tab['status'] = 'Đã khởi tạo trình duyệt'
    
            driver.get('https://facebook.com', e_wait=3)
            for keyword in keywords:
                print(keyword)
                driver.get(f"https://www.facebook.com/search/posts/?q={keyword}", e_wait=3)
                # search = driver.find('//input[@type="search"]', send_keys=keyword, clear=True, wait=5)
                # driver.enter(search)
                # sleep(10)
                get_first_ads(driver, account, stop_event)
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
    start_time = time_time()
    max_duration = 5 * 60
    while not stop_event.is_set():
        if time_time() - start_time >= max_duration:
            print("Browsered five munites")
            return
        
        listPosts = driver.find_all('[aria-posinset]','css')
        # listPosts = driver.find_all('[role="article"]','css')
        print(f'Count post get success: {len(listPosts)}')

        if len(listPosts) == 0:
            driver.execute_script("window.scrollBy(0, 300);")
            continue

        for p in listPosts:
            try:
                stt = p.get_attribute('aria-posinset')

                if stt in listId:
                    continue
                
                listId.add(stt)

                # driver.wait_and_click('.//*[@aria-label="Like"]', scope=p)

                isSponsored = checkAds(driver,p)

                if isSponsored == False:
                    sleep(2)
                    continue

                try:
                    data = getContentPost(driver, p)
                    data['post']['account_id'] = (account and account.get('id')) or 1
                    res = posts.create(data)
                    print(f"=> Res insert data: ")
                    dd(res)
                except Exception as e:
                    print(f'Error when get content: {e}')
                driver.closeModal(last=True)
            except Exception as e:
                print(e)
        driver.execute_script("window.scrollBy(0, 200);")
        driver.randomSleep(2, 3)
        
def checkAds(driver, p):
    actions_chains = driver.action_chains()
    # as_links = p.find_elements(By.CSS_SELECTOR, 'a[role="link"][target="_blank"]')
    as_links = p.find_elements(By.CSS_SELECTOR, 'a[role="link"][tabindex="0"]')
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

def stop_crawl_up(id):
    thread = farm_ads[id]['thread']
    thread.join()
    farm_ads[id]['check'] = 1
    del farm_ads[id]

