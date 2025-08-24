# main.py
import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# --- Flaskアプリケーションの初期設定 ---
app = Flask(__name__)

# CORSの設定
CORS(app, origins=["http://localhost:5173", "http://localhost:5175"]) # フロントエンドのURLを追加して

# --- データベースの設定 ---
# 環境変数からデータベースURLを取得。なければデフォルト値を使用。
# 例: postgresql://<user>:<password>@<host>:<port>/<dbname>
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'kono5013') # ここにパスワードを入力
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432') # データベースのポート番号を指定
db_name = os.environ.get('DB_NAME', 'ideatter_demo_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyのインスタンスを作成
db = SQLAlchemy(app)

# --- データベースモデルの定義 (ORM) ---
# Ideaモデルの定義
class Idea(db.Model):
    __tablename__ = 'ideas' # 対応付けるテーブル名
    ideaId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    explanationA = db.Column(db.String(120), nullable=False)
    explanationB = db.Column(db.String(120))
    explanationC = db.Column(db.String(120))
    description = db.Column(db.String(2000))
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    likes = db.Column(db.Integer, nullable=False, default=0)

    # JSONに変換するためのヘルパーメソッド
    def to_dict(self):
        return {
            "ideaId": self.ideaId,
            "username": self.username,
            "explanationA": self.explanationA,
            "explanationB": self.explanationB,
            "explanationC": self.explanationC,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() + 'Z', # ISO 8601形式で返す
            "likes": self.likes
        }

# Commentモデルの定義
class Comment(db.Model):
    __tablename__ = 'comments' # 対応付けるテーブル名
    commentId = db.Column(db.Integer, primary_key=True)
    ideaId = db.Column(db.Integer, db.ForeignKey('ideas.ideaId'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # JSONに変換するためのヘルパーメソッド
    def to_dict(self):
        return {
            "commentId": self.commentId,
            "ideaId": self.ideaId,
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() + 'Z' # ISO 8601形式で返す
        }

# WantToCreateモデルの定義
# このモデルは、ユーザーがアイデアを作成したいことを示す
class WantToCreate(db.Model):
    __tablename__ = 'want_to_create' # 対応付けるテーブル名
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    ideaId = db.Column(db.Integer, db.ForeignKey('ideas.ideaId'), nullable=False)
    
    # JSONに変換するためのヘルパーメソッド
    def to_dict(self):
        return {
            "username": self.username,
            "ideaId": self.ideaId,
        }

# --- APIエンドポイントの定義 ---

@app.route("/")
def read_root():
    return render_template("desc.html")

@app.route("/ideas", methods=['GET'])
def get_tweets():
    """全てのツイートをデータベースから取得する"""
    try:
        # データベースからidの降順で全てのツイートを取得
        tweets = Idea.query.order_by(Idea.ideaId.desc()).all()
        # 各ツイートを辞書に変換してリストにする
        return jsonify([tweet.to_dict() for tweet in tweets])
    except Exception as e:
        # エラーハンドリング
        return jsonify({"error": "Could not retrieve tweets", "details": str(e)}), 500
    
@app.route("/comments/<int:idea_id>", methods=['GET'])
def get_comments(idea_id):
    """指定されたアイデアのコメントを取得する"""
    try:
        # 指定されたアイデアIDに紐づくコメントを取得
        comments = Comment.query.filter_by(ideaId=idea_id).order_by(Comment.timestamp.desc()).all()
        # 各コメントを辞書に変換してリストにする
        return jsonify([comment.to_dict() for comment in comments])
    except Exception as e:
        # エラーハンドリング
        return jsonify({"error": "Could not retrieve comments", "details": str(e)}), 500

@app.route("/comments/<int:idea_id>/count", methods=['GET'])
def get_comment_count(idea_id):
    """指定されたアイデアのコメント数を取得する"""
    try:
        # 指定されたアイデアIDに紐づくコメントの数をカウント
        count = Comment.query.filter_by(ideaId=idea_id).count()
        return jsonify({"ideaId": idea_id, "commentCount": count})
    except Exception as e:
        # エラーハンドリング
        return jsonify({"error": "Could not retrieve comment count", "details": str(e)}), 500
    
@app.route("/create/<int:idea_id>", methods=['GET'])
def get_want_to_create(idea_id):
    """指定されたアイデアに対して、ユーザーが作成したいことを示す"""
    try:
        # 指定されたアイデアIDに紐づくWantToCreateを取得
        want_to_create = WantToCreate.query.filter_by(ideaId=idea_id).all()
        # 各WantToCreateを辞書に変換してリストにする
        return jsonify([item.to_dict() for item in want_to_create])
    except Exception as e:
        # エラーハンドリング
        return jsonify({"error": "Could not retrieve want to create", "details": str(e)}), 500
    
@app.route("/create/<int:idea_id>/count", methods=['GET'])
def get_want_to_create_count(idea_id):
    """指定されたアイデアに対して、ユーザーが作成したいことを示す数を取得する"""
    try:
        # 指定されたアイデアIDに紐づくWantToCreateの数をカウント
        count = WantToCreate.query.filter_by(ideaId=idea_id).count()
        return jsonify({"ideaId": idea_id, "wantToCreateCount": count})
    except Exception as e:
        # エラーハンドリング
        return jsonify({"error": "Could not retrieve want to create count", "details": str(e)}), 500


@app.route("/post/idea", methods=['POST'])
def create_tweet():
    """新しいツイートをデータベースに保存する"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    username = data.get('username')
    explanationA = data.get('explanationA')
    explanationB = data.get('explanationB')
    explanationC = data.get('explanationC')
    description = data.get('description')
    likes = data.get('likes', 0)

    if not username or not explanationA:
        return jsonify({"error": "Missing username or content"}), 400

    try:
        # 新しいTweetオブジェクトを作成
        newIdea = Idea(
            username=username, 
            explanationA=explanationA,
            explanationB=explanationB,
            explanationC=explanationC,
            description=description,
            likes=likes
        )
        
        # データベースセッションに追加
        db.session.add(newIdea)
        # データベースに変更をコミット（保存）
        db.session.commit()
        
        return jsonify(newIdea.to_dict()), 201
    except Exception as e:
        db.session.rollback() # エラーが発生した場合はロールバック
        return jsonify({"error": "Could not create tweet", "details": str(e)}), 500

@app.route("/post/comment", methods=['POST'])
def create_comment():
    """新しいコメントをデータベースに保存する"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    ideaId = data.get('ideaId')
    username = data.get('username')
    content = data.get('content')

    if not ideaId or not username or not content:
        return jsonify({"error": "Missing ideaId, username, or content"}), 400

    try:
        # 新しいCommentオブジェクトを作成
        newComment = Comment(
            ideaId=ideaId,
            username=username,
            content=content
        )
        
        # データベースセッションに追加
        db.session.add(newComment)
        # データベースに変更をコミット（保存）
        db.session.commit()
        
        return jsonify(newComment.to_dict()), 201
    
    except Exception as e:
        db.session.rollback() # エラーが発生した場合はロールバック
        return jsonify({"error": "Could not create comment", "details": str(e)}), 500

@app.route("/post/create", methods=['POST'])
def create_want_to_create():
    """ユーザーがアイデアを作成したいことを示す"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    username = data.get('username')
    ideaId = data.get('ideaId')

    if not username or not ideaId:
        return jsonify({"error": "Missing username or ideaId"}), 400

    try:
        # 新しいWantToCreateオブジェクトを作成
        newWantToCreate = WantToCreate(
            username=username,
            ideaId=ideaId
        )
        
        # データベースセッションに追加
        db.session.add(newWantToCreate)
        # データベースに変更をコミット（保存）
        db.session.commit()
        
        return jsonify(newWantToCreate.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not create want to create", "details": str(e)}), 500

@app.route("/ideas/<int:idea_id>/like", methods=['POST'])
def increment_likes(idea_id):
    """指定されたアイデアのいいね数を排他制御付きでインクリメントする"""
    try:
        # 排他ロック付きで該当のアイデアを取得
        # with_for_update(nowait=False)でペシミスティックロックを適用
        idea = db.session.query(Idea).filter_by(ideaId=idea_id).with_for_update().first()
        
        if not idea:
            return jsonify({"error": "Idea not found"}), 404
        
        # いいね数をインクリメント
        idea.likes += 1
        
        # データベースに変更をコミット
        db.session.commit()
        
        return jsonify({
            "ideaId": idea.ideaId,
            "likes": idea.likes,
            "message": "Like count incremented successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Could not increment likes", "details": str(e)}), 500


# --- サーバーの起動 ---
if __name__ == "__main__":
    # アプリケーションコンテキスト内でテーブルを作成
    # このコードは初回実行時、またはモデルに変更があった場合にテーブルを（再）作成します
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)
