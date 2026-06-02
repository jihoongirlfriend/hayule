import streamlit as st
from google import genai

# 페이지 설정
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💖",
)

st.title("💖 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# API Key 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets에 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# Gemini 클라이언트
client = genai.Client(api_key=api_key)

# 채팅 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요 😊\n"
                "연애 고민, 썸, 이별, 재회, 고백 등 무엇이든 편하게 이야기해주세요."
            ),
        }
    ]

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("연애 고민을 입력하세요..."):

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답
    with st.chat_message("assistant"):
        try:
            with st.spinner("생각 중..."):

                # 대화 기록 구성
                history_text = ""

                for msg in st.session_state.messages:
                    role = "사용자" if msg["role"] == "user" else "상담사"
                    history_text += f"{role}: {msg['content']}\n"

                system_prompt = """
당신은 따뜻하고 공감 능력이 뛰어난 연애 상담사입니다.

규칙:
- 상대방을 비난하지 말 것
- 현실적인 조언 제공
- 공감 → 분석 → 조언 순서로 답변
- 한국어로 답변
- 너무 단정적으로 판단하지 말 것
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=f"""
{system_prompt}

다음은 지금까지의 대화입니다.

{history_text}

상담사 답변:
"""
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

        except Exception as e:
            error_msg = f"오류가 발생했습니다.\n\n{str(e)}"

            st.error(error_msg)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_msg,
                }
            )
