from sql import profiles, posts
from managers import Driver
from .login import login
from time import sleep
from selenium.webdriver.common.by import By
from stores import crawl_ads
import pyperclip
import re

def start_crawl_up(id):
    from handles import getContentPost
    tab = crawl_ads[id]
    profile = profiles.show(id)

    if not tab or not profile:
        return
    
    stop_event = tab['stop_event']
    tab['status'] = 'Bắt đầu khời tạo trình duyệt'
    account = profile.get('account')
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
                tab['status'] == 'Tài khoản hiện không thể login, thử lại sau 15p',
                sleep(900)
                continue

            # Lấy danh sách bài viết
            try:
                import json
                post_list = create_browser_link_spy_fb(driver, account, stop_event, tab)
                for p in post_list:
                    try:
                        data = getContentPost(driver, p)
                        print(json.dumps(data, indent=4))
                        res = posts.create(data)
                        print(f'Res: {res}')
                        tab['status'] = 'Đã thêm dữ liệu!'
                        print(f'======================================')
                    except Exception as e:
                        print(f'Lỗi khi thêm bài viết: {e}')
                driver.get('https://facebook.com', e_wait=2)
                driver.clickOk()
                sleep(1)
            except RuntimeError as e:
                tab['status'] = f"Lỗi: {e}"
                print(f'Lỗi khi cào bài viết: {e}')
                sleep(300)

    except Exception as e:
        tab['status'] = 'Đã xảy ra lỗi....'
        print(f"Đã có lỗi xảy ra: {e}")
    finally:
        tab['status'] = 'Đang đóng....'
        driver.quit()
        print('Trình duyệt đã bị đóng')

def stop_crawl_up(id):
    thread = crawl_ads[id]['thread']
    thread.join()
    crawl_ads[id]['check'] = 1
    del crawl_ads[id]

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
                                print(f"==> {href}")
                                try:
                                    share = p.find_element(By.XPATH, './/*[@aria-label="Send this to friends or post it on your profile."]')
                                    actions.move_to_element(share).perform()
                                    share.click()
                                    sleep(3)
                                    parent_element = driver.find_element(By.XPATH, ".//*[@aria-label='List of available \"share to\" options in the unified share sheet.']")
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
                                    if len(list_posts) >= 5:
                                        print('Đã thu thập đủ 5 bài viết, trả về danh sách.')
                                        return list_posts
                                except Exception as e:
                                    print(f'Lỗi click share {stt}: {e}')
                                break
            except Exception as e:
                print(e)
        driver.randomSleep()
        tab['status'] = 'Cuộn chuột xuống!'
        driver.execute_script("window.scrollBy(0, 200);")
        sleep(5)