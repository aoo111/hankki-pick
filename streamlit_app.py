import streamlit as st
from openai import OpenAI
from pathlib import Path
import tempfile
import os
import random


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="오늘 뭐 먹지?",
    page_icon="🍽️",
    layout="centered"
)

st.title("🍽️ 오늘 뭐 먹지?")

st.write(
    """
    오늘 먹을 메뉴가 고민된다면 제가 골라드릴게요! 😋

    **AI 추천부터 음성 질문, 랜덤 뽑기, 음식 월드컵까지**
    원하는 방식으로 오늘의 메뉴를 결정해보세요.
    """
)


# =========================================================
# 2. OpenAI API KEY 설정
# =========================================================

try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]

except Exception:
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password"
    )


if not openai_api_key:

    st.info(
        "왼쪽 메뉴에서 OpenAI API Key를 입력해주세요. 🔑"
    )

    st.stop()


client = OpenAI(
    api_key=openai_api_key
)


# =========================================================
# 3. 사용할 AI 모델
# =========================================================

TEXT_MODEL = "gpt-5.6-luna"

TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"

VOICE_MODEL = "gpt-4o-mini-tts"


# =========================================================
# 4. 메뉴 데이터
# =========================================================

MENU_DATA = {

    "한식": [
        "김치찌개",
        "된장찌개",
        "순두부찌개",
        "제육볶음",
        "닭갈비",
        "삼겹살",
        "불고기",
        "비빔밥",
        "국밥",
        "냉면",
        "칼국수",
        "부대찌개",
        "보쌈",
        "족발",
        "갈비탕"
    ],

    "중식": [
        "짜장면",
        "짬뽕",
        "볶음밥",
        "탕수육",
        "마파두부",
        "마라탕",
        "마라샹궈",
        "유린기",
        "양꼬치",
        "우육면"
    ],

    "일식": [
        "돈까스",
        "초밥",
        "우동",
        "라멘",
        "규동",
        "가츠동",
        "카레",
        "회덮밥",
        "소바",
        "오므라이스"
    ],

    "양식": [
        "토마토 파스타",
        "크림 파스타",
        "알리오 올리오",
        "리조또",
        "피자",
        "스테이크",
        "라자냐",
        "감바스",
        "함박스테이크",
        "필라프"
    ],

    "분식": [
        "떡볶이",
        "김밥",
        "라면",
        "순대",
        "튀김",
        "쫄면",
        "라볶이",
        "어묵",
        "김치볶음밥",
        "떡꼬치"
    ],

    "아시아 음식": [
        "쌀국수",
        "팟타이",
        "분짜",
        "나시고랭",
        "카오팟",
        "반미",
        "탄탄면",
        "똠얌꿍",
        "인도 카레",
        "탄두리치킨"
    ],

    "패스트푸드": [
        "햄버거",
        "치킨",
        "핫도그",
        "치킨버거",
        "감자튀김",
        "타코",
        "부리토",
        "샌드위치",
        "피자",
        "치킨텐더"
    ],

    "샐러드 / 건강식": [
        "닭가슴살 샐러드",
        "연어 샐러드",
        "포케",
        "두부 샐러드",
        "샌드위치",
        "그릭요거트",
        "닭가슴살 도시락",
        "월남쌈",
        "곤약 비빔밥",
        "두부덮밥"
    ]
}


# 모든 메뉴를 하나의 리스트로 합치기
ALL_MENUS = []

for category_menus in MENU_DATA.values():

    for menu in category_menus:

        if menu not in ALL_MENUS:
            ALL_MENUS.append(menu)


# =========================================================
# 5. AI 메뉴 추천 역할 설정
# =========================================================

FOOD_SYSTEM_PROMPT = """
당신은 사용자가 오늘 먹을 음식을 결정하도록 도와주는
친근하고 센스 있는 AI 메뉴 추천 전문가입니다.

사용자의 상황, 취향, 예산, 음식 종류,
매운맛 선호도, 배고픔과 기분을 종합해서
오늘 가장 잘 어울리는 메뉴를 추천하세요.


[고려할 정보]

1. 아침 / 점심 / 저녁 / 야식
2. 음식 종류
3. 혼밥인지 여러 명인지
4. 배달 / 외식 / 포장 / 집밥 여부
5. 예산
6. 매운맛 선호도
7. 배고픔 정도
8. 현재 기분
9. 싫어하거나 먹지 못하는 음식
10. 이전에 이미 먹었다고 말한 음식


[추천 방식]

가능하면 메뉴를 3개 추천하세요.

다음 형태로 답변하세요.


### 🥇 오늘의 1순위
메뉴 이름

현재 상황에서 추천하는 이유를 짧게 설명하세요.


### 🥈 2순위
메뉴 이름

추천 이유를 짧게 설명하세요.


### 🥉 3순위
메뉴 이름

추천 이유를 짧게 설명하세요.


마지막에는 반드시

**🍽️ 오늘 하나만 고른다면: 메뉴 이름**

형태로 최종 메뉴 하나를 확실하게 골라주세요.


[중요한 규칙]

- 너무 많은 메뉴를 나열하지 마세요.
- 최종적으로 하나를 확실하게 선택해주세요.
- 사용자가 싫다고 한 음식은 추천하지 마세요.
- 이미 먹었다고 말한 음식은 가급적 제외하세요.
- 알레르기나 먹지 못하는 음식은 반드시 제외하세요.
- 조건이 충분하면 불필요한 질문을 하지 마세요.
- 정보가 너무 부족할 경우에만 질문 1~2개를 하세요.
- 실제 존재 여부를 확인하지 않은 음식점 이름은 만들지 마세요.
- 위치나 날씨를 확인하지 않았다면 임의로 만들어내지 마세요.
- 친근하고 자연스러운 한국어를 사용하세요.
- 설명은 길지 않게 해주세요.
"""


# =========================================================
# 6. 처음 환영 메시지
# =========================================================

WELCOME_MESSAGE = """
안녕하세요! 🍽️

오늘도 **뭐 먹을지 고민 중이신가요?**

제가 오늘 먹기 좋은 메뉴를 골라드릴게요. 😋

### 원하는 방법을 골라보세요.

💬 **AI에게 메뉴 추천받기**

🎤 **말해서 추천받기**

🎲 **랜덤 메뉴 뽑기**

🥊 **음식 월드컵**

예를 들어,

- "오늘 저녁 뭐 먹지?"
- "매콤하고 든든한 거 먹고 싶어"
- "만원 정도로 혼밥 추천해줘"
- "데이트 메뉴 추천해줘"
- "어제 치킨 먹었으니까 빼줘"

처럼 질문해보세요!
"""


if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "voice": False,
            "exclude_from_model": True
        }
    ]


# =========================================================
# 7. 게임에 사용할 메뉴 가져오기
# =========================================================

def get_game_menu_pool(food_type, avoid_food):

    if food_type in MENU_DATA:

        menu_pool = MENU_DATA[food_type].copy()

    else:

        menu_pool = ALL_MENUS.copy()


    # 사용자가 쉼표로 제외 음식을 입력했을 경우
    if avoid_food:

        avoid_words = [
            word.strip()
            for word in avoid_food.replace("/", ",").split(",")
            if word.strip()
        ]

        filtered_pool = []

        for menu in menu_pool:

            blocked = False

            for word in avoid_words:

                if word in menu:
                    blocked = True
                    break

            if not blocked:
                filtered_pool.append(menu)

        menu_pool = filtered_pool


    return menu_pool


# =========================================================
# 8. 음식 월드컵 시작 함수
# =========================================================

def start_worldcup(menu_pool):

    if len(menu_pool) < 2:

        st.session_state.worldcup_error = (
            "월드컵을 진행할 메뉴가 부족합니다."
        )

        return


    if len(menu_pool) >= 8:
        tournament_size = 8

    elif len(menu_pool) >= 4:
        tournament_size = 4

    else:
        tournament_size = 2


    contestants = random.sample(
        menu_pool,
        tournament_size
    )


    st.session_state.worldcup_contestants = contestants

    st.session_state.worldcup_winners = []

    st.session_state.worldcup_match_index = 0

    st.session_state.worldcup_champion = None

    st.session_state.worldcup_error = None


# =========================================================
# 9. 음식 월드컵 선택 함수
# =========================================================

def choose_worldcup_menu(winner):

    st.session_state.worldcup_winners.append(
        winner
    )

    st.session_state.worldcup_match_index += 2


    contestants = (
        st.session_state.worldcup_contestants
    )


    # 현재 라운드가 끝난 경우
    if (
        st.session_state.worldcup_match_index
        >= len(contestants)
    ):

        winners = (
            st.session_state.worldcup_winners.copy()
        )


        # 최종 우승
        if len(winners) == 1:

            st.session_state.worldcup_champion = (
                winners[0]
            )


        # 다음 라운드
        else:

            st.session_state.worldcup_contestants = (
                winners
            )

            st.session_state.worldcup_winners = []

            st.session_state.worldcup_match_index = 0


    st.rerun()


# =========================================================
# 10. 사이드바 설정
# =========================================================

with st.sidebar:

    st.header("🍴 오늘의 식사 설정")

    st.caption(
        "원하는 조건만 선택해도 됩니다."
    )


    meal_time = st.selectbox(
        "🕐 언제 먹나요?",
        [
            "상관없음",
            "아침",
            "점심",
            "저녁",
            "야식"
        ]
    )


    food_type = st.selectbox(
        "🍚 어떤 종류가 당기나요?",
        [
            "상관없음",
            "한식",
            "중식",
            "일식",
            "양식",
            "분식",
            "아시아 음식",
            "패스트푸드",
            "샐러드 / 건강식"
        ]
    )


    situation = st.selectbox(
        "👥 누구와 먹나요?",
        [
            "상관없음",
            "혼밥",
            "친구",
            "연인 / 데이트",
            "가족",
            "직장 동료"
        ]
    )


    eating_method = st.selectbox(
        "🏠 어떻게 먹을까요?",
        [
            "상관없음",
            "외식",
            "배달",
            "포장",
            "집에서 만들어 먹기"
        ]
    )


    budget = st.selectbox(
        "💰 1인당 예산은?",
        [
            "상관없음",
            "5,000원 이하",
            "5,000원 ~ 10,000원",
            "10,000원 ~ 15,000원",
            "15,000원 ~ 30,000원",
            "30,000원 이상"
        ]
    )


    spicy = st.select_slider(
        "🌶️ 매운맛",
        options=[
            "안 매운 음식",
            "살짝 매콤",
            "적당히 매운맛",
            "아주 매운맛",
            "상관없음"
        ],
        value="상관없음"
    )


    hunger = st.select_slider(
        "🍖 지금 얼마나 배고픈가요?",
        options=[
            "가볍게",
            "보통",
            "든든하게",
            "엄청 배고픔"
        ],
        value="보통"
    )


    mood = st.selectbox(
        "😊 지금 기분은?",
        [
            "상관없음",
            "기분 좋은 날",
            "스트레스 받음",
            "피곤함",
            "기분이 가라앉음",
            "특별한 걸 먹고 싶음",
            "그냥 빨리 먹고 싶음"
        ]
    )


    avoid_food = st.text_input(
        "🚫 먹기 싫거나 못 먹는 음식",
        placeholder="예: 해산물, 치즈, 오이"
    )


    st.divider()


    # =====================================================
    # 음성 설정
    # =====================================================

    st.subheader("🔊 음성 설정")


    voice_answer = st.toggle(
        "음성 질문에 음성으로 답하기",
        value=True
    )


    st.caption(
        "음성 답변은 AI가 생성한 음성입니다."
    )


    st.divider()


    # =====================================================
    # 초기화
    # =====================================================

    if st.button(
        "🗑️ 대화 초기화",
        use_container_width=True
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
                "voice": False,
                "exclude_from_model": True
            }
        ]


        # 게임 기록도 초기화
        keys_to_delete = [
            "random_menu",
            "worldcup_contestants",
            "worldcup_winners",
            "worldcup_match_index",
            "worldcup_champion",
            "worldcup_error"
        ]


        for key in keys_to_delete:

            if key in st.session_state:

                del st.session_state[key]


        st.rerun()


# =========================================================
# 11. 현재 조건 확인
# =========================================================

with st.expander(
    "🍴 현재 선택한 조건 보기"
):

    st.write(
        f"**식사 시간:** {meal_time}"
    )

    st.write(
        f"**음식 종류:** {food_type}"
    )

    st.write(
        f"**식사 상대:** {situation}"
    )

    st.write(
        f"**식사 방법:** {eating_method}"
    )

    st.write(
        f"**예산:** {budget}"
    )

    st.write(
        f"**매운맛:** {spicy}"
    )

    st.write(
        f"**배고픔:** {hunger}"
    )

    st.write(
        f"**기분:** {mood}"
    )

    st.write(
        f"**제외 음식:** "
        f"{avoid_food if avoid_food else '없음'}"
    )


# =========================================================
# 12. 기존 대화 출력
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        if (
            message["role"] == "user"
            and message.get("voice", False)
        ):

            st.caption(
                "🎤 음성으로 질문했습니다."
            )


        st.markdown(
            message["content"]
        )


        if message.get("audio"):

            st.audio(
                message["audio"],
                format="audio/mp3"
            )


# =========================================================
# 13. 메뉴 결정 게임
# =========================================================

st.divider()

st.header("🎮 메뉴 결정 게임")

st.write(
    "생각하기도 귀찮다면 게임으로 결정해보세요!"
)


game_tab1, game_tab2 = st.tabs(
    [
        "🎲 랜덤 뽑기",
        "🥊 음식 월드컵"
    ]
)


# =========================================================
# 14. 랜덤 메뉴 뽑기
# =========================================================

with game_tab1:

    st.subheader(
        "🎰 오늘의 랜덤 메뉴"
    )

    st.write(
        """
        버튼을 누르면 오늘 먹을 메뉴를
        하나 랜덤으로 골라드립니다.
        """
    )


    if food_type != "상관없음":

        st.caption(
            f"현재 **{food_type}** 메뉴에서 뽑습니다."
        )

    else:

        st.caption(
            "모든 음식 종류에서 랜덤으로 뽑습니다."
        )


    game_pool = get_game_menu_pool(
        food_type,
        avoid_food
    )


    if st.button(
        "🎲 운명의 메뉴 뽑기",
        use_container_width=True,
        key="random_food_button"
    ):

        if game_pool:

            st.session_state.random_menu = (
                random.choice(game_pool)
            )

        else:

            st.warning(
                "조건에 맞는 메뉴가 없습니다."
            )


    if "random_menu" in st.session_state:

        random_menu = (
            st.session_state.random_menu
        )


        st.success(
            f"🎉 오늘의 메뉴는 **{random_menu}**!"
        )


        st.markdown(
            f"""
### 🍽️ {random_menu}

오늘은 더 이상 고민 금지!

**오늘 메뉴는 {random_menu}로 결정! 😋**
"""
        )


        if st.button(
            "🔄 다시 뽑기",
            use_container_width=True,
            key="random_food_again"
        ):

            if game_pool:

                st.session_state.random_menu = (
                    random.choice(game_pool)
                )

                st.rerun()


# =========================================================
# 15. 음식 월드컵
# =========================================================

with game_tab2:

    st.subheader(
        "🥊 오늘 뭐 먹지? 음식 월드컵"
    )

    st.write(
        """
        둘 중 더 먹고 싶은 메뉴를 계속 선택하세요.

        마지막까지 살아남은 음식이
        **오늘의 메뉴**가 됩니다. 🏆
        """
    )


    worldcup_pool = get_game_menu_pool(
        food_type,
        avoid_food
    )


    if st.button(
        "🏁 음식 월드컵 시작",
        use_container_width=True,
        key="start_worldcup_button"
    ):

        start_worldcup(
            worldcup_pool
        )

        st.rerun()


    # 오류
    if st.session_state.get(
        "worldcup_error"
    ):

        st.warning(
            st.session_state.worldcup_error
        )


    # =====================================================
    # 우승 메뉴
    # =====================================================

    if st.session_state.get(
        "worldcup_champion"
    ):

        champion = (
            st.session_state.worldcup_champion
        )


        st.balloons()


        st.success(
            "🏆 음식 월드컵 우승!"
        )


        st.markdown(
            f"""
## 🏆 오늘의 최종 메뉴

# 🍽️ {champion}

고민 끝!

**오늘은 {champion} 먹으러 가자! 😋**
"""
        )


        if st.button(
            "🔄 월드컵 다시 시작",
            use_container_width=True,
            key="restart_worldcup_button"
        ):

            start_worldcup(
                worldcup_pool
            )

            st.rerun()


    # =====================================================
    # 월드컵 진행 중
    # =====================================================

    elif (
        "worldcup_contestants"
        in st.session_state
    ):

        contestants = (
            st.session_state.worldcup_contestants
        )


        match_index = (
            st.session_state.worldcup_match_index
        )


        if (
            match_index
            < len(contestants)
        ):

            remaining = len(contestants)


            if remaining == 8:

                round_name = "8강"

            elif remaining == 4:

                round_name = "4강"

            elif remaining == 2:

                round_name = "결승"

            else:

                round_name = (
                    f"{remaining}강"
                )


            match_number = (
                match_index // 2
            ) + 1


            total_matches = (
                len(contestants) // 2
            )


            st.markdown(
                f"""
### 🏟️ {round_name}

**{match_number} / {total_matches} 경기**

둘 중 지금 더 먹고 싶은 음식을 선택하세요.
"""
            )


            menu_a = contestants[
                match_index
            ]

            menu_b = contestants[
                match_index + 1
            ]


            col1, col2 = st.columns(2)


            with col1:

                st.markdown(
                    f"### 🍽️ {menu_a}"
                )


                if st.button(
                    f"👉 {menu_a}",
                    use_container_width=True,
                    key=(
                        f"worldcup_a_"
                        f"{round_name}_"
                        f"{match_index}_"
                        f"{menu_a}"
                    )
                ):

                    choose_worldcup_menu(
                        menu_a
                    )


            with col2:

                st.markdown(
                    f"### 🍽️ {menu_b}"
                )


                if st.button(
                    f"👉 {menu_b}",
                    use_container_width=True,
                    key=(
                        f"worldcup_b_"
                        f"{round_name}_"
                        f"{match_index}_"
                        f"{menu_b}"
                    )
                ):

                    choose_worldcup_menu(
                        menu_b
                    )


# =========================================================
# 16. 음성 질문
# =========================================================

st.divider()

st.header("🎤 말해서 추천받기")

st.write(
    """
    마이크 버튼을 누르고
    지금 먹고 싶은 음식이나 상황을 말해보세요.
    """
)


voice_audio = st.audio_input(
    "🎙️ 음성을 녹음해주세요.",
    sample_rate=16000
)


voice_send = st.button(
    "🎤 음성 질문 보내기",
    use_container_width=True,
    disabled=voice_audio is None
)


# =========================================================
# 17. 글 질문
# =========================================================

typed_prompt = st.chat_input(
    "오늘 뭐 먹을지 말씀해주세요 😋"
)


# =========================================================
# 18. 최종 사용자 질문 결정
# =========================================================

prompt = None

voice_mode = False


# 음성 질문
if (
    voice_send
    and voice_audio is not None
):

    try:

        with st.spinner(
            "🎧 음성을 듣고 있어요..."
        ):

            transcription = (
                client.audio.transcriptions.create(
                    model=TRANSCRIBE_MODEL,
                    file=voice_audio,
                    language="ko"
                )
            )


            prompt = (
                transcription.text.strip()
            )

            voice_mode = True


        if not prompt:

            st.warning(
                "음성을 정확하게 인식하지 못했습니다. 다시 말해주세요."
            )

            prompt = None


    except Exception as e:

        st.error(
            f"음성 인식 중 오류가 발생했습니다: {e}"
        )

        prompt = None


# 글 질문
elif typed_prompt:

    prompt = typed_prompt.strip()

    voice_mode = False


# =========================================================
# 19. 사용자 질문 처리
# =========================================================

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "voice": voice_mode
        }
    )


    # 사용자 메시지 출력
    with st.chat_message("user"):

        if voice_mode:

            st.caption(
                "🎤 음성으로 질문했습니다."
            )


        st.markdown(prompt)


    # =====================================================
    # 현재 메뉴 조건
    # =====================================================

    FOOD_CONTEXT = f"""
현재 사용자가 선택한 메뉴 추천 조건입니다.

식사 시간:
{meal_time}

선호 음식 종류:
{food_type}

누구와 먹는지:
{situation}

식사 방식:
{eating_method}

1인당 예상 예산:
{budget}

매운맛 선호:
{spicy}

배고픔 정도:
{hunger}

현재 기분:
{mood}

먹기 싫거나 먹지 못하는 음식:
{avoid_food if avoid_food else "특별히 없음"}


위 조건과 사용자가 실제 대화에서 말한 내용을
함께 고려해서 메뉴를 추천하세요.

사용자가 대화에서 직접 말한 내용과
선택 조건이 서로 다르면
사용자가 직접 말한 내용을 우선하세요.
"""


    # =====================================================
    # AI에 전달할 대화 기록 만들기
    # =====================================================

    conversation = []


    for message in st.session_state.messages:

        if message.get(
            "exclude_from_model",
            False
        ):

            continue


        if message["role"] in [
            "user",
            "assistant"
        ]:

            conversation.append(
                {
                    "role": message["role"],
                    "content": message["content"]
                }
            )


    # =====================================================
    # AI 메뉴 추천 생성
    # =====================================================

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "🍳 오늘 먹기 좋은 메뉴를 고르고 있어요..."
            ):

                response = (
                    client.responses.create(

                        model=TEXT_MODEL,

                        instructions=(
                            FOOD_SYSTEM_PROMPT
                            + "\n\n"
                            + FOOD_CONTEXT
                        ),

                        input=conversation
                    )
                )


                assistant_response = (
                    response.output_text.strip()
                )


            # 글 답변
            st.markdown(
                assistant_response
            )


            # =================================================
            # 음성 답변 생성
            # =================================================

            audio_bytes = None


            if (
                voice_mode
                and voice_answer
            ):

                try:

                    with st.spinner(
                        "🔊 음성 답변을 만들고 있어요..."
                    ):

                        with (
                            tempfile.NamedTemporaryFile(
                                delete=False,
                                suffix=".mp3"
                            )
                        ) as temp_file:

                            speech_file_path = Path(
                                temp_file.name
                            )


                        # 너무 긴 음성 생성 방지
                        speech_text = (
                            assistant_response[:4000]
                        )


                        with (
                            client.audio.speech
                            .with_streaming_response
                            .create(

                                model=VOICE_MODEL,

                                voice="coral",

                                input=speech_text,

                                instructions=(
                                    "한국어로 자연스럽고 밝게 말하세요. "
                                    "오늘 먹을 메뉴를 추천해주는 "
                                    "친근한 친구처럼 이야기하세요. "
                                    "말하는 속도는 너무 빠르지 않게 해주세요."
                                )
                            )
                        ) as speech_response:

                            speech_response.stream_to_file(
                                speech_file_path
                            )


                        audio_bytes = (
                            speech_file_path.read_bytes()
                        )


                        try:

                            os.remove(
                                speech_file_path
                            )

                        except Exception:

                            pass


                    st.caption(
                        "🔊 아래 음성은 AI가 생성한 음성입니다."
                    )


                    st.audio(
                        audio_bytes,
                        format="audio/mp3",
                        autoplay=True
                    )


                except Exception as e:

                    st.warning(
                        f"음성 답변 생성 중 오류가 발생했습니다: {e}"
                    )


            # =================================================
            # AI 답변 저장
            # =================================================

            assistant_message = {
                "role": "assistant",
                "content": assistant_response,
                "voice": (
                    voice_mode
                    and voice_answer
                )
            }


            if audio_bytes:

                assistant_message[
                    "audio"
                ] = audio_bytes


            st.session_state.messages.append(
                assistant_message
            )


        except Exception as e:

            st.error(
                f"AI 답변 생성 중 오류가 발생했습니다: {e}"
            )
