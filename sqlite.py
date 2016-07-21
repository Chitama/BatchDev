

import sqlite3
from datetime import datetime

# SQL操作用クラス
class SQLite:

    # 初期化
    def __init__(self):

        # DBに接続する
        self.connection = sqlite3.connect(
                                     host='localhost',
                                     user='root',
                                     password='himiT123',
                                     db='batchDev',
                                     charset='utf8',
                                     cursorclass=sqlite3.cursors.DictCursor
                                )

# 製品テーブルから製品リスト（ISBNリスト）を取得するメソッド
    def get_aisn_list(self):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "SELECT aisn, title FROM product"
            cursor.execute(sql)
        # 結果取り出し
        aisn_list = cursor.fetchall()
        return aisn_list


# 製品テーブルから指定したISBNに対応する製品名を取得すメソッド
    def get_product(self, aisn):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "SELECT title FROM product WHERE aisn=%s"
            cursor.execute(sql, (aisn))
        # 結果取り出し
        result = cursor.fetchall()
        return result


# Amazon情報テーブルから指定したISBNに該当するレコードを削除するメソッド
    def delete_amazon_records(self, aisn):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM product_amazon WHERE aisn_id=%s"
            delete_num = cursor.execute(sql, (aisn))
            print("Amazon情報テーブル レコード削除：" + str(delete_num) + "件")

# 楽天情報テーブルから指定したISBNに該当するレコードを削除するメソッド
    def delete_rakuten_records(self, aisn):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM product_rakuten WHERE aisn_id=%s"
            delete_num =cursor.execute(sql, (aisn))
            print("楽天情報テーブル レコード削除：" + str(delete_num) + "件")



# Amazon情報テーブルに１件レコード追加するメソッド
    def insert_amazon_info(self,
                           aisn,
                           average,
                           review_num,
                           top_review_title,
                           top_review_comment,
                           review_url,
                           detail_url
                        ):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO \
                        product_amazon(aisn_id, average, review_num, top_review_title, top_review_comment, review_url, detail_url, registered) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            insert_num=cursor.execute(sql, (aisn, average, review_num, top_review_title, top_review_comment, review_url, detail_url, datetime.now().date()))
            print("Amazon情報テーブル レコード追加：" + str(insert_num) + "件")
            #明示的コミット
            self.connection.commit()

# 楽天情報テーブルに１件レコード追加するメソッド
    def insert_rakuten_info(self,
                           aisn,
                           average,
                           review_num,
                           top_review_title,
                           top_review_comment,
                           review_url,
                           detail_url
                        ):
        # SQL実行
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO \
                        product_rakuten(aisn_id, average, review_num, top_review_title, top_review_comment, review_url, detail_url, registered) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            insert_num=cursor.execute(sql, (aisn, average, review_num, top_review_title, top_review_comment, review_url, detail_url, datetime.now().date()))
            print("楽天情報テーブル レコード追加：" + str(insert_num) + "件")
            #明示的コミット
            self.connection.commit()



# データベース切断メソッド
    def db_close(self):
        self.connection.close()



