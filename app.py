import streamlit as st
import google.generativeai as genai

# 画面の基本設定
st.set_page_config(page_title="航空会社 安全性評価", page_icon="✈️", layout="centered")

correct_password = st.secrets["APP_PASSWORD"]
user_password = st.text_input("合言葉を入力してください", type="password")

if user_password != correct_password:
    st.warning("このサイトは限定公開です。正しい合言葉を入力してください。")
    st.stop()

st.title("✈️ 航空会社 安全性評価システム (V4)")
st.write("航空会社名を入力すると、最新データに基づき安全性をS〜Fで判定します。")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("システムエラー: APIキーが設定されていません。")
    st.stop()

# 指示書（エンタメ性と理由付けを追加）
system_instruction = """
あなたは航空会社の安全性を評価する専門AIです。
利用者が楽しく読めるように、キャッチーな一言を添えつつ、各項目の「理由」を簡潔に解説してください。

## 評価アルゴリズム
1. ゲートチェック（足切り）
- IOSA未取得 または EU乗り入れ禁止リスト掲載、深刻な財務危機はゲート不合格（最終判定「F」）。
2. 運航品質スコア (推定幅で算出)
- 機材品質と整備（30点）/ 安全文化と事故歴（30点）/ パイロット・労働環境（20点）/ サイバー・システム耐性（20点）
3. 軸別キャップ
- 事故歴に致命的欠陥：上限60点 / サプライチェーン極度依存：上限80点
4. 外部リスク曝露
- 地政学・紛争リスク、標的・テロリスクを【低・中・高・極高】で判定。
5. 最終判定の決定ロジック
- S(90-100), A(80-89), B(70-79), C(60-69), D(40-59), F(39以下/不合格)
※外部リスクが「高・極高」の場合は品質からランクを1〜2段階下げる。

## 出力フォーマット（厳守）
必ず以下のマークダウン形式で出力してください。ロゴ画像はClearbit APIを使用し、[]内を推測して出力します。

![ロゴ](https://logo.clearbit.com/[対象の航空会社の公式ドメイン(例: jal.co.jp)])
### ✈️ [航空会社名]：[その航空会社を表すキャッチーな一言]

**1. ゲートチェック判定**: [合否]
* *理由*: [1文で解説]

**2. 運航品質スコア**: [点数幅]
* **機材と整備**: [点数] - [理由を簡潔に]
* **安全文化と事故歴**: [点数] - [理由を簡潔に]
* **労働環境**: [点数] - [理由を簡潔に]
* **システム耐性**: [点数] - [理由を簡潔に]

**3. 外部リスク曝露**: [低・中・高・極高]
* *理由*: [地政学・標的リスクの解説を簡潔に]

**4. 2軸マトリクス**: [品質と外部リスクの組み合わせ]

**5. 最終判定**: [S/A/B/C/D/F] - [対応する文言]
"""

airline_name = st.text_input("評価したい航空会社名を入力してください (例: ANA, ライアンエアー)")

if st.button("安全性を評価する"):
    if airline_name:
        with st.spinner("AIが最新データから評価を計算中..."):
            try:
                model = genai.GenerativeModel(model_name="gemini-3.8-flash")
                final_prompt = f"{system_instruction}\n\n対象の航空会社: {airline_name}"
                response = model.generate_content(final_prompt)
                
                st.success(f"評価が完了しました。")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("航空会社名を入力してください。")
