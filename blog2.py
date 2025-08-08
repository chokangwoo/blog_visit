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
import re
import pandas as pd
import tkinter as tk
from tkinter import ttk


import time
import blog_param2 as pa

#방문자수 카운트하는 함수
def get_visit_count(driver, wait):
    """나의활동 페이지에서 방문 횟수(숫자)만 추출"""
    try:
        # 방문 횟수 em 태그 대기
        em_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "em.gm-tcol-c"))
        )
        full_text = em_elem.text  # 예: "42회"
        # 숫자만 추출
        match = re.search(r"\d+", full_text)
        if match:
            visit_count = int(match.group())
            return visit_count
        else:
            print("방문 횟수를 찾지 못했습니다.")
            return None
    except Exception as e:
        print("방문 횟수 가져오기 실패:", e)
        return None



# 표로 보여주는 함수
def show_results_gui(results):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("카페 방문 현황")

    cols = ["카페명", "현재 방문 횟수", "필요 방문 횟수", "남은 방문 횟수", "상태"]
    tree = ttk.Treeview(root, columns=cols, show="headings", height=12)

    widths = [180, 130, 130, 140, 160]
    for i, c in enumerate(cols):
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=widths[i], stretch=True)

    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")

    tree.tag_configure("ok",   background="#e8f5e9")  # 충족
    tree.tag_configure("lack", background="#fff3e0")  # 부족
    tree.tag_configure("none", background="#ffebee")  # 미가입/기준 없음

    for r in results:
        status = r["상태"]
        tag = "ok" if status == "방문 횟수 충족" else ("lack" if status == "방문 횟수 부족" else "none")
        row = [
            str(r["카페명"]),
            str(r["현재 방문 횟수"]),
            str(r["필요 방문 횟수"]),
            str(r["남은 방문 횟수"]),
            str(r["상태"]),
        ]
        tree.insert("", "end", values=row, tags=(tag,))

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.minsize(780, 420)
    root.mainloop()



# 방문 평가하는 함수
def evaluate_visit(count, required):
    """
    count: 현재 방문 횟수(int | None)
    required: 필요 방문 횟수(int | None)
    return: status(str), remaining(str|int), required_display(str|int), current_display(str|int)
    """
    # 가입 안 된 경우
    if count is None:
        return "가입되지 않은 카페", "-", required if isinstance(required, int) else "-", "-"

    # 필요 기준이 없는 경우(키 불일치 등)
    if not isinstance(required, int):
        # 기준이 없으면 충족/부족 판단 자체를 안 함 → 남은 횟수 계산 불가
        return "기준 없음", "-", "-", count

    # 정상 계산
    remaining = max(required - count, 0)
    if count < required:
        status = "방문 횟수 부족"
    else:
        status = "방문 횟수 충족"
    return status, remaining, required, count



# login_cafe에서 방문 횟수 반환하도록 수정
def login_cafe(username, password, url):
    try:
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

        print(f"아이디: {username} 로그인 시도중")
        driver.get(url)
        wait.until(EC.element_to_be_clickable((By.ID, "gnb_login_button"))).click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.login_form")))

        id_field = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div#input_item_id > input.input_id")
        ))
        pw_field = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div#input_item_pw > input.input_pw")
        ))

        for elem in (id_field, pw_field):
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            time.sleep(0.2)
            elem.click()
            time.sleep(0.2)

        def js_set_value(elem, text):
            driver.execute_script("arguments[0].value = '';", elem)
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            """, elem, text)
            time.sleep(1)

        js_set_value(id_field, username)
        js_set_value(pw_field, password)

        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_login")))
        submit_btn.click()

        print(f"아이디: {username} 로그인 완료")
        try:
            my_activity_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//ul[contains(@class,'info-action-tab')]//button[normalize-space()='나의활동']")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", my_activity_btn)
            my_activity_btn.click()
            print("'나의활동' 버튼 클릭 완료")
        except Exception as e:
            print("'나의활동' 버튼 클릭 실패:", e)

        count = get_visit_count(driver, wait)
        print(f"현재 방문 횟수: {count}")
        time.sleep(2)

        return count   # 방문 횟수 반환

    except Exception as e:
        print("로그인 실패:", e)
        return None    # 실패 시 None 반환

    finally:
        if driver:
            driver.quit()



def all_login(blog_url, blog_info):
    results = []

    for name, url in blog_url.items():
        for username, password in blog_info.items():
            print(f"<{name} 블로그>")
            count = login_cafe(username, password, url)

            # BLOG_COUNT에서 필요 기준 가져오기 (없으면 None)
            required = pa.BLOG_COUNT.get(name, None)

            # 상태/남은 횟수 계산
            status, remaining, required_disp, current_disp = evaluate_visit(count, required)

            # 로그 출력(선택)
            if status == "가입되지 않은 카페":
                print(f"'{name}'은(는) 가입되지 않은 카페입니다.")
            elif status == "기준 없음":
                print(f"ℹ'{name}'은(는) 필요 방문 기준이 설정되어 있지 않습니다. (현재: {current_disp}회)")
            elif status == "방문 횟수 부족":
                print(f"'{name}' 부족: 현재 {current_disp}회 / 필요 {required_disp}회 / 남은 {remaining}회")
            else:
                print(f" '{name}' 충족: 현재 {current_disp}회 / 필요 {required_disp}회")

            # 표 데이터
            results.append({
                "카페명": name,
                "현재 방문 횟수": current_disp,     # int 또는 "-"
                "필요 방문 횟수": required_disp,    # int 또는 "-"
                "남은 방문 횟수": remaining,        # int 또는 "-"
                "상태": status
            })

    return results



if __name__ == "__main__":
    #창 닫기 모드  활성화(1), 비활성화(0)
    head = 1

    #모든 카페 방문 시작
    results=all_login(pa.BLOG_URL, pa.BLOG_INFO)
    show_results_gui(results)  # 마지막에 GUI로 보여주기



