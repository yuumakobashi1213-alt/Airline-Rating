import streamlit as st
import google.generativeai as genai

# 画面の基本設定
st.set_page_config(page_title="航空会社 安全性評価", page_icon="✈️", layout="centered")

# --- 合言葉（パスワード）設定 ---
# secretsに設定した合言葉と一致しないと中身を見せない仕組み
correct_password = st.secrets["APP_PASSWORD"]
user_password = st.text_input("合言葉を入力してください", type="password")

if user_password != correct_password:
    st.warning("このサイトは限定公開です。正しい合言葉を入力してください。")
    st.stop() # ここで処理を止める

# --- ここから下がメイン画面 ---
st.title("✈️ 航空会社 安全性評価システム (V4)")
st.write("航空会社名を入力すると、最新データに基づき安全性をS〜Fで判定します。")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("システムエラー: APIキーが設定されていません。")
    st.stop()

# V4モデルの指示書
system_instruction = """
航空会社名を受け取り、安全リスクを客観的に算出します。
コンサルティング総評などの文章は出力せず、指定のフォーマットに従って端的に結果を出力してください。

## 評価アルゴリズム
1. ゲートチェック（足切り）
- IOSA未取得 または EU乗り入れ禁止リスト掲載、あるいは深刻な財務危機の場合はゲート不合格（最終判定「F」）。

2. 運航品質スコア (推定幅で算出)
- 機材品質と整備（30点）
- 安全文化と事故歴（30点）
- パイロット・労働環境（20点）
- サイバー・システム耐性（20点）

3. 軸別キャップ
- 事故歴に致命的欠陥がある場合：品質スコア上限60点
- サプライチェーンに極度な依存がある場合：品質スコア上限80点

4. 外部リスク曝露
- 地政学・紛争リスク、標的・テロリスクを【低・中・高・極高】で判定。

5. 最終判定の決定ロジック
- S (90〜100点相当): 問題なし
- A (80〜89点相当): 問題なし
- B (70〜79点相当): 問題なし
- C (60〜69点相当): やや懸念あり
- D (40〜59点相当): どうしてもの場合は乗っても良い
- F (39点以下 または ゲート不合格): 絶対避けるべき
※外部リスクが「高・極高」の場合は品質からランクを1〜2段階下げる。

## 出力フォーマット（厳守）
1. **ゲートチェック判定**: [合否]
2. **運航品質スコア**: [点数幅]
3. **外部リスク曝露**: [判定]
4. **2軸マトリクス**: [品質と外部リスクの組み合わせ]
5. **最終判定**: [S/A/B/C/D/F] - [対応する文言]
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)

airline_name = st.text_input("評価したい航空会社名を入力してください (例: ANA, ライアンエアー)")

if st.button("安全性を評価する"):
    if airline_name:
        with st.spinner("AIが最新データを検索し、評価を計算中..."):
            try:
                response = model.generate_content(airline_name)
                st.success("評価が完了しました。")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("航空会社名を入力してください。")
