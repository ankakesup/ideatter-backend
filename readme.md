# 起動方法

## 1.データベースの作成
今回は twitter_clone_db という名前のデータベースを作成します。

'''
CREATE DATABASE twitter_clone_db;
'''

## 2. テーブルの作成:
作成したデータベースに接続し、ツイートを保存するための tweets テーブルを作成します。

```sql
-- twitter_clone_db データベースに接続してから実行してください
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    content VARCHAR(280) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
);
```

## 3. アプリケーションの起動
以下のコマンドを実行して、アプリケーションを起動します。

'''
net start postgresql-x64-17
python main.py
'''

# dbの作成(power shell)

'''
psql -U postgres
'''

'''
CREATE DATABASE ideatter_demo_db;
\q
'''
