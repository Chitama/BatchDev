

import sys
from sqlite import sqlite3
# サブ処理
import batch_sub as sub

##########
# メイン処理
##########
if __name__ == "__main__":

    ''' 第一引数でAISN取得 '''
    param = sys.argv
    aisn = param[1]
    # AISN文字列をUTF-8にエンコード
    aisn.encode('utf-8')

    # DB接続
    sqlite = SQLite()

    ''' AISNチェック（製品テーブル）'''
    # 製品テーブルに、引数で指定されたISBNに対応する製品がない場合、プログラム異常終了。
    # 対応する製品がある場合、製品名（リスト）を返す。
    title_list = sqlite.get_product(aisn)
    if len(title_list) == 0:
        print("【Error】引数で指定したISBNに対応する製品は、登録されていません。")

        # DB切断
        sqlite.db_close()
        sys.exit(-1)

    ''' 「Amazon」情報 更新処理 '''
    # Amazonサイトから製品情報をスクレイピング。
    amazon_info_dict = sub.get_amazon_info(aisn)

    # 古いレコード削除（Amazon情報テーブル）
    sqlite.delete_amazon_records(aisn)

    # 新規レコード追加（Amazon情報テーブル）
    sqlite.insert_amazon_info(
                       aisn,
                       amazon_info_dict['average'],
                       amazon_info_dict['review_num'],
                       amazon_info_dict['top_review_title'],
                       amazon_info_dict['top_review_commnet'],
                       amazon_info_dict['review_page_url'],
                       amazon_info_dict['detail_page_url'],
                       )

    # レコード更新（製品テーブル）
    sqlite.update_amazon_flg(aisn, True, amazon_info_dict['image_url'])

    ''' 「楽天」情報 更新処理 '''
    # 楽天から情報を取得
    rakuten_info_list = sub.get_rakuten_info(aisn)

    # 古いレコード削除（楽天情報テーブル）
    sqlite.delete_rakuten_records(aisn)

    # 新規レコード追加（Amazon情報テーブル）
    sqlite.insert_rakuten_info(
                       aisn,
                       rakuten_info_list[0].rsReviewRate,
                       rakuten_info_list[0].rsReviewCount,
                       "楽天レビュータイトルだよ",#取得してきた値に変更する
                       rakuten_info_list[0].rsReviewComments[0],
                       rakuten_info_list[0].rsItemURL,#レビューURLに変更する
                       rakuten_info_list[0].rsItemURL,
                       )

    # レコード更新（製品テーブル）
    sqlite.update_rakuten_flg(aisn, True)




    # DB切断
    sqlite.db_close()
    # 正常終了
    sys.exit(0)



