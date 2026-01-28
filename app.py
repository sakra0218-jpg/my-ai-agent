import streamlit as st
import google.generativeai as genai
import wikipediaapi

# 1. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# 2. アプリの設定 🎨
st.set_page_config(page_title="AIリサーチ・プロ", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")
st.write("安定版のエンジンを使用して、Google検索とWikipediaを統合調査します。")

# 3. リサーチ機能（Google検索グラウンディング対応）
def perform_research(query):
    # Google検索ツールを定義
    tools = [{'google_search_retrieval': {}}]
    model = genai.GenerativeModel('gemini-1.5-flash', tools=tools)
    
    prompt = f"""
    あなたはプロの調査員です。以下のキーワードについて、最新の情報を調査しレポートを作成してください。
    キーワード: {query}
    【要件】概要、最新動向3点、ソースの明記。
    """
    
    response = model.generate_content(prompt)
    return response

# 4. 画面レイアウト
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：ドイツロマン主義 現代政治, トロンボーン Bach 42BO 特徴")

if st.button("リサーチを開始"):
    if keyword:
        with st.spinner(f"「{keyword}」を全力で調査中..."):
            try:
                result = perform_research(keyword)
                st.success("調査完了！")
                st.markdown("---")
                st.markdown(result.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("キーワードを入力してください。")
