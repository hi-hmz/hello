from selenium import webdriver
import re
import requests
import time
import os


# 获取影片url
def get_movie_url():
    global movie_name
    movie = input('请输入要查询的影片名:')
    driver = webdriver.Chrome()  # 创建一个Chrome浏览器的webdriver实例
    driver.get('https://movie.douban.com/')
    driver.find_element_by_id('inp-query').send_keys(movie)  # 找到输入框元素并输入要查询的影片
    driver.find_element_by_class_name('inp-btn').click()  # 点击搜索
    time.sleep(3)
    try:
        driver.find_element_by_class_name('cover-link').click()  # 点击搜索到的第一个结果
    except Exception:
        print('未搜索到影片', movie)
        driver.quit()
        return 'false'
    else:
        movie_name = driver.find_elements_by_tag_name('span')[3].text  # 影片名
        movie_info = driver.find_element_by_id('info').text  # 影片信息,导演 主演等
        movie_grade = driver.find_element_by_class_name('rating_num').text  # 影片的豆瓣评分
        movie_intro = driver.find_element_by_id('link-report').text  # 影片剧情简介
        movie_url = driver.current_url  # 获取当前网页地址
        driver.quit()
        print('为您搜索到以下内容:')
        print('影片名:', movie_name)
        print('豆瓣评分:', movie_grade)
        print(movie_info)
        print('剧情简介:')
        print(movie_intro)
        return movie_url


# 获取影片评论
def get_movie_comment(movie_url):
    url = movie_url + 'comments?start=0&limit=20&sort=new_score&status=P'
    response = requests.get(url, headers)
    if response.status_code == 200:
        pattern = '<span class="filter-name">(.+?)</span>'
        regex = re.compile(pattern)
        classification = regex.findall(response.text)  # 评论分类
        pattern = '<span class="comment-percent">(.+?)</span>'
        regex = re.compile(pattern)
        percent = regex.findall(response.text)  # 各评论分类百分比
        try:
            for j in range(1, 4):
                print(classification[j], ':', percent[j - 1])
        except Exception:
            print('该影片还未上映,暂无评价')
            return
    for i in range(11):
        url = movie_url + 'comments?start=%d&limit=20&sort=new_score&status=P' % (i * 20)
        response = requests.get(url, headers)
        if response.status_code == 200:
            pattern = 'class="">(.+?)</a>'
            regex = re.compile(pattern)
            user_list = regex.findall(response.text)
            pattern = '<span class="comment-time " title="(.+?)">'
            regex = re.compile(pattern)
            time_list = regex.findall(response.text)
            pattern = '<span class="short">(.+?)</span>'
            regex = re.compile(pattern)
            txt_list = regex.findall(response.text)
            print('----------------------以下是全部评论(别人的评论,仅供参考😃)---------------------------')
            for j in range(len(txt_list)):
                print('昵称:{}       评论时间:{}'.format(user_list[j], time_list[j]))
                print('评论内容:{}'.format(txt_list[j]))
                print()
        else:
            print('评论获取失败')
            print(response.status_code)


# 获取影片剧照
def get_movie_image(movie_url):
    url = movie_url + 'all_photos'
    response = requests.get(url, headers)
    if response.status_code == 200:
        pattern = '<img src="https://(.+?)">'
        regex = re.compile(pattern)
        img_list = regex.findall(response.text)
        if not os.path.exists('D:/%s剧照' % movie_name):
            os.makedirs('D:/%s剧照' % movie_name)
            for i in range(10):
                filename = os.path.basename(img_list[i])
                with open('D:/%s剧照/%s' % (movie_name, filename), 'wb') as f:
                    f.write(requests.get('https://' + img_list[i]).content)
            print('剧照获取成功,已存放至: D:/%s剧照' % movie_name)
        else:
            print('该影片剧照已存在,不能重复获取,图片存放位置为: D:/%s剧照' % movie_name)
    else:
        print('影片剧照获取失败')
        print(response.status_code)


def main():
    movie_url = get_movie_url()
    if movie_url != 'false':
        get_movie_comment(movie_url)
        get_movie_image(movie_url)


if __name__ == '__main__':
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    main()
