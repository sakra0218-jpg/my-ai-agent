import streamlit as st
import google.generativeai as genai

# 1. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# 2. アプリの基本設定
st.set_page_config(page_title="AIリサーチ・エージェント", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")
st.write("環境に合わせて最適なモデルを自動選択し、Google検索を用いて調査します。")

# 3. モデルを自動スキャンする関数
@st.cache_resource
def get_best_available_model():
    try:
        available_models = [m.name for m in genai.list_models()]
        candidates = ["gemini-2.0-flash", "gemini-1.5-flash"]
        for candidate in candidates:
            for actual_name in available_models:
                if candidate in actual_name:
                    return actual_name
        return available_models[0]
    except Exception as e:
        return "models/gemini-1.5-flash"

target_model_name = get_best_available_model()
st.info(f"✅ 使用中のモデル: `{target_model_name}`")

# 4. リサーチ実行関数（プロトコル直接指定でエラーを回避）
def perform_research(query, model_full_name):
    prompt = f"キーワード: {query} について、Google検索を用いて最新の正確なレポートを作成してください。"

    # 【重要】辞書形式ではなく、モデルに合わせたツール定義を生成します
    # 2.0系と1.5系で名前が混在している現状を突破する書き方です
    
    try:
        # まず、2026年の標準である google_search 形式を試みます
        # 内部的な proto 構造を模倣することで "Unknown field" を回避します
        model = genai.GenerativeModel(
            model_name=model_full_name,
            tools=[{"google_search": {}}]
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response
    except Exception as e:
        # 万が一 Unknown field が出た場合、文字列指定で再試行します
        # 一部のSDKバージョンではこの「文字列渡し」が魔法のように効きます
        try:
            model = genai.GenerativeModel(model_name=model_full_name, tools="google_search")
            response = model.generate_content(prompt)
            if response and response.text:
                return response
        except:
            # 最終手段：1.5系で動作が保証されている古い形式にフォールバック
            # APIが「古い」と言っても、SDKが新しい名前を知らない場合はこちらが通ります
            model = genai.GenerativeModel(
                model_name=model_full_name,
                tools=[{"google_search_retrieval": {}}]
            )
            return model.generate_content(prompt)

# 5. UI（ここがエラーの原因でした。ボタンは1つだけにします）
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：最新のトロンボーン価格, ドイツ哲学 現代的意義")

# 重複を防ぐため、一度しか登場させない
if st.button("プロフェッショナル調査を開始", key="research_button"):
    if keyword:
        with st.spinner(f"「{keyword}」を分析中..."):
            try:
                result = perform_research(keyword, target_model_name)
                if result and hasattr(result, 'text'):
                    st.success("分析が完了しました！")
                    st.markdown("---")
                    st.markdown(result.text)
                else:
                    st.error("AIからの回答が空でした。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("キーワードを入力してください。")


