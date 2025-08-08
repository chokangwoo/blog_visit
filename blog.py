'''
실행 전에 해당 패키지를 터미널에 입력하고 엔터(다운로드)
pip install selenium webdriver-manager 
'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import blog_param as pa


#카페에 로그인하는 함수
def login_cafe(username, password, url):
    try:
        # 1.드라이버 & WebDriverWait 설정
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        if head == 1:
            options.add_argument('--headless')

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        wait = WebDriverWait(driver, 10)

        # 2.카페 페이지 열기 + 로그인 버튼 클릭
        print(f"아이디: {username} 로그인 시도중")
        driver.get(url)
        wait.until(EC.element_to_be_clickable((By.ID, "gnb_login_button"))).click()

        # 3.로그인 레이어 뜨기 대기
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.login_form")))

        # 4.ID/PW input 요소 찾기
        id_field = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div#input_item_id > input.input_id")
        ))
        pw_field = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div#input_item_pw > input.input_pw")
        ))

        # 5.화면 중앙 스크롤 & 포커스
        for elem in (id_field, pw_field):
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            time.sleep(0.2)
            elem.click()
            time.sleep(0.2)

        # 6.JS로 value 주입 & input 이벤트 발생
        def js_set_value(elem, text):
            driver.execute_script("arguments[0].value = '';", elem)
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            """, elem, text)
            time.sleep(1)

        js_set_value(id_field, username)
        js_set_value(pw_field, password)

        # 7.로그인 버튼 클릭
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_login")))
        submit_btn.click()

        # 8.로그인 완료 대기
        print(f"아이디: {username} 로그인 완료")
        time.sleep(10)


    except Exception as e:
        print("로그인 실패:", e)

    finally:
        if driver:
            driver.quit()



#모든 카페에 로그인하는 함수 
def all_login(blog_url, blog_info):
    for name, url in blog_url.items():
        for username, password in blog_info.items():
            print(f"<{name} 블로그>")
            login_cafe(username, password, url)



if __name__ == "__main__":
    #창 닫기 모드  활성화(1), 비활성화(0)
    head = 0

    #모든 카페 방문 시작
    all_login(pa.BLOG_URL, pa.BLOG_INFO)




