import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 파일의 저장명 변경을 위해 크롤링 하는 작품의 제목을 적어주자
Novel_Title = '서녀공략'  

# 네이버 시리즈의 웹소설 중 크롤링이 하고 싶은 페이지 링크를 복사해서 붙여넣는다.
# 이 코드의 경우, 베스트가 아닌 전체 댓글을 기준으로 하고 댓글의 댓글은 제외되어 있다.
base_url = 'https://series.naver.com/novel/detail.series?productNo=5107316' 

def collect_data(url):
    service = Service('C:/c-d/chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(3)
    driver.get(url)
    time.sleep(3) 
    try:
        all_comments_tab = driver.find_element(By.XPATH, "//span[contains(text(), '전체댓글')]")
        all_comments_tab.click()
        time.sleep(3) 
    except Exception as e:
        print("Failed to find or click '전체댓글' tab:", e)
        driver.quit()
        return None
    comments = []
    current_page = 1
    while True:
        if current_page > 1:
            try:
                next_page = driver.find_element(By.XPATH, f"//span[@class='u_cbox_num_page' and text()='{current_page}']")
                next_page.click()
                time.sleep(2)
            except Exception as e:
                print(f"Failed to navigate to page {current_page}:", e)
                break
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        content_wrap = soup.find('div', class_='u_cbox_content_wrap')
        if content_wrap is None:
            print("Failed to find comment container element.")
            break
        cmtList = content_wrap.find_all('li')
        for element in cmtList:
            name_element = element.find('span', class_='u_cbox_nick')
            review_element = element.find('span', class_='u_cbox_contents')
            date_element = element.find('span', class_='u_cbox_date')
            if name_element is None or review_element is None or date_element is None:
                print("Failed to extract comment information from element.")
                continue
            name = name_element.text
            review = review_element.text
            date = date_element.text
            comment = {'Name': name, 'Review': review, 'Date': date}
            comments.append(comment)
        current_page += 1
        if current_page % 5 == 1 and current_page != 1:
            try:
                next_button = driver.find_element(By.XPATH, "//span[@class='u_cbox_cnt_page' and contains(text(), '다음')]")
                next_button.click()
                time.sleep(2) 
            except Exception as e:
                print("Failed to find or click 'Next' button:", e)
                break
    data = pd.DataFrame(comments)
    driver.quit()
    return data
collected_data = collect_data(base_url)
if collected_data is not None:
    print('데이터 수집 완료')
    file_path = os.path.join(os.getcwd(), f'{Novel_Title}-Total_collected_data.xlsx')
    collected_data.to_excel(file_path, index=False)
    print(f'데이터가 {file_path} 파일로 저장되었습니다.')
else:
    print('데이터 수집 실패')
