# ベースイメージ（軽めでOK）
FROM python:3.11-slim

# 環境変数（Pythonの出力をバッファしない等）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリ
WORKDIR /app

# 依存ライブラリだけ先にインストール（レイヤーキャッシュ効かせる用）
RUN pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart

# アプリのコードをコピー
COPY main.py /app/main.py
COPY templates /app/templates
COPY core /app/core
COPY mdf /app/mdf
COPY quiz /app/quiz
COPY web /app/web

# ポート公開（FastAPI / Uvicorn のデフォルト）
EXPOSE 8080

# アプリ起動コマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]