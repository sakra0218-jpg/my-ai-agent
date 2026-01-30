import streamlit as st
import google.generativeai as genai

# 1. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# 2. アプリの基本設定
st.set_page_config(page_title="AIリサーチ・エージェント", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")
st.write("環境に合わせて最適なモデルを自動選択し、Google検索を用いて調査します。")

# 3. 【実戦的アプローチ】利用可能なモデルを自動スキャンする関数
@st.cache_resource
def get_best_available_model():
    try:
        # 今のAPIキーで使えるモデルのリストを取得
        available_models = [m.name for m in genai.list_models()]
        
        # 優先順位を定義（2.0-flashがあれば最高、なければ1.5-flash）
        candidates = ["gemini-2.0-flash", "gemini-1.5-flash"]
        
        for candidate in candidates:
            for actual_name in available_models:
                if candidate in actual_name:
                    # 'models/gemini-1.5-flash-latest' のような「現場の名前」を返す
                    return actual_name
        
        # 見つからなければリストの先頭を返す
        return available_models[0]
    except Exception as e:
        st.error(f"モデルの自動スキャンに失敗しました: {e}")
        return "models/gemini-1.5-flash" # フォールバック

# モデル名を自動確定
target_model_name = get_best_available_model()

# どのモデルが選ばれたか表示（開発中の安心感のため）
st.info(f"✅ 使用中のモデル: `{target_model_name}`")

# 4. リサーチ実行関数（Google検索グラウンディング）
def perform_research(query, model_full_name):
    # Google検索ツールを定義
    tools = [{'google_search': {}}]
    model = genai.GenerativeModel(model_name=model_full_name, tools=tools)
    
    prompt = f"""
    あなたは高度な専門知識を持つシニアリサーチアナリストです。
    以下のキーワードについて、Google検索を用いて最新かつ正確な情報を調査し、レポートを作成してください。

    キーワード: {query}

    【レポート構成】
    1. 概要と現状
    2. 重要なトピックや最新の動向（3点以上）
    3. 今後の展望または専門的な考察
    4. 参照ソースの明記
    """
    
    response = model.generate_content(prompt)
    return response

# 5. UI（ユーザーインターフェース）
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：最新のAIトレンド, 特定の機材の評価など")

if st.button("プロフェッショナル調査を開始"):
    if keyword:
        with st.spinner(f"「{keyword}」について、ネット上の情報を分析中..."):
            try:
                result = perform_research(keyword, target_model_name)
                st.success("分析が完了しました！")
                st.markdown("---")
                st.markdown(result.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("キーワードを入力してください。")
