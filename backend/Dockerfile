FROM python:3.9-slim

# 作業ディレクトリ作成
WORKDIR /app

# 依存関係のコピー＆インストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# uploads ディレクトリを永続化
RUN mkdir -p uploads

# ポート設定（Flask）
EXPOSE 5000

# デフォルトコマンド
CMD ["sh", "-c", "celery -A tasks worker --loglevel=info & python translation_app.py"]
