import streamlit as st
from google import genai

# 1. 秘密の場所からAPIキーを読み込む 🔑
API_KEY = st.secrets["GEMINI_API_KEY"]

# 2. アプリの基本設定
st.set_page_config(page_title="AIリサーチ・プロ", page_icon="🔬", layout="wide")
st.title("🔬 AIプロフェッショナル・リサーチ")
st.write("環境に合わせて最適なAIモデルを自動選択し、Google検索を用いて調査します。")

# 3. 【タフな設計】利用可能なモデルを自動スキャンする関数
@st.cache_resource
def get_best_available_model(_client):
    try:
        # あなたのAPIキーで今使える全モデルのリストを取得
        models = [m.name for m in _client.models.list()]
        
        # 優先順位: 2.0-flash -> 1.5-flash -> その他
        candidates = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        for candidate in candidates:
            for actual_name in models:
                if candidate in actual_name:
                    return actual_name  # 見つかった「正式名称」を返す
        
        return models[0] # 万が一見つからなければリストの先頭を使用
    except Exception as e:
        st.error(f"モデルリストの取得に失敗しました: {e}")
        return None

# クライアントの初期化
client = genai.Client(api_key=API_KEY)
target_model = get_best_available_model(client)

if target_model:
    st.info(f"✅ システム稼働中: `{target_model}` を使用します")
else:
    st.error("APIキーが無効、または課金設定が反映されていない可能性があります。")

# 4. リサーチ実行関数（Google検索グラウンディング）
def perform_research(query, model_name):
    # Google検索ツールを有効化
    search_tool = {'google_search': {}}
    
    prompt = f"""
    あなたは高度な専門知識を持つシニアリサーチアナリストです。
    提供されたキーワードについて、Google検索を用いて最新かつ正確な情報を調査し、レポートを作成してください。

    キーワード: {query}

    【レポート構成】
    1. 概要と現状
    2. 重要なトピックや最新の動向（3点以上）
    3. 今後の展望または専門的な考察
    4. 参照ソースの明記
    """
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={'tools': [search_tool]}
    )
    return response

# 5. UI（ユーザーインターフェース）
keyword = st.text_input("調査したいテーマを入力してください", placeholder="例：ドイツロマン主義 現代政治 影響, Bach 42BO プロ奏者の評価")

if st.button("プロフェッショナル調査を開始"):
    if keyword and target_model:
        with st.spinner(f"「{keyword}」について、ネット上の膨大な情報を分析中..."):
            try:
                result = perform_research(keyword, target_model)
                
                st.success("分析が完了しました！")
                st.markdown("---")
                
                # レポートの表示
                st.markdown(result.text)
                
                # 引用情報の詳細（オプション）
                if hasattr(result, 'candidates') and result.candidates[0].grounding_metadata:
                    with st.expander("🔍 検索ソースの詳細（グラウンディング情報）"):
                        st.write(result.candidates[0].grounding_metadata)

            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ 課金上限、または一時的な回数制限に達しました。少し待ってから再試行してください。")
                else:
                    st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("キーワードを入力してください。")