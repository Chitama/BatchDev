#coding:utf-8

import sys, codecs
#from HTMLParser import html.parser
from html.parser import HTMLParser
import requests
import json

''' 楽天 API操作用 '''
class RKAPISearch:

    # 楽天商品検索API リクエストURL
    apiURL = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20140222?"

    # jsonファイル書き出し用
    OutputData = []
    def CreateResultFile(self):
        if len(self.OutputData) > 0:
            with open('response.json','w') as j:
                json.dump(self.OutputData, j, sort_keys=True, indent=4,ensure_ascii=False)

    # キーワード検索
    def KeywordSearch(self,keyword):
        # applicationId 申請したIDを設定
        st_load = {
            "title": keyword.decode('shift_jis'),
            "applicationId": 00000000000000,
            "hits": 10
        }

        # 検索条件をセットし、APIにリクエスト
        r = requests.get(self.apiURL, params = st_load)
        # リクエスト応答をjsonで保持
        res = r.json()
        # 保持したjsonからデータを取得
        return self.doSearch(res)


    # 検索結果から情報を抜き出す
    def doSearch(self,res):
        paste = []
        itemList = []
        itemRecord = u"検索結果" + str(res['count']) + u"件" + "\n"

        # リクエスト結果の一覧を1件ずつ参照する
        for i in res['Items']:
            item = i["Item"]

            # 結果情報を保持
            contents = ResultData()
            contents.rsTitle = str(item['title'])     # タイトル
            contents.rsBrand = str(item['brand'])     # ブランド
            contents.rsPrice = str(item['itemPrice']) # 標準価格
            contents.rsReviewRate = str(item['reviewAverage'])  # レビュー平均点
            contents.rsReviewCount = str(item['reviewCount'])   # レビュー件数
            contents.rsItemCapt = str(item['itemCaption']) # 商品説明
            contents.rsItemURL = str(item['itemUrl'])      # 商品ページURL

            # リクエスト結果のURLから商品ページのレビューコメントを取得
            parser = ItemParser()
            r = requests.get(str(item['itemUrl']))#商品ページURLからhtml文取得
            parser.feed(r.text)#解析

            # レビューコメントを保持
            contents.rsReviewComments = parser.getResult()
            # レビューページURLを保持
            contents.rsReviewPage = parser.getReviewURL()
            # jsonファイル作成用のdictを作成
            record = {'title':contents.rsTitle,'brand':contents.rsBrand,
            'price':contents.rsPrice,'rvAverage':contents.rsReviewRate,
            'itemCaption':contents.rsItemCapt, 'ItemURL':contents.rsItemURL,
             'rvCount':contents.rsReviewCount, 'reviewPageURL':contents.rsReviewPage}

            if len(contents.rsReviewComments) > 0:
                idx = 0
                for txt in contents.rsReviewComments:
                    # keyTitle = 'rvTitle{index}'.format('index'=str(idx))
                    # keyComment = 'rvComment{index}'.format('index' = str(idx))
                    keyTitle = 'rvTitle%d'  % idx
                    keyComment = 'rvComment%d' % (idx - 1)
                    if idx % 2 == 1:
                        record[keyComment] = contents.rsReviewComments[idx]
                    else:
                        record[keyTitle] = contents.rsReviewComments[idx]
                    idx = idx + 1
            else:
                record['rvComment'] = ""

            paste.append(record)
            itemList.append(contents)


        self.OutputData = paste
        return itemList

# 検索結果情報1件分のデータ格納クラス
class ResultData:
    rsTitle = u""
    rsBrand = u""
    rsIsbn = u""
    rsPrice = u""
    rsItemCapt = u""
    rsItemURL = u""
    rsReviewRate = ""
    rsReviewCount = ""
    rsReviewPage = u""
    rsReviewComments = []

# html文からレビューコメント属性を参照しコメントだけ抜き出すクラス
class ItemParser(HTMLParser):
    resultContents = []
    resultURL = u""

    def __init__(self):
        HTMLParser.__init__(self)
        self.istake = False
        self.rvcount = 0

        self.revUrlTake = False
        self.reviewUrl = u""
        self.revTitleTake = False

    # レビュー取得（複数）
    def getResult(self):
        return self.resultContents
    def getReviewURL(self):
        return self.resultURL
    # htmlタグの始めをみつけたら
    def handle_starttag(self, tag, attrs):
        self.istake = False

        # 楽天のページのレビュー:description class属性の<p>タグ内
        if tag == 'p':
            attrs = dict(attrs)
            if 'class' in attrs:
                if attrs['class'] == 'description':
                    #print("START  :", data)
                    self.istake = True
                    self.rvcount = self.rvcount + 1
        elif tag == 'a':
            attrs = dict(attrs)
            if 'href' in attrs:
                if 'review.rakuten.co.jp/item' in attrs['href']:
                    self.resultURL = attrs['href']
                    #print(attrs['href'])
        elif tag == 'div':
            attrs = dict(attrs)
            if 'class' in attrs:
                if attrs['class'] == 'review-title':
                    self.revTitleTake = True
                elif attrs['class'] == 'review-title notitle':
                    self.resultContents.append(u"no title")

    def handle_data(self, data):
        if self.istake:
            if data != "None":
                self.resultContents.append(data)
            self.istake = False
        elif self.revTitleTake:
            if data != "None":
                self.resultContents.append(data)
            self.revTitleTake = False
