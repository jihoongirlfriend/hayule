import streamlit as st
from google import genai
from google.genai import types

# ---------------------------
# 페이지 설정
# ---------------------------
st.set_page_config(
    page_title="급식 메뉴 추천 챗봇",
    page_icon="🍱",
    layout="centered"
)

st.title("🍱 급식 메뉴 추천 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# ---------------------------
# API 키 확인
# ---------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY가 설정되지 않았습니다. "
        "Streamlit Secrets를 확인해주세요."
    )
    st.stop()

# ---------------------------
# Gemini Client 생성
# ---------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 클라이언트 생성 실패: {e}")
    st.stop()

# ---------------------------
# 채팅 기록 초기화
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 🍱\n\n"
                "학생 수, 예산, 선호 음식, 알레르기 정보 등을 알려주시면 "
                "급식 메뉴를 추천해드릴게요."
            )
        }
    ]

# ---------------------------
# 기존 메시지 출력
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# 사용자 입력
# ---------------------------
prompt = st.chat_input("예: 중학생 300명, 1인당 4500원, 한식 위주")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        # 채팅 기록 문자열 생성
        history_text = ""

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "챗봇"
            history_text += f"{role}: {msg['content']}\n"

        system_prompt = """
당신은 학교 급식 영양사 및 급식 메뉴 전문 컨설턴트입니다.

규칙:
1. 급식 메뉴를 추천한다.
2. 영양 균형을 고려한다.
3. 국, 밥, 반찬, 후식 등을 포함할 수 있다.
4. 학생들이 좋아할 만한 메뉴를 제안한다.
5. 알레르기 관련 주의사항이 있으면 함께 알려준다.
6. 답변은 한국어로 작성한다.
7. 보기 좋게 마크다운 형식으로 작성한다.
"""

        full_prompt = f"""
{system_prompt}

대화 기록:
{history_text}

사용자 최신 요청:
{prompt}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1000
            )
        )

        answer = response.text

    except Exception as e:
        answer = f"""
⚠️ 오류가 발생했습니다.

오류 내용:
`{str(e)}`

잠시 후 다시 시도해주세요.
"""

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
