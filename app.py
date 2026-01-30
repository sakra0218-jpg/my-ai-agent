# 4. リサーチ実行関数（Google検索グラウンディング対応）
def perform_research(query, model_full_name):
    # エラーを解消するため、'google_search' に修正
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
