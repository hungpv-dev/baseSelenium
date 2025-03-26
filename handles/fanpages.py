from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from helpers import convert_to_db_format, clean_facebook_url_redirect, remove_params, is_valid_link, convert_shorthand_to_number

def dd(data):
    import json
    print(json.dumps(data, indent=4, ensure_ascii=False))

API_TOKEN_GEMINI = 'AIzaSyAOVpv0d5_KEkF4xXi1jhA0DTh2-CWQ1Iw'

def find_modal(driver, typeModalXpaths):
    """Tìm modal theo danh sách XPath."""
    for xpath in typeModalXpaths:
        modal = driver.find(xpath)
        if modal:
            return modal
    return None

def getContentPost(driver, p):
    removeDyamic = [
        'All reactions:',
        '',
    ]
    typeModalXpaths = [
        '//*[@role="dialog" and @aria-labelledby]',
        # '//*[@aria-posinset="1"]'
    ]
    selectDyamic = {
        'comment': 'comment',
        'share': 'share'
    }
    removeComment = [
        '·',
        'Author\n',
        '  ',
        'Top fan'
        'Follow',
    ]
    try:
        # Xử lý lấy content

        data = getWhySeeAds(driver, p)
        sleep(1)
        data = getShareLink(driver, p, data)

        driver.wait_and_click('.//*[@aria-label="Leave a comment"]', scope=p)
        sleep(5)

        # Tìm modal lần đầu
        modal = find_modal(driver, typeModalXpaths)
        
        if modal is None:
            driver.get(data.get('fb_link'), e_wait=3)
            modal = find_modal(driver, typeModalXpaths)

        # Xử lý modal
        if modal:
            aria_posinset = modal.get_attribute("aria-posinset")
            driver.closeModal(0 if aria_posinset else 2)
        else:
            raise Exception('Not found modal')

        sleep(1)
        dataComment = []
        sleep(2)


        timeUp = None
        try:
            linkTimeUp = WebDriverWait(modal, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//a[@attributionsrc]"))
            )
            if linkTimeUp:
                for link in linkTimeUp:
                    retry_count = 3 
                    while retry_count > 0:
                        try:
                            rect = link.rect
                            if rect['width'] > 0 and rect['height'] > 0:
                                href_text = link.text.strip()
                                cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', href_text)
                                formatted_time = convert_to_db_format(cleaned_text)
                                if formatted_time:
                                    timeUp = formatted_time
                            break  # Nếu thành công thì thoát vòng lặp
                        except Exception as e:
                            print(f"Error time up: {e}")
                            if "stale element" in str(e).lower():
                                print("Element is stale, re-locating...")
                                linkTimeUp = WebDriverWait(modal, 5).until(
                                    EC.presence_of_all_elements_located((By.XPATH, ".//a[@attributionsrc]"))
                                )
                                link = linkTimeUp[0]  # Lấy lại phần tử đầu tiên
                            else:
                                break 
                        retry_count -= 1
                        sleep(1)

        except Exception as ea:
            print("Error when get time up.")
        
        data['time_up'] = timeUp

        content, content_link = extract_facebook_content(modal, driver)
        print('Get Content')
        data['content'] = content
        data['content_link'] = content_link
        data['view'] = ''

        data['fb_post_link'] = data['fb_link']
        data['fb_video_link'] = ''


        # Lấy ảnh và video
        print('Get image and video')
        media = None
        try:
            media = modal.find_element(By.XPATH,'.//*[@data-ad-rendering-role="story_message"]/parent::div/following-sibling::div')
        except Exception:
            media = modal
            
        try:
            if 'medias' not in data:
                data['medias'] = {
                    'images': [],
                    'videos': [],
                    'ifames': [],
                } 
            images = media.find_elements(By.XPATH, './/img')
            for img in images:
                src = img.get_attribute('src')
                if src and src.startswith('http') and "emoji.php" not in src:
                    data['medias']['images'].append(img.get_attribute('src'))
                
            videos = media.find_elements(By.XPATH, './/video')
            for video in videos:
                data['medias']['videos'].append(video.get_attribute('src'))

            try:
                original_tab = driver.current_window_handle

                driver.execute_script("window.open('', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])  # Chuyển sang tab mới
                driver.get(data.get('fb_link'), e_wait=3)

                # Lấy URL hiện tại
                url_post = driver.current_url
                video_path = extract_video_path(url_post)

                # Tạo iframe
                match = re.search(r'/(videos|posts|reel)/(\d+)', url_post)
                if match:
                    data['fb_id'] = match.group(2)
            
                if '/videos/' in url_post:
                    data['fb_video_link'] = url_post
                    data['fb_post_link'] = url_post.replace('/videos/', '/posts/')
                elif '/posts/' in url_post:
                    data['fb_video_link'] = url_post.replace('/posts/', '/videos/')
                    data['fb_post_link'] = url_post
                elif 'reel' in url_post:
                    a = driver.find('//*[@aria-label="See Owner Profile"]')
                    if a:
                        href = a.get_attribute('href')
                        page_id = get_id_from_url(href)
                        if page_id:
                            video_path = f"{page_id}/videos/{data['fb_id']}"
                            data['fb_video_link'] = f"https://facebook.com/{video_path}"
                            data['fb_post_link'] = data['fb_video_link'].replace('/videos/', '/posts/')

                if len(data['medias']['videos']) > 0:
                    if '/videos/' not in url_post: 
                        driver.get(data['fb_video_link'], e_wait=3)
                    iframe = f'https://www.facebook.com/plugins/video.php?height=476&href=https://www.facebook.com/{video_path}'
                    data['medias']['ifames'].append(iframe)

                    print('Start get count views')
                    ditrictElemets = driver.find_all('//*[@aria-label="See who reacted to this"]/ancestor::div[3]')
                    for dictric in ditrictElemets:
                        textDictric = dictric.text.strip()
                        if textDictric:
                            listCount = textDictric.split('\n')
                            view = listCount[-1] if listCount else ''
                            data['view'] = view
                
                # Đóng tab hiện tại
                driver.close()
                driver.switch_to.window(original_tab)  # Quay lại tab gốc
            except Exception as e:
                print(f"Error when get info: {e}")
        except Exception as e:
            print(e)
            print(f'Post not image or video')

        try:
            data['like'] = ''
            data['comment'] = ''
            data['share'] = ''

            print('Start get dictrict')
            ditrictElemets = modal.find_elements(By.XPATH, './/*[@aria-label="See who reacted to this"]/ancestor::div[3]')
            for dictric in ditrictElemets:
                textDictric = dictric.text.strip()
                if textDictric:
                    for string in removeDyamic:
                        listCount = textDictric.replace(string, '')
                        listCount = listCount.split('\n')
                        if listCount:
                            data['like'] = listCount[1] if len(listCount) > 1 else 0
                            if data['like'] == 'Comment':
                                data['like'] = 0
                            for dyamic in listCount:
                                if selectDyamic['comment'] in dyamic:
                                    data['comment'] = dyamic
                                if selectDyamic['share'] in dyamic:
                                    data['share'] = dyamic
        except Exception as e:
            print(f"Khong lay duoc like, comment, share")
        
        data['like'] = convert_shorthand_to_number(data['like'])
        data['comment'] = convert_shorthand_to_number(data['comment'])
        data['share'] = convert_shorthand_to_number(data['share'])
        data['view'] = convert_shorthand_to_number(data['view'])

        

        # # Lấy comment
        # if modal == None:
        #     modal = driver
        # try:
        #     scroll = modal.find_element(By.XPATH, './div/div/div/div[2]')
        #     driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll)
        #     print('Cuộn chuột xuống')
        # except: 
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # sleep(3)
        # driver.randomSleep()
        
        try:
            comments = modal.find_elements(By.XPATH, ".//*[contains(@aria-label, 'Comment')]")
            
            # Click vào các từ xem thêm
            for cm in comments:
                # Xóa ảnh trùng trong danh sách data['media']['images']
                try:
                    imgs_in_comment = cm.find_elements(By.CSS_SELECTOR, 'img')
                    for img in imgs_in_comment:
                        src = img.get_attribute('src')
                        if src in data['medias']['images']:
                            data['medias']['images'].remove(src)
                except:
                    pass
                # Xóa video trùng trong danh sách data['media']['videos']
                try:
                    videos_in_comment = cm.find_elements(By.CSS_SELECTOR, 'video')
                    for video in videos_in_comment:
                        src = video.get_attribute('src')
                        if src in data['medias']['videos']:
                            data['medias']['videos'].remove(src)
                except:
                    pass

                try:
                    xem_them = cm.find_element(By.XPATH, ".//div[text()='See more']")
                    if xem_them:
                        driver.execute_script("arguments[0].click();", xem_them)
                except:
                    pass
            countComment = 0
            for cm in comments:
                if countComment >= 10:
                    break
                textComment = ''
                link_comment = []
                try:
                    div_elements = cm.find_elements(By.XPATH, './div')[1]
                    div_2 = div_elements.find_elements(By.XPATH, './div')
                    
                    
                    if not div_2 or not div_2[0]: 
                        continue
                    textComment = div_2[0].text
                    
                    try:
                        if len(div_2) > 1:
                            a_tags = div_2[1].find_elements(By.XPATH, './/a') 
                            if not a_tags:
                                a_tags = div_2[0].find_elements(By.XPATH, './/a')  
                        elif len(div_2) > 0:
                            a_tags = div_2[0].find_elements(By.XPATH, './/a')
                        else:
                            a_tags = []
                        for a in a_tags:
                            try:
                                img_element = None
                                try:
                                    img_element = a.find_element(By.XPATH, 'preceding-sibling::img') 
                                except:
                                    pass
                                
                                if img_element:
                                    print("Not tag a when get href.")
                                else:
                                    href = a.get_attribute('href')
                                    if href and is_valid_link(href) and href not in link_comment:
                                        link_comment.append(href)
                            except Exception as e:
                                print(f"Error when get href: {e}")
                    except IndexError as ie:
                        print(f"Error index: {ie}")
                    except Exception as e:
                        print(f"Error not found: {e}")
                        
                except:
                    countComment += 1
                    pass
                    
                for text in removeComment:
                    textComment = textComment.replace(text,'')

                textComment = textComment.strip()
                textArray = textComment.split('\n')

                if 'Top fan' in textComment:
                    user_name = textArray[1]
                    textContentComment = ' '.join(textArray[2:])
                else:
                    user_name = textArray[0]
                    textContentComment = ' '.join(textArray[1:])

                textContentComment = textContentComment.replace('Follow','').strip()
                
                if user_name == '' or textContentComment == '':
                    continue

                countComment += 1
                dataComment.append({
                    'user_name': user_name,
                    'content': textContentComment,
                    'link_comment': [clean_facebook_url_redirect(url) for url in link_comment],
                })
            # print(f"=> Lưu được {len(dataComment)} bình luận!")
        except Exception as e:
            print(e)
            print("Error when get comment!")


        try:
            images = data.get('medias').get('images')
            filtered_images = [
                img for img in images 
                if 'facebook_icons' not in img and 'facebook.com/images' not in img
            ]
            data['medias']['images'] = filtered_images
        except Exception as e:
            print(e)

        # print(data)
        merged_data = {
            "post": data,
            "comments": dataComment
        }
        return merged_data
    except Exception as e:
        print(f'Error when get content: {e}')
        return None

def extract_video_path(url):
    # Regex để bắt đoạn "page/videos/ID"
    match = re.search(r'([^/]+)/(videos|posts)/\d+', url)
    return match.group(0).replace('posts', 'videos') if match else None

def get_id_from_url(url: str) -> str:
    """Trích xuất giá trị của 'id' từ URL."""
    match = re.search(r"id=(\d+)", url)
    return match.group(1) if match else None

import pyperclip
def getWhySeeAds(driver, modal):
    data = {}
    reasons = []
    # Why am I seeing this ad?
    try:
        print('Start get reason me see post')
        driver.wait_and_click('.//*[@aria-label="Actions for this post"]', scope=modal)
        driver.wait_and_click('//*[text()="Why am I seeing this ad?"]', scope=modal)
        sleep(1)
        driver.wait_and_click('//*[contains(text(), "View who") or contains(text(), "wants to show ads to?")]', scope=modal)
        sleep(1)
        reasonsElements = driver.find_all('//*[@role="dialog"]/div/div[2]/div/div[4]/div[3]/div',wait=10)
        for rea in reasonsElements:
            if rea.text:
                reasons.append(rea.text.strip())

    except Exception as e:
        print(f"Error when get reason {e}")

    data['reasons'] = reasons
    print('Close modal')
    driver.closeModal(last=True)
    return data

def getShareLink(driver, p, data):
    try:
        driver.wait_and_click('.//*[@aria-label="Send this to friends or post it on your profile."]', scope=p)
        sleep(5)
        list = driver.find_all('//*[@role="list"]//*[@role="listitem"]',wait=10)
        for item in list:
            try:
                item_text = item.text.lower()
                if "copy link" in item_text:
                    item.click()
                    sleep(2)
                    break
            except Exception as e:
                print(f"Error when click copy: {e}")
        
        fb_link = pyperclip.paste()
        fb_id = extract_post_id(fb_link)
        data['fb_id'] = fb_id
        data['fb_link'] = fb_link
    except Exception as e:
        print(f"Error when get link post {e}")
    return data

def extract_post_id(url):
    patterns = [
        r'/(?:p|v)/([a-zA-Z0-9]+)',               # Dạng /p/ hoặc /v/
        r'/posts/([a-zA-Z0-9]+)',                 # Dạng /posts/{post_id}
        r'/(?:photo\.php|video\.php)\?v=([0-9]+)',  # Dạng photo.php?v=123456789
        r'/permalink\.php\?story_fbid=([0-9]+)',   # Dạng permalink.php?story_fbid=123456789
        r'/reel/([0-9]+)',                        # Dạng /reel/{post_id}
        r'/watch/\?v=([0-9]+)',                   # Dạng /watch?v={post_id}
        r'/story.php\?story_fbid=([0-9]+)',       # Dạng story.php?story_fbid={post_id}
        r'fb\.watch/([a-zA-Z0-9_-]+)/?'           # Dạng fb.watch/{id}
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ''


def extract_facebook_content(modal, driver):
    removeString = [
        '\n',
        '·',
        '  ',
        'See Translation',  # Xem bản dịch
        'See original',     # Xem bản gốc
        'Rate this translation'  # Xếp hạng bản dịch này
    ]

    try:
        try:
            seeMores = modal.find_elements(By.XPATH, ".//*[contains(text(), 'See more')]")
            for see in seeMores:
                try:
                    see.click()
                    sleep(3)
                except Exception as e:
                    continue
        except Exception as e:
            print(f'Click see more not success: {e}')
        
        content_link = []
        content = modal.find_element(By.XPATH, './/*[@data-ad-rendering-role="story_message"]')

        replace_content = []
        a_tags = content.find_elements(By.XPATH,'.//a')
        for a in a_tags:
            href = a.get_attribute('href')
            if href:
                clean_href = clean_facebook_url_redirect(href)
                clean_href = remove_params(clean_href, 'fbclid')
                text_link = a.text.strip()
                if text_link.startswith('http'):
                    content_link.append(clean_href)
                    replace_content.append({
                        'text': text_link,
                        'link': clean_href,
                    })

        contentText = content.text
        contentText = contentText.replace('See less','')
        
        for rep in replace_content:
            contentText = contentText.replace(rep.get('text'), rep.get('link'))

        for string in removeString:
            contentText = contentText.replace(string, '')
        return contentText.strip(), content_link
    except Exception as e:
        print(f'Not found content')
        return '', []
