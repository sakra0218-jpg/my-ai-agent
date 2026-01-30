import os
import sys
import subprocess

# 1. 強制インストール（requirements.txtが無視される問題への対策）
try:
    import google.genai as genai
except ImportError:
    # 実行時に直接ライブラリをインストールします
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    import google.genai as genai

import streamlit as st

# 2. アプリの基本設定
st.set_page_config(page_title="AIリサーチ・エージェント", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")

# 3. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]
# 最新のSDK形式でクライアントを作成
client = genai.Client(api_key=API_KEY)

# 4. リサーチ実行関数（最新のgoogle-genai v1.0+ 形式）
def perform_research(query):
    # 最新SDKでの検索ツールの指定方法
    # ここが 'google_search' か 'google_search_retrieval' かで悩む必要がなくなります
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"以下のキーワードについてGoogle検索を用いて最新情報を調査しレポートを作成してください: {query}",
            config={
                'tools': [{'google_search': {}}],
            }
        )
        return response
    except Exception as e:
        # 2.0-flashが未対応の場合は1.5-flashでリトライ
        st.warning("モデルを切り替えて再試行中...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=query,
            config={'tools': [{'google_search': {}}]}
        )
        return response

# 5. UI設定
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：最新のトロンボーン価格, ドイツ哲学 現代的意義")

if st.button("プロフェッショナル調査を開始", key="final_button"):
    if keyword:
        with st.spinner(f"「{keyword}」を分析中..."):
            try:
                result = perform_research(keyword)
                if result and result.text:
                    st.success("分析が完了しました！")
                    st.markdown("---")
                    st.markdown(result.text)
                else:
                    st.error("AIからの回答が空でした。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
