# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from aip import AipOcr
import base64
from bs4 import BeautifulSoup
import urllib, urllib2
import re
from datetime import datetime


# Baidu OCR
BAIDU_OCR_APP_ID = '10679672'
BAIDU_OCR_API_KEY = '0YFQ4k5Vr7o2HBpgEh1fNTdY'
BAIDU_OCR_SECRET_KEY = 'NRbjByifNGGQmLyY3EcoyWV0Af5VwAuX'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render
from rest_framework.views import APIView
from dss.Serializer import serializer
from django.http import HttpResponse, HttpRequest


def response_as_json(data, foreign_penetrate=False):
    jsonString = serializer(data=data, output_type="json", foreign=foreign_penetrate)
    response = HttpResponse(
            # json.dumps(dataa, cls=MyEncoder),
            jsonString,
            content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200, foreign_penetrate=False, **kwargs):
    data = {
        "code": code,
        "msg": "成功",
        "data": data,
    }
    return response_as_json(data, foreign_penetrate=foreign_penetrate)


def json_error(error_string="", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)

JsonResponse = json_response
JsonError = json_error


class ReturnJson(APIView):
    def get(self, request, *args, **kwargs):
        # print datetime.now()
        width = 640
        imgurl = request.GET.get('imgurl', '') + '?imageView2/3/w/%s/' % (width)
        question, answers = find_q_and_a(imgurl, width)
        print 'answers', answers
        # print datetime.now()
        content1 = baidu(question)
        content2 = sogou(question)
        content = content1 + content2
        text = format(content=content)
        # print datetime.now()
        results = []
        print '============================================='
        print 'question:', question
        print '---------------------------------------------'
        for a in answers:
            dict = {}
            dict['answer'] = a
            dict['count'] = text.count(a)
            print a,'    ',dict['count']
            results.append(dict)
        print '============================================='
        # print datetime.now()
        return JsonResponse(results)


def find_q_and_a(img_url, img_width):
    client = AipOcr(BAIDU_OCR_APP_ID, BAIDU_OCR_API_KEY, BAIDU_OCR_SECRET_KEY)
    # result = client.general(f_b)
    result = client.generalUrl(img_url)
    if result.get('error_code', None):
        result = client.generalUrl(img_url)
    print result
    words = result['words_result']
    question = ''
    answers = []
    for w in words:
        location = w.get('location', None)
        if location:
            top = location.get('top', 0)
            left = location.get('left', 0)
            if top < 150*img_width/640:
                continue
            elif top < 300*img_width/640:
                question += w['words']
            elif top < 700*img_width/640 and left < 150*img_width/640:
                a = w['words']
                if a.startswith('A') or a.startswith('B') or a.startswith('C'):
                    a = a[2:]
                answers.append(a)
    return (question, answers)


def baidu(question):
    url = 'http://www.baidu.com/s?wd=%s' % (urllib.quote(question.strip().decode(sys.stdin.encoding).encode('gbk')))
    opener = urllib2.build_opener(urllib2.ProxyHandler({}))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64)")]
    urllib2.install_opener(opener)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request, timeout=5)
    if response.getcode() != 200:
        return None

    content = response.read()
    return content


def sogou(question):
    url = 'https://www.sogou.com/web?query=%s' % (urllib.quote(question.strip().decode(sys.stdin.encoding).encode('gbk')))
    opener = urllib2.build_opener(urllib2.ProxyHandler({}))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64)")]
    urllib2.install_opener(opener)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request, timeout=5)
    if response.getcode() != 200:
        return None

    content = response.read()
    return content


def format(content):
    dr = re.compile(r'<[^>]+>', re.S)
    cop = re.compile("[^\u4e00-\u9fa50-9]")
    dd = dr.sub('', content)
    text = cop.sub('', dd)
    return text
