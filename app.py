import streamlit as st
from google import genai  # ← 最新の google-genai を使用します
import wikipediaapi

# 1. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

# 2. アプリの基本設定 🎨
st.set_page_config(page_title="AIリサーチ・エージェント", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")
st.write("最新の Gemini 2.0 検索エンジンを使用して、ネット上の情報を調査します。")

# 3. リサーチ実行関数（2026年・Google検索完全対応）
def perform_research(query):
    try:
        # 最新の google-genai SDK 形式
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"以下のキーワードについてGoogle検索を用いて最新情報を調査しレポートを作成してください: {query}",
            config={
                'tools': [{'google_search': {}}],
            }
        )
        return response
    except Exception as e:
        # 2.0-flashがエラーの場合は1.5-flashで再試行
        st.warning("モデルを切り替えて再試行中...")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=query,
            config={'tools': [{'google_search': {}}]}
        )
        return response

# 4. UI（ユーザーインターフェース）
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：最新のトロンボーン価格, 千歳烏山の歴史, ドイツロマン主義の意義")

if st.button("プロフェッショナル調査を開始", key="main_research_button"):
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
    else:
        st.warning("キーワードを入力してください。")
