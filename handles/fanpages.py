from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from helpers import convert_to_db_format, clean_facebook_url_redirect, remove_params, is_valid_link, convert_shorthand_to_number

def getContentPost(driver, post):
    removeDyamic = [
        'All reactions:',
        '',
    ]
    typeModalXpaths = [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[2]/div/div/div/div',
        '//*[@role="dialog" and @aria-labelledby]',
        '//*[@aria-posinset="1"]'
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
        driver.get(post['fb_link'], e_wait=2)
        modal = None
        driver.randomSleep()
        for type in typeModalXpaths:
            modal = driver.find(type)
            if modal is not None:
                break
        if modal:
            aria_posinset = modal.get_attribute("aria-posinset")
            if aria_posinset is None:
                driver.closeModal(2)
            else:
                driver.closeModal(0)
        else: 
            print('Không thấy modal')
            # modal = driver
            # raise Exception('Không tìm thấy Modal')
        sleep(1)
        data = {
            'content': '',
            'account_id': post.get('account_id'),
            'fb_link': post["fb_link"],
            'fb_id': post["fb_id"],
            "comment": 0,
            "like": 0,
            "share": 0,
            'medias' : {
                'images': [],
                'videos': []
            },
        }
        dataComment = []
        sleep(2)

        timeUp = None
        try:
            print('Lấy time up')
            if modal is None:
                container = driver
            else:
                container = modal
            linkTimeUp = WebDriverWait(container, 5).until(
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
                                print(formatted_time)
                                if formatted_time:
                                    timeUp = formatted_time
                            break  # Nếu thành công thì thoát vòng lặp
                        except Exception as e:
                            print(f"Lỗi time up: {e}")
                            if "stale element" in str(e).lower():
                                print("Element is stale, re-locating...")
                                linkTimeUp = WebDriverWait(container, 5).until(
                                    EC.presence_of_all_elements_located((By.XPATH, ".//a[@attributionsrc]"))
                                )
                                link = linkTimeUp[0]  # Lấy lại phần tử đầu tiên
                            else:
                                break 
                        retry_count -= 1
                        sleep(1)

        except Exception as ea:
            print(f"Lỗi time up ngoài: {ea}")
            print("The element is stale and cannot be accessed.")
        
        data['time_up'] = timeUp
        print('Lấy content')
        content, content_link = extract_facebook_content(modal, driver)
        data['content'] = content
        data['content_link'] = content_link
        print(data)

        # Lấy ảnh và video
        print('Lấy hình ảnh')
        media = None
        try:
            media = modal.find_element(By.XPATH,'.//*[@data-ad-rendering-role="story_message"]/parent::div/following-sibling::div')
        except Exception:
            media = modal
            
        media = modal
        if modal == None:
            media = driver.find('//*[@role="main"]') 
        try:
            images = media.find_elements(By.XPATH, './/img')
            for img in images:
                src = img.get_attribute('src')
                if src and src.startswith('http') and "emoji.php" not in src:
                    data['medias']['images'].append(img.get_attribute('src'))
                
            videos = media.find_elements(By.XPATH, './/video')
            for video in videos:
                data['medias']['videos'].append(video.get_attribute('src'))
        except Exception as e:
            print(e)
            print(f'Bài viết k có ảnh hoặc video')

        try:
            if modal == None:
                like_share_element = driver.find('//*[@role="complementary"]/div/div/div/div/div/div[2]/div')
            else:
                like_share_element = modal.find_element(By.XPATH, './/*[@data-visualcompletion="ignore-dynamic"]/div/div/div/div')
            listCount = like_share_element.text
            for string in removeDyamic:
                listCount = listCount.replace(string, '')

            listCount = listCount.split('\n')
            filtered_list = [item for item in listCount if item.strip()] # Lại bỏ thằng rỗng
            def extract_number(text):
                match = re.search(r'[\d,.KM]+', text)  # Tìm số có thể có đơn vị K, M
                return match.group() if match else '0'

            # Gán giá trị
            if len(filtered_list) >= 1:
                data['like'] = extract_number(filtered_list[0])

            if len(filtered_list) >= 2:
                data['comment'] = extract_number(filtered_list[1])

            if len(filtered_list) >= 3:
                data['share'] = extract_number(filtered_list[2])
        except Exception as e:
            print(f"Không lấy được like, comment, share")
        
        data['like'] = convert_shorthand_to_number(data['like'])
        data['comment'] = convert_shorthand_to_number(data['comment'])
        data['share'] = convert_shorthand_to_number(data['share'])

        # Lấy comment
        if modal == None:
            modal = driver
        try:
            scroll = modal.find_element(By.XPATH, './div/div/div/div[2]')
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll)
            print('Cuộn chuột xuống')
        except: 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        driver.randomSleep()
        
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
                                    print("Thẻ <a> có thẻ <img> phía trước, không lấy href.")
                                else:
                                    href = a.get_attribute('href')
                                    if href and is_valid_link(href, post) and href not in link_comment:
                                        link_comment.append(href)
                            except Exception as e:
                                print(f"Lỗi khi lấy href: {e}")
                    except IndexError as ie:
                        print(f"Lỗi chỉ mục: {ie}")
                    except Exception as e:
                        print(f"Lỗi không xác định: {e}")
                        
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
            print(f"=> Lưu được {len(dataComment)} bình luận!")
        except Exception as e:
            print(e)
            print("Không lấy được bình luận!")


        try:
            images = data.get('medias').get('images')
            filtered_images = [img for img in images if 'facebook_icons' not in img]
            data['medias']['images'] = filtered_images
        except Exception as e:
            print(e)

        merged_data = {
            "post": data,
            "comments": dataComment
        }
        return merged_data
    except Exception as e:
        print(f'Lỗi khi lấy content: {e}')
        return None

def extract_facebook_content(modal, driver):
    removeString = [
        '\n',
        '·',
        '  ',
        'See Translation',  # Xem bản dịch
        'See original',     # Xem bản gốc
        'Rate this translation'  # Xếp hạng bản dịch này
    ]
    is_none = False
    if modal == None:
        is_none = True
        modal = driver.find('//*[@role="complementary"]') 

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
            print(f'Click see more không thành công: {e}')
        
        content_link = []
        if is_none: 
            content = modal.find_element(By.XPATH, "./div/div/div/div/div/div/div[3]")
        else:
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
        for rep in replace_content:
            contentText = contentText.replace(rep.get('text'), rep.get('link'))

        for string in removeString:
            contentText = contentText.replace(string, '')
        return contentText.strip(), content_link
    except Exception as e:
        print(f'Không tìm thấy nội dung')
        return '', []
