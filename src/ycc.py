from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import random
from webdriver_manager.chrome import ChromeDriverManager

class YoutubeCommentCrawler:
    def __init__(self):
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        
    def open_video(self, url):
        self.browser.get(url)
        time.sleep(2)  # 페이지 로딩 대기
        self.browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(6)  # 동적 로딩 대기
    
    def scroll_to_load_comments(self):
        last_height = self.browser.execute_script("return document.documentElement.scrollHeight")
        while True:
            self.browser.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(random.uniform(1.5, 3.0))  # 로딩과 다양성을 위해 랜덤 대기 시간 적용
            new_height = self.browser.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def scrape_comments(self):
        comments = self.browser.find_elements(By.XPATH, '//*[@id="content-text"]')
        usernames = self.browser.find_elements(By.XPATH, '//*[@id="author-text"]')
        likes = self.browser.find_elements(By.XPATH, '//*[contains(@id, "vote-count-middle")]')
        
        data = {
            'username': [username.text for username in usernames],
            'comment': [comment.text for comment in comments],
            'likes': [like.text if like.text != '' else '0' for like in likes],
        }
        
        return pd.DataFrame(data)
    
    def close_browser(self):
        self.browser.quit()

# Example usage:
if __name__ == "__main__":
    # 1. 클래스 인스턴스 생성
    crawler = YoutubeCommentCrawler()

    # 2. 유튜브 비디오 열기
    url = "https://www.youtube.com/watch?v=Sq9DmUBdQMs"
    crawler.open_video(url)

    # 3. 댓글을 스크롤하여 로드
    crawler.scroll_to_load_comments()

    # 4. 댓글 스크랩
    df = crawler.scrape_comments()

    # 5. 브라우저 닫기
    crawler.close_browser()

    # 6. 결과 출력
    print(df)