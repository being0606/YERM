import random
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# TODO: argparse로 수정
URL = "https://www.youtube.com/watch?v=Sq9DmUBdQMs"


# 웹드라이버 설정
browser = webdriver.Chrome()
browser.get(URL)  # 유튜브 비디오 URL 입력

time.sleep(2)  # 페이지 로딩 대기

# 댓글 섹션까지 스크롤
browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
time.sleep(6)  # 동적 로딩 대기

# 스크롤 다운하여 모든 댓글 로드 
# TODO: 스크롤 함수와 종료조건 함수로 분할
last_height = browser.execute_script("return document.documentElement.scrollHeight")
while True:
    browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(random.uniform(1.5, 3.0))  # 로딩과 다양성을 위해 랜덤 대기 시간 적용
    new_height = browser.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    


# 댓글 요소 수집
# TODO: 함수로 분리
comments = browser.find_elements(By.XPATH, '//*[@id="content-text"]')
usernames = browser.find_elements(By.XPATH, '//*[@id="author-text"]')
n_likes = browser.find_elements(By.XPATH, '//*[contains(@id, "vote-count-middle")]')
author_elements = browser.find_elements(By.CSS_SELECTOR, "#author-text .yt-simple-endpoint.style-scope.ytd-comment-view-model")
time_elements = browser.find_elements(By.CSS_SELECTOR, "#published-time-text .yt-simple-endpoint.style-scope.ytd-comment-view-model")

# DataFrame 생성
# TODO: 함수로 분리
data = {
    'usernames': [username.text for username in usernames],
    'n_likes': [like.text if like.text != '' else '0' for like in n_likes],
    'times' : [element.text.strip() for element in time_elements],
    'comment': [comment.text for comment in comments],
    # 'reply_counts' : [element.text.strip() for element in reply_count_elements]
}

df = pd.DataFrame(data)
df['comment'] = df['comment'].str.replace('[^가-힣]', ' ', regex = True) # 댓글 전처리
df['comment']

# DataFrame 확인
print(df)