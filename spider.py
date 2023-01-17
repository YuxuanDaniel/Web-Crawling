import requests
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import time
import json
from lxml import etree
import cv2
import os
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np

store_urls = []
store_video = []

def Image_download(path,url):
    data = requests.get(url).content
    while True:
        time.sleep(0.2)
        if len(data)>5:
            break
    with open(path,"wb") as f:
        f.write(data)

# Turn pictures to Black White
def canny(img):
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.Canny(img, 50, 150)

# Calculating how long captcha need to travel
def distance():
    img_small = cv2.imread("small.png", 0)
    img_big = cv2.imread("big.jpeg", 0)
    img_small = cv2.resize(img_small,(271,271))
    img_big = cv2.resize(img_big,(1360,848))
    result_small =canny(img_small)
    result_big =canny(img_big)
    res = cv2.matchTemplate(result_small, result_big, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    data = max_loc[0]
    w, h = img_small.shape[::-1]
    w1, h1 = img_big.shape[::-1]
    data += w/2
    data = (data/w1)*271     
    data += (data-135.5)*0.3  
    data = round(data,1)     
    data +=6
    return data

# Monitor human slide Captcha
def get_track(distance):
    track = []
    current = 0
    mid = distance * 4 / 5
    t = 0.5  
    v = 0 
    while current < distance:
        if current < mid:
            a = 6
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        if current > distance:
            current = current - move
            move = distance - current
            current += move
        track.append(move)
    return track

def get_home_ulrs(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-logging"])
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_argument("--headless")
    options.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    browser.get(url)

    with open('douyin_cookies.txt','r') as f:
        cookies_list = json.load(f)
        for cookie in cookies_list:
            browser.add_cookie(cookie)
    browser.refresh()
    time.sleep(2)

    for i in range(7):
        js = 'window.scrollTo(0,document.body.scrollHeight)'
        browser.execute_script(js)
        time.sleep(1)
    first_half = '//*[@id="dark"]/div[2]/div/div[3]/div[2]/ul/li['
    last_half = ']/div/a'
    # first_half ='//*[@id="douyin-right-container"]/div[2]/div/div[3]/div[2]/ul/li['
    # last_half =']/div/a'
    for i in range(100):
        path = first_half + str(i+1)+ last_half
        video_player = browser.find_elements(By.XPATH, path)
        print(i)
        final=video_player[0].get_attribute('href')
        store_urls.append(final)
    browser.close()
    print('length:',len(store_urls))
    return store_urls

def get_video(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-logging","enable-automation"])
    options.add_argument("--headless")
    options.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    browser.get(url)
    with open('douyin_cookies.txt','r') as f:
        cookies_list = json.load(f)
        for cookie in cookies_list:
            browser.add_cookie(cookie)
    browser.refresh()
    browser.maximize_window()

    try:
        data = browser.find_element(By.CLASS_NAME,"captcha_verify_img--wrapper").find_elements(By.TAG_NAME,"img")
        if len(data) != 0:
            while True:
                data = browser.find_element(By.CLASS_NAME,"captcha_verify_img--wrapper").find_elements(By.TAG_NAME,"img")
                url_a = data[0].get_attribute("src")
                url_b = data[1].get_attribute("src")
                Image_download('big.jpeg', url_a)
                Image_download('small.png', url_b)
                data = distance()
                tracks = get_track(data)
                tracks.reverse()
                actions = ActionChains(browser)
                move_btn = browser.find_element(By.CLASS_NAME,'secsdk-captcha-drag-icon')
                actions.move_to_element(move_btn)
                actions.click_and_hold(on_element=move_btn).perform()
                for x in tracks:
                    actions.move_by_offset(xoffset=x, yoffset=0).perform()
                time.sleep(0.5)
                actions.release(on_element=move_btn).perform()
                time.sleep(2)
                html = browser.find_elements(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div/div/div[1]/div[2]/div/xg-video-container/video/source')
                if len(html) != 0:
                    break
        html = browser.find_elements(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div/div/div[1]/div[2]/div/xg-video-container/video/source')
        for link in html:
            video = link.get_attribute('src')
            store_video.append(video)
            print('Currently getting {} video URL:'.format(len(store_video)),link.get_attribute('src'))
            break
        browser.close()
        return 1
    except:
        html = browser.find_elements(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div/div/div[1]/div[2]/div/xg-video-container/video/source')
        for link in html:
            video = link.get_attribute('src')
            store_video.append(video)
            print('Currently getting {} video URL:'.format(len(store_video)),link.get_attribute('src'))
            break
        browser.close()
        return 1

if __name__ == '__main__':
    print('Getting Video URL')
    url = 'https://www.douyin.com/search/%E8%88%AA%E6%8B%8D%E5%86%9B%E8%AE%AD?aid=a926aca1-c6e8-4b71-afa8-f49e470e135a&publish_time=0&sem_keyword=douyinwangye&sort_type=0&source=normal_search&type=video&ug_source=sem_sogou'
    get_home_ulrs(url)
    for link in store_urls:
        get_video(link)
    video_link=np.array(store_video)
    np.save('video_link.npy',video_link)
    print('Save Successfully')
        