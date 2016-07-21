

from bs4 import BeautifulSoup
from urllib.request import urlopen
# Amazon情報 取得用
from amazonApi import AmazonAPI
# 楽天情報 取得用
from rakutenApi import RKAPISearch

##########
# サブ処理
##########
'''Amazon詳細情報取得'''
def get_amazon_info(aisn):
    print("Amazon詳細情報取得 開始")

    # Amazon情報格納用の辞書型データ
    amazon_info_dict = {}

    # １）Amazonサイトにアクセスして、AISNで該当した製品一覧情報(XML)を取得
    amazon = AmazonAPI()
    xml = amazon.product_search(aisn)

    product_list_xml = BeautifulSoup(xml)

    # ２）一番最初に該当した製品の「詳細ページURL」「レビュー情報URL」を取得する。
    # 詳細ページURL
    detail_page_url_tag = product_list_xml.find("detailpageurl")
    detail_page_url = detail_page_url_tag.text
    #print("商品情報ページURL：")
    #print(detail_page_url)

    # レビュー情報URL
    itemlinks = product_list_xml.findAll("itemlink")
    for itemlink in itemlinks:
        if itemlink.description.text == 'All Customer Reviews':
            review_page_url = itemlink.url.text
            break
    #print("レビュー情報ページURL：")
    #print(review_page_url)

    # ３） 「詳細ページURL」のリンク先ページから「平均点」「レビュー件数取得」「画像URL取得」
    detail_page = urlopen(detail_page_url)
    detail_html = BeautifulSoup(detail_page, "html.parser")

    # 平均点
    average_block = detail_html.find(class_="reviewCountTextLinkedHistogram noUnderline")
    average_tag = average_block.find(class_="a-icon-alt")
    average_str = average_tag.text.split(" ")
    average = average_str[1]
    #print("レビュー平均点：")
    #print(average)

    # レビュー件数
    review_num_tag = detail_html.find(class_="a-size-base", id="acrCustomerReviewText")
    review_num_str = review_num_tag.text.split("件")
    review_num = review_num_str[0]
    #print("レビュー件数：")
    #print(review_num)

    # 商品画像URL（Amazonのみ使用）
    #image_url_tag = detail_html.find(class_="a-dynamic-image image-stretch-vertical frontImage", id="imgBlkFront")
    image_url_tag = detail_html.find(id="imgBlkFront")
    image_url = image_url_tag['src']
    #print("商品画像URL：")
    #print(image_url)

    # ５） 「レビューページURL」のリンク先ページからトップ評価１件の「レビュータイトル」「レビューコメント」を取得
    review_page = urlopen(review_page_url)
    review_html = BeautifulSoup(review_page, "html.parser")

    # トップレビュータイトル
    top_review_title_tag = review_html.find(class_="a-size-base review-title a-text-bold")
    if top_review_title_tag == None:
        top_review_title_tag = review_html.find(class_="a-size-base a-link-normal review-title a-color-base a-text-bold")
    top_review_title = top_review_title_tag.text
    #print("トップレビュータイトル：")
    #print(top_review_title)

    # トップレビューコメント
    top_review_comment_tag = review_html.find(class_="a-size-base review-text")
    top_review_commnet = top_review_comment_tag.text
    #print("トップレビューコメント：")
    #print(top_review_commnet)

    amazon_info_dict.update({ "detail_page_url":detail_page_url,
                              "review_page_url":review_page_url,
                              "average":average,
                              "review_num":review_num,
                              "top_review_title":top_review_title,
                              "top_review_commnet":top_review_commnet,
                              "image_url":image_url})
    return amazon_info_dict


'''楽天 詳細情報取得'''
def get_rakuten_info(keyword):
    print("楽天 詳細情報取得 開始")

    # 楽天APIクラス
    searcher = RKAPISearch()

    # キーワードで商品検索
    keyword.encode('shift_jis')
    result_list = searcher.KeywordSearch(keyword)
    return result_list



