from bottlenose import api
from urllib.request import urlopen
from bs4 import BeautifulSoup
from numpy.lib.financial import rate
import pandas as pd

''' Amazon API操作用 '''
class AmazonAPI:
    # 初期化
    def __init__(self):

        # 申請したIDを設定
        # Amazon APIを利用するためのID情報
        AMAZON_ACCESS_KEY_ID = ""
        AMAZON_SECRET_KEY = ""
        AMAZON_ASSOC_TAG = ""
        # Amazonアクセス
        self.amazon = api.Amazon(AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, Region="JP")

    # http: // www.ajaxtower.jp / ecs / itemsearch / index2.html
    # コスメ商品一覧検索
    def product_search(self, key_words):
        #response = self.amazon.ItemSearch(Keywords=key_words, SearchIndex="All", ItemPage=1)
        response = self.amazon.ItemSearch(Keywords=key_words, SearchIndex="Beauty")
        u_response = response.decode('utf-8','strict')
        return u_response

    # 商品情報取得
    def get_item_info(self, item_id):
        response = self.amazon.ItemLookup(ItemId=item_id)
        u_response = response.decode('utf-8','strict')
        return u_response

    # Brand, BrowseNode, Condition, ItemPage, Keywords, Manufacturer, MaximumPrice, MerchantId, MinimumPrice, Sort, Title
    # 商品の全レビュー情報取得
    def get_reviews(self, url):
        # 取得した全レビュー情報を格納するデータフレーム型変数
        reviews = pd.DataFrame(columns=['タイトル', '投稿者', '投稿日', '評価', 'コメント'] )
        # レビュー情報のインデックス数（0～）
        index = 0

        # 対象となるURLページにアクセス
        html = urlopen(url)

        # 全レビュー情報を取得するまでループ
        while True:

            # 取得したHTML情報をパース
            soup = BeautifulSoup(html, "html.parser")
            review_parts = soup.findAll(class_="a-section review")

            for review_part in review_parts:
                # 各種情報の取得
                title = review_part.find(class_="a-size-base a-link-normal review-title a-color-base a-text-bold")
                author = review_part.find(class_="a-size-base a-link-normal author")
                date = review_part.find(class_="a-size-base a-color-secondary review-date")
                rate = review_part.find(class_="a-icon a-icon-star a-star-5 review-rating")

                if rate is None:
                    rate = review_part.find(class_="a-icon a-icon-star a-star-4 review-rating")
                if rate is None:
                    rate = review_part.find(class_="a-icon a-icon-star a-star-3 review-rating")
                if rate is None:
                    rate = review_part.find(class_="a-icon a-icon-star a-star-2 review-rating")
                if rate is None:
                    rate = review_part.find(class_="a-icon a-icon-star a-star-1 review-rating")
                comment = review_part.find(class_="a-size-base review-text")

                # 全レビュー情報をデータフレーム型変数に格納。
                review = pd.DataFrame([[title.text, author.text, date.text, rate.text, comment.text]])
                review.columns = ['タイトル', '投稿者', '投稿日', '評価', 'コメント']
                review.index = [index]
                reviews = pd.concat([reviews, review], axis=0)
                index += 1

            # レビューは１ページに10件しか表示されない。そのため、次のページをクロール
            try:
                next_page_url = soup.find(class_="a-last").a.get("href")
                html = urlopen(u'http://www.amazon.co.jp/' + next_page_url.split('/', 2)[2])

            except AttributeError:
                # 次のページが見つからなければ、検索を終了
                print("レビュー情報の検索 終了")
                break

        return reviews


# 適宜、必要なメソッドを追加する予定。