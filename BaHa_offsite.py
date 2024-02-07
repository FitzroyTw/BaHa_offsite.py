import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np

headers = {
    'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


def login_with_captcha(userid, password, url='https://user.gamer.com.tw/login.php'):
    driver = webdriver.Chrome()
    driver.get(url)
    user_id = driver.find_element(By.NAME, 'userid')
    user_id.send_keys(userid)
    user_password = driver.find_element(By.NAME, 'password')
    user_password.send_keys(password)
    input("請解決機器人驗證後按 Enter 鍵繼續...")
    # 抓取 cookies
    cookies = driver.get_cookies()
    driver.quit()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session


def offsite():
    session = login_with_captcha('your id', 'your password')
    while True:
        try:
            url = 'https://forum.gamer.com.tw/B.php?bsn=60076'
            response = session.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            sel = soup.select("div.b-list__tile p")
            count = 0
            bsn = url.split('bsn=')[1]
            bsn = bsn.split('&')[0]
            for i in sel:
                count += 1
                print(f'{count}.{i.text}')
            try:
                choice = int(input(f'請輸入要查看的文章編號(1~{count})：'))
                print('------------------------------------')
                if 0 < choice <= len(sel):
                    url = sel[choice - 1]['href']
                    full_url = f'https://forum.gamer.com.tw/{url}'
                    r = session.get(full_url, headers=headers)
                    soup = BeautifulSoup(r.text, "html.parser")
                    title = soup.select_one('h1.c-post__header__title').text
                    print("標題:" + title)
                    reply_blocks = soup.select('section[id^="post"]')
                else:
                    print("超過範圍! 重新輸入")
                    continue
            except:
                print("請輸入有效的數字。")
                continue
            for reply_block in reply_blocks:
                floor = reply_block.select_one('div.c-post__header__author a').get('data-floor')
                user_name = reply_block.select_one('div.c-post__header__author a.username').text
                user_id = reply_block.select_one('div.c-post__header__author a.userid').text
                content = reply_block.select_one('div.c-article__content')
                for br_tag in content.find_all('br'):
                    br_tag.replace_with('\n')
                if content.select('a.photoswipe-image'):
                    for a_tag in content.select('a.photoswipe-image'):
                        image = a_tag.get('href')
                        print(image)
                article_time = reply_block.select_one('div.c-post__header__info a.edittime').get('data-mtime')
                text = content.text
                reply_id = reply_block.get('id')[-8:]
                print(floor + '.' + user_name + '  id:' + user_id + '  發文時間:' + article_time)
                print("文章內容:")
                print(text.strip())
                reply_url = f'https://forum.gamer.com.tw/ajax/moreCommend.php?bsn={bsn}&snB={reply_id}'
                r1 = session.get(reply_url, headers=headers)
                json = r1.json()
                commends = []
                for key, value in json.items():
                    # 判斷是否是數字(commend)，排除"next_snC"
                    if key.isdigit():
                        commends.append('內容:' + value['content'])  # 使用.get 如果沒有的話會顯示none 而直接用['']沒有這東西的話會報錯
                        if value.get('nick'):
                            commends.append('名字:' + value['nick'])
                        else:
                            commends.append('名字: None')
                        commends.append('帳號:' + value.get('userid'))
                        commends.append(value.get('time'))
                        commends.append(value.get('floor'))
                commends = commends[::-1]  # reverse
                print(" ")
                print("底下留言:")
                commends = np.array(commends).reshape(-1, 5)
                print(commends)
                print("-----------".strip())
            input('任意鍵返回')
        except requests.RequestException as e:
            print(f"發生錯誤: {e}")

