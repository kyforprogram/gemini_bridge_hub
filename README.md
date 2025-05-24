# Gemini 翻訳 Web API
実行前
![image](https://github.com/user-attachments/assets/0839c952-2049-4a2c-9bd0-3a4637d406af)

実行後
![image](https://github.com/user-attachments/assets/2ed06bb3-9c86-4937-a5c4-8c08dbf3238a)


## 🚀 プロジェクト概要

**Gemini 翻訳 Web API** は、Google Gemini（GenAI）を利用して、Excel 内の「英語」列テキストを自動で要約・翻訳し、エンジニア 1 年目向け／小学生向け の 2 種類のサマリを生成する Web アプリケーションです。バッチ処理やレート制御、バックグラウンドタスク（Celery）を組み合わせ、大規模データも効率的に処理できます。

## ⚙️ 主な技術スタック

* **言語・フレームワーク**: Python 3.9, Flask, Celery
* **データ処理**: Pandas, openpyxl
* **AI モデル**: Google Gemini (GenAI API)
* **メッセージブローカー**: Redis
* **コンテナ**: Docker, Docker Compose
* **クラウド**: AWS EC2, Security Group, IAM, SSM, Amazon Linux 2023

## 📦 アーキテクチャ

```text
+-------------+    HTTP    +-------------+    AMQP/Redis    +-------------+
|  Frontend   | <--------> |    Flask    | <--------------> |   Celery    |
|  (HTML/JS)  |            |  REST API   |    Broker/Backend|   Worker    |
+-------------+            +-------------+                  +-------------+
       |                                                      |
       |                                                      |
       v                                                      v
  Browser UI                                            Gemini GenAI
       |                                                      |
       v                                                      |
  File Upload                                                 |
                                                              
```

## 📋 プリレクイジット

* Python 3.9
* Docker & Docker Compose
* AWS アカウント

  * EC2 インスタンス (Amazon Linux 2023)
  * セキュリティグループでポート 5000/Open
  * IAM ロール (SSM, EC2 へのアクセス許可)
* Google GenAI API Key

## ⬇️ ローカル環境セットアップ (Docker Compose)

```bash
git clone git@github.com:kyforprogram/gemini_bridge_hub.git
cd gemini_bridge_hub
# 必要に応じて uploads ディレクトリ作成
mkdir -p uploads
# ビルド＆起動
docker-compose up --build -d
```

### コンテナ構成

* **web**: Flask API + 静的ファイルサーバ
* **worker**: Celery ワーカー
* **redis**: メッセージブローカー

## ☁️ AWS EC2 デプロイ手順

1. **EC2 インスタンス作成** (Amazon Linux 2023)
2. **セキュリティグループ**: TCP 22(SSH), 5000 を許可
3. **SSM セッションマネージャ** で接続
4. **Docker & Docker Compose Plugin** インストール
5. リポジトリをクローン & `uploads` ディレクトリ作成
6. `docker-compose up --build -d`
7. **CloudWatch Logs** で `web` / `worker` コンテナログを監視
8. ブラウザで `http://<EC2-パブリックIP>:5000/` にアクセス

## 🚀 使い方

1. ブラウザで `http:<パブリック IPv4 アドレス>:5000/` にアクセス
2. API Key を入力
3. Excel(.xlsx) ファイルを選択
4. 「翻訳開始」ボタンをクリック
5. 処理完了後にダウンロードリンクが表示される

## 📁 プロジェクト構成

```
gemini_bridge_hub/
├── backend/
│   ├── Dockerfile
│   ├── python_to_translation.py
│   ├── tasks.py
│   ├── translation_app.py
│   ├── celery_worker.sh
│   └── requirements.txt
├── frontend/
│   └── index.html
├── docker-compose.yml
├── uploads/          # 共有ボリューム
└── README.md
```



