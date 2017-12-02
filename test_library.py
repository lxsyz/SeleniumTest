# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import random
import json
import datetime
import requests
from bs4 import BeautifulSoup

from xml import etree
# from importlib import reload
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# reload(sys)
# sys.setdefaultencoding("utf-8")

_username = '2017282160045'
_password = '193211'
browser = webdriver.Chrome()


def login(username_, password_, ):
    url = 'http://seat.lib.whu.edu.cn/login'

    browser.get(url)
    time.sleep(5)

    # # 输入用户名,密码
    username = browser.find_element_by_xpath('//input[@name="username"]')
    password = browser.find_element_by_xpath('//input[@name="password"]')
    captcha = browser.find_element_by_xpath('//input[@name="captcha"]')
    username.clear()
    username.send_keys(username_)
    password.clear()
    password.send_keys(password_)
    captcha.clear()

    verify_code_ = input('verify_code > ')
    print(verify_code_)
    captcha.send_keys(verify_code_)



    # 提交登陆
    sub_btn = browser.find_element_by_xpath('//input[@class="btn1"]')
    sub_btn.click()
    time.sleep(5)
    print('登陆完成')
    cookies = browser.get_cookies()

    cookie = [item["name"] + "=" + item["value"] for item in cookies]
    cookiestr = '; '.join(item for item in cookie)
    print(cookiestr)
    headers = {'cookie': cookiestr}
    return headers


def choose_seat():
    '''
    选择常用座位
    :return: 
    '''
    # 是否循环重新选座
    looping = True

    # 获取cookie
    headers = login(_username, _password)
    # 进入常用座位
    often_seat = browser.find_element_by_xpath('//a[@href="/freeBook/fav"]')
    often_seat.click()
    # 网页源码
    html_doc = browser.page_source
    soup = BeautifulSoup(html_doc, 'html.parser', from_encoding='utf-8')

    # 获得常用座位列表
    all_seats = soup.find_all("div", id="seats")
    seat_num = ""

    # todo 这里暂时只是做了选常用的第一个座位做测试，后面应该考虑座位是否占用，选后面的座位等
    for seat in all_seats:
        # print(seat)
        seat_num = seat.find("li").attrs['id']
        print(seat_num)
    if seat_num != "":
        string = '//li[@id="' + seat_num + '"]'
    print("seat_num is ", seat_num)

    # 前提是有常用座位
    seat_number = browser.find_element_by_xpath(string)
    seat_number.click()
    time.sleep(5)
    # 时间选择页面
    time_html_doc = browser.page_source
    soup = BeautifulSoup(time_html_doc, 'html.parser', from_encoding='utf-8')

    # 开始循环抢座位
    while looping:
        ul = soup.find_all("ul")[4]
        if ul is not None:
            print(ul)
            print("################")
            li_list = ul.find_all("a")
            if li_list is None or len(li_list) == 0:
                print("sorry no start time to choose")
                looping = True
            else:
                start_time = li_list[0].attrs['time']

                # 选择开始时间
                temp = '//a[@time="' + start_time + '"]'
                start_btn = browser.find_element_by_xpath(temp)
                start_btn.click()

                # print(seat_num[5:])

                # 再选择结束时间
                endtime_html = requests.post('http://seat.lib.whu.edu.cn/freeBook/ajaxGetEndTime', data={
                    'start': start_time,
                    'seat': seat_num[5:]
                }, headers=headers)

                soup = BeautifulSoup(endtime_html.content, 'html.parser', from_encoding='utf-8')
                a = soup.find_all("a")

                if a is None or len(a) == 0:
                    print("sorry no end time to choose")
                    looping = True
                else:
                    end_time = a[len(a) - 1].attrs['time']


                    # 选择时间处的验证码
                    another_captcha = browser.find_element_by_xpath('//input[@id="captchaValue"]')
                    verify_code = input("choose time captcha > ")
                    another_captcha.send_keys(verify_code)

                    response = requests.post('http://seat.lib.whu.edu.cn/selfRes', data={'seat':seat_num[5:],
                                                'start':start_time,
                                                'end':end_time,
                                                'captcha':verify_code},
                                             headers=headers)
                    if response.status_code == 200:
                        looping = False
                        print('预约成功')

                # # 点击预约按钮
                # sure_btn = browser.find_element_by_xpath('//a[@id="reserveBtn"]')
                # sure_btn.click()
        else:
            print("no start time to choose")


if __name__ == '__main__':
    choose_seat()

    # endtime_html = requests.post('http://seat.lib.whu.edu.cn/freeBook/ajaxGetEndTime', data={
    #     'start': '1320',
    #     'seat': '8765'
    # }, headers={'cookie': 'JSESSIONID=AF445FEC57E8CC47EC51272C13BE3636'})
    # print(endtime_html.content)
    # html = ''
    # with open('1.html', 'r', encoding='utf-8') as f:
    #     html = f.read()
    # soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    # ul = soup.find_all("ul")[4]
    # print(ul)
    # if ul is not None:
    #     print("sad")
    # print("################")
    # li_list = ul.find_all("a")
    # print(li_list)
    # for i in li_list:
    #     print(i.attrs['time'])
    #
    # end_ul = soup.find("ul", id="endTimeCotent")
    # print(end_ul)
    # a = end_ul.find_all("a")
    # if a is None or len(a) == 0:
    #     print(a)