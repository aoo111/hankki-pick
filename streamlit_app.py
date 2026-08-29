import streamlit as st
from openai import OpenAI
from pathlib import Path
import tempfile
import random
import os
import re


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="오늘 뭐 먹지?",
    page_icon="🍽️",
    layout="centered"
)


# =========================================================
# 2. 이미지 폴더 설정
# =========================================================

IMAGE_FOLDER = Path("images")


# =========================================================
# 3. 음식 이미지 연결
# =========================================================

FOOD_IMAGES = {

    # 한식
    "김치찌개": "kimchi_stew.png",
    "순두부찌개": "sundubu.png",
    "제육볶음": "jeyuk.png",
    "닭갈비": "dakgalbi.png",
    "삼겹살": "samgyeopsal.png",
    "비빔밥": "bibimbap.png",
    "국밥": "gukbap.png",

    # 분식
    "떡볶이": "tteokbokki.png",
    "김밥": "gimbap.png",

    # 중식
    "짜장면": "jjajangmyeon.png",
    "짬뽕": "jjamppong.png",
    "마라탕": "malatang.png",

    # 일식
    "돈까스": "donkatsu.png",
    "초밥": "sushi.png",
    "라멘": "ramen.png",

    # 양식
    "토마토 파스타": "pasta.png",
    "크림 파스타": "pasta.png",
    "알리오 올리오": "pasta.png",
    "파스타": "pasta.png",
    "피자": "pizza.png",

    # 패스트푸드
    "햄버거": "burger.png",
    "치킨": "chicken.png",

    # 아시아
    "쌀국수": "pho.png",
    "팟타이": "padthai.png",

    # 건강식
    "포케": "poke.png",
    "샐러드": "salad.png",
    "닭가슴살 샐러드": "salad.png",
    "연어 샐러드": "salad.png"
}


# =========================================================
# 4. 카테고리 대표 이미지
# =========================================================

CATEGORY_IMAGES = {

    "한식": "category_korean.png",

    "중식": "category_chinese.png",

    "일식": "category_japanese.png",

    "양식": "category_western.png",

    "분식": "category_snack.png",

    "아시아 음식": "category_asian.png",

    "패스트푸드": "category_fastfood.png",

    "샐러드 / 건강식": "category_healthy.png"
}


# =========================================================
# 5. 이미지 관련 함수
# =========================================================

def get_image_path(filename):

    path = IMAGE_FOLDER / filename

    if path.exists():
        return path

    return None


def get_food_image(menu_name):

    # 메뉴 이름과 정확하게 일치
    if menu_name in FOOD_IMAGES:

        path = get_image_path(
            FOOD_IMAGES[menu_name]
        )

        if path:
            return path


    # AI 답변에서 메뉴명이 조금 길어진 경우
    for food_name, filename in FOOD_IMAGES.items():

        if food_name in menu_name:

            path = get_image_path(filename)

            if path:
                return path


    # 기본 이미지
    default_path = get_image_path(
        "default_food.png"
    )

    return default_path


def show_food_image(
    menu_name,
    width=300
):

    image_path = get_food_image(
        menu_name
    )

    if image_path:

        st.image(
            str(image_path),
            width=width
        )


def show_category_image(
    category
):

    if category in CATEGORY_IMAGES:

        image_path = get_image_path(
            CATEGORY_IMAGES[category]
        )

        if image_path:

            st.image(
                str(image_path),
                use_container_width=True
            )


# =========================================================
# 6. 상단 배너
# =========================================================

st.title("🍽️ 오늘 뭐 먹지?")


banner_path = get_image_path(
    "main_banner.png"
)


if banner_path:

    st.image(
        str(banner_path),
        use_container_width=True
    )


st.write(
    """
    오늘 메뉴가 고민된다면 이제 그만 고민하세요! 😋

    **AI 추천, 음성 추천, 랜덤 뽑기, 음식 월드컵**

    원하는 방법으로 오늘의 메뉴를 결정해보세요.
    """
)


# =========================================================
# 7. OpenAI API KEY
# =========================================================

try:

    openai_api_key = st.secrets[
        "OPENAI_API_KEY"
    ]


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
# 8. AI 모델
# =========================================================

TEXT_MODEL = "gpt-5.6-luna"

TRANSCRIBE_MODEL = (
    "gpt-4o-mini-transcribe"
)

VOICE_MODEL = (
    "gpt-4o-mini-tts"
)


# =========================================================
# 9. 음식 데이터
# =========================================================

MENU_DATA = {

    "한식": [

        "김치찌개",
        "순두부찌개",
        "제육볶음",
        "닭갈비",
        "삼겹살",
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
        "마라탕",
        "마라샹궈",
        "유린기",
        "양꼬치"
    ],


    "일식": [

        "돈까스",
        "초밥",
        "우동",
        "라멘",
        "규동",
        "가츠동",
        "카레",
        "소바"
    ],


    "양식": [

        "토마토 파스타",
        "크림 파스타",
        "알리오 올리오",
        "리조또",
        "피자",
        "스테이크",
        "라자냐",
        "함박스테이크"
    ],


    "분식": [

        "떡볶이",
        "김밥",
        "라면",
        "순대",
        "튀김",
        "쫄면",
        "라볶이"
    ],


    "아시아 음식": [

        "쌀국수",
        "팟타이",
        "분짜",
        "나시고랭",
        "반미",
        "인도 카레"
    ],


    "패스트푸드": [

        "햄버거",
        "치킨",
        "핫도그",
        "치킨버거",
        "샌드위치",
        "피자"
    ],


    "샐러드 / 건강식": [

        "닭가슴살 샐러드",
        "연어 샐러드",
        "포케",
        "두부 샐러드",
        "샌드위치",
        "월남쌈"
    ]
}


# =========================================================
# 10. 모든 메뉴 리스트
# =========================================================

ALL_MENUS = []


for category_menus in MENU_DATA.values():

    for menu in category_menus:

        if menu not in ALL_MENUS:

            ALL_MENUS.append(
                menu
            )


# =========================================================
# 11. AI 시스템 프롬프트
# =========================================================

FOOD_SYSTEM_PROMPT = """
당신은 사용자가 오늘 먹을 음식을 결정하도록 도와주는
친근하고 센스 있는 AI 메뉴 추천 전문가입니다.

사용자의 상황과 취향을 분석해서
오늘 가장 잘 어울리는 메뉴를 추천하세요.


[고려해야 할 정보]

1. 식사 시간
2. 음식 종류
3. 혼밥 또는 동행 여부
4. 배달 / 외식 / 포장 / 집밥
5. 예산
6. 매운맛 선호
7. 배고픔
8. 현재 기분
9. 싫어하거나 먹지 못하는 음식
10. 이전에 이미 먹은 음식


[답변 형식]

가능하면 메뉴를 3개 추천합니다.


### 🥇 오늘의 1순위

메뉴 이름

추천 이유


### 🥈 2순위

메뉴 이름

추천 이유


### 🥉 3순위

메뉴 이름

추천 이유


마지막에는 반드시 아래 형태로 답하세요.

🍽️ 오늘 하나만 고른다면: 메뉴 이름


[중요]

- 최종 메뉴는 하나를 확실하게 결정하세요.
- 너무 많은 메뉴를 나열하지 마세요.
- 싫어하는 음식은 제외하세요.
- 먹지 못하는 음식은 반드시 제외하세요.
- 이미 먹었다고 한 메뉴는 가급적 제외하세요.
- 실제 존재 여부를 확인하지 않은 식당 이름은 만들지 마세요.
- 위치나 날씨를 확인하지 않았다면 추측하지 마세요.
- 자연스러운 한국어를 사용하세요.
- 설명은 너무 길지 않게 하세요.
"""


# =========================================================
# 12. 처음 메시지
# =========================================================

WELCOME_MESSAGE = """
안녕하세요! 🍽️

오늘 **뭐 먹을지 고민 중이신가요?**

원하는 방법으로 메뉴를 골라보세요.

💬 **AI에게 추천받기**

🎤 **말해서 추천받기**

🎲 **랜덤으로 뽑기**

🥊 **음식 월드컵**

예를 들어

**"오늘 스트레스 받았는데 매콤한 거 먹고 싶어"**

처럼 편하게 말해주세요. 😋
"""


if "messages" not in st.session_state:

    st.session_state.messages = [

        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "exclude_from_model": True
        }

    ]


# =========================================================
# 13. 게임 메뉴 생성
# =========================================================

def get_game_menu_pool(
    food_type,
    avoid_food
):

    if food_type in MENU_DATA:

        menu_pool = MENU_DATA[
            food_type
        ].copy()

    else:

        menu_pool = ALL_MENUS.copy()


    if avoid_food:

        avoid_words = [

            word.strip()

            for word in
            avoid_food.replace(
                "/",
                ","
            ).split(",")

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

                filtered_pool.append(
                    menu
                )


        menu_pool = filtered_pool


    return menu_pool


# =========================================================
# 14. 음식 월드컵 시작
# =========================================================

def start_worldcup(
    menu_pool
):

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


    st.session_state.worldcup_contestants = (
        contestants
    )

    st.session_state.worldcup_winners = []

    st.session_state.worldcup_match_index = 0

    st.session_state.worldcup_champion = None

    st.session_state.worldcup_error = None


# =========================================================
# 15. 월드컵 선택
# =========================================================

def choose_worldcup_menu(
    winner
):

    st.session_state.worldcup_winners.append(
        winner
    )


    st.session_state.worldcup_match_index += 2


    contestants = (
        st.session_state.worldcup_contestants
    )


    if (
        st.session_state.worldcup_match_index
        >= len(contestants)
    ):

        winners = (
            st.session_state.worldcup_winners.copy()
        )


        if len(winners) == 1:

            st.session_state.worldcup_champion = (
                winners[0]
            )


        else:

            st.session_state.worldcup_contestants = (
                winners
            )

            st.session_state.worldcup_winners = []

            st.session_state.worldcup_match_index = 0


    st.rerun()


# =========================================================
# 16. AI 답변에서 최종 메뉴 추출
# =========================================================

def extract_final_menu(
    response_text
):

    marker = (
        "오늘 하나만 고른다면:"
    )


    if marker not in response_text:

        return None


    result = response_text.split(
        marker
    )[-1]


    result = result.split(
        "\n"
    )[0]


    # 마크다운 제거
    result = re.sub(
        r"[*_#`]",
        "",
        result
    )


    result = result.replace(
        "🍽️",
        ""
    )


    return result.strip()


# =========================================================
# 17. 사이드바
# =========================================================

with st.sidebar:

    st.header(
        "🍴 오늘의 식사 설정"
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


    # =============================================
    # 카테고리 대표 이미지
    # =============================================

    if food_type != "상관없음":

        show_category_image(
            food_type
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
        "💰 1인당 예산",
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
        "🍖 배고픔",
        options=[
            "가볍게",
            "보통",
            "든든하게",
            "엄청 배고픔"
        ],
        value="보통"
    )


    mood = st.selectbox(
        "😊 지금 기분",
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
        placeholder="예: 해산물, 치즈"
    )


    st.divider()


    st.subheader(
        "🔊 음성 설정"
    )


    voice_answer = st.toggle(
        "음성 질문에 음성으로 답하기",
        value=True
    )


    st.caption(
        "음성은 AI가 생성한 음성입니다."
    )


    st.divider()


    if st.button(
        "🗑️ 처음부터 다시 시작",
        use_container_width=True
    ):

        st.session_state.messages = [

            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
                "exclude_from_model": True
            }

        ]


        reset_keys = [

            "random_menu",

            "worldcup_contestants",

            "worldcup_winners",

            "worldcup_match_index",

            "worldcup_champion",

            "worldcup_error"
        ]


        for key in reset_keys:

            if key in st.session_state:

                del st.session_state[key]


        st.rerun()


# =========================================================
# 18. 현재 조건
# =========================================================

with st.expander(
    "🍴 현재 선택한 조건"
):

    st.write(
        f"**시간:** {meal_time}"
    )

    st.write(
        f"**종류:** {food_type}"
    )

    st.write(
        f"**누구와:** {situation}"
    )

    st.write(
        f"**방법:** {eating_method}"
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
# 19. 기존 채팅 출력
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        if (
            message["role"] == "user"
            and message.get(
                "voice",
                False
            )
        ):

            st.caption(
                "🎤 음성으로 질문했습니다."
            )


        st.markdown(
            message["content"]
        )


        # AI 최종 추천 음식 이미지
        if message.get(
            "final_menu"
        ):

            show_food_image(
                message["final_menu"],
                width=300
            )


        # 음성 답변
        if message.get(
            "audio"
        ):

            st.audio(
                message["audio"],
                format="audio/mp3"
            )


# =========================================================
# 20. 메뉴 게임
# =========================================================

st.divider()

st.header(
    "🎮 메뉴 결정 게임"
)


game_tab1, game_tab2 = st.tabs(
    [
        "🎲 랜덤 뽑기",
        "🥊 음식 월드컵"
    ]
)


# =========================================================
# 21. 랜덤 메뉴
# =========================================================

with game_tab1:

    st.subheader(
        "🎰 운명의 메뉴 뽑기"
    )


    st.write(
        "고민하기 귀찮다면 운명에 맡겨보세요!"
    )


    game_pool = get_game_menu_pool(
        food_type,
        avoid_food
    )


    if food_type != "상관없음":

        st.caption(
            f"현재 {food_type} 메뉴 중에서 뽑습니다."
        )


    if st.button(
        "🎲 오늘의 메뉴 뽑기",
        use_container_width=True,
        key="random_button"
    ):

        if game_pool:

            st.session_state.random_menu = (
                random.choice(
                    game_pool
                )
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
            f"🎉 오늘의 메뉴는 {random_menu}!"
        )


        # =============================================
        # 랜덤 결과 이미지
        # =============================================

        show_food_image(
            random_menu,
            width=350
        )


        st.markdown(
            f"""
## 🍽️ {random_menu}

오늘은 고민 그만!

**{random_menu}로 결정! 😋**
"""
        )


        if st.button(
            "🔄 다시 뽑기",
            use_container_width=True,
            key="random_again"
        ):

            if game_pool:

                st.session_state.random_menu = (
                    random.choice(
                        game_pool
                    )
                )

                st.rerun()


# =========================================================
# 22. 음식 월드컵
# =========================================================

with game_tab2:

    st.subheader(
        "🥊 음식 월드컵"
    )


    st.write(
        """
        둘 중 더 먹고 싶은 음식을 선택하세요.

        마지막까지 살아남은 음식이 오늘의 메뉴입니다. 🏆
        """
    )


    worldcup_pool = get_game_menu_pool(
        food_type,
        avoid_food
    )


    if st.button(
        "🏁 음식 월드컵 시작",
        use_container_width=True,
        key="worldcup_start"
    ):

        start_worldcup(
            worldcup_pool
        )

        st.rerun()


    if st.session_state.get(
        "worldcup_error"
    ):

        st.warning(
            st.session_state.worldcup_error
        )


    # =====================================================
    # 월드컵 우승
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


        # 우승 음식 이미지
        show_food_image(
            champion,
            width=400
        )


        st.markdown(
            f"""
# 🍽️ {champion}

고민 끝!

**오늘은 {champion} 먹는 날! 😋**
"""
        )


        if st.button(
            "🔄 다시 월드컵",
            use_container_width=True,
            key="worldcup_again"
        ):

            start_worldcup(
                worldcup_pool
            )

            st.rerun()


    # =====================================================
    # 월드컵 진행
    # =====================================================

    elif (
        "worldcup_contestants"
        in st.session_state
    ):

        contestants = (
            st.session_state.worldcup_contestants
        )


        index = (
            st.session_state.worldcup_match_index
        )


        if index < len(contestants):

            remaining = len(
                contestants
            )


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


            st.markdown(
                f"## 🏟️ {round_name}"
            )


            menu_a = contestants[
                index
            ]

            menu_b = contestants[
                index + 1
            ]


            col1, col2 = st.columns(
                2
            )


            # =============================================
            # 왼쪽 음식
            # =============================================

            with col1:

                st.markdown(
                    f"### 🍽️ {menu_a}"
                )


                # 음식 이미지
                show_food_image(
                    menu_a,
                    width=250
                )


                if st.button(
                    f"👉 {menu_a}",
                    use_container_width=True,
                    key=(
                        f"a_{round_name}_"
                        f"{index}_{menu_a}"
                    )
                ):

                    choose_worldcup_menu(
                        menu_a
                    )


            # =============================================
            # 오른쪽 음식
            # =============================================

            with col2:

                st.markdown(
                    f"### 🍽️ {menu_b}"
                )


                # 음식 이미지
                show_food_image(
                    menu_b,
                    width=250
                )


                if st.button(
                    f"👉 {menu_b}",
                    use_container_width=True,
                    key=(
                        f"b_{round_name}_"
                        f"{index}_{menu_b}"
                    )
                ):

                    choose_worldcup_menu(
                        menu_b
                    )


# =========================================================
# 23. 음성 입력
# =========================================================

st.divider()

st.header(
    "🎤 말해서 추천받기"
)


st.write(
    "먹고 싶은 음식이나 현재 상황을 말해주세요."
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
# 24. 글 입력
# =========================================================

typed_prompt = st.chat_input(
    "오늘 뭐 먹을지 말씀해주세요 😋"
)


prompt = None

voice_mode = False


# =========================================================
# 25. 음성 → 글 변환
# =========================================================

if (
    voice_send
    and voice_audio is not None
):

    try:

        with st.spinner(
            "🎧 목소리를 듣고 있어요..."
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


    except Exception as e:

        st.error(
            f"음성 인식 오류: {e}"
        )


elif typed_prompt:

    prompt = (
        typed_prompt.strip()
    )


# =========================================================
# 26. 질문 처리
# =========================================================

if prompt:

    st.session_state.messages.append(

        {
            "role": "user",
            "content": prompt,
            "voice": voice_mode
        }

    )


    with st.chat_message(
        "user"
    ):

        if voice_mode:

            st.caption(
                "🎤 음성 질문"
            )


        st.markdown(
            prompt
        )


    # =====================================================
    # 사용자 조건
    # =====================================================

    FOOD_CONTEXT = f"""
현재 사용자의 식사 조건입니다.

식사 시간:
{meal_time}

음식 종류:
{food_type}

누구와 먹는지:
{situation}

식사 방식:
{eating_method}

예산:
{budget}

매운맛:
{spicy}

배고픔:
{hunger}

현재 기분:
{mood}

제외 음식:
{avoid_food if avoid_food else "없음"}

사용자가 직접 대화에서 말한 내용이 있다면
선택 메뉴보다 대화 내용을 우선하세요.

가능하면 일반적으로 알려진 구체적인 메뉴명을 사용하세요.
"""


    # =====================================================
    # 대화 기록
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
    # AI 답변
    # =====================================================

    with st.chat_message(
        "assistant"
    ):

        try:

            # =============================================
            # 귀여운 로딩 이미지
            # =============================================

            loading_placeholder = (
                st.empty()
            )


            loading_path = get_image_path(
                "loading_food.png"
            )


            if loading_path:

                loading_placeholder.image(
                    str(loading_path),
                    width=140
                )


            with st.spinner(
                "🍳 맛있는 메뉴를 고민하고 있어요..."
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


            # 로딩 이미지 제거
            loading_placeholder.empty()


            # =============================================
            # AI 답변 출력
            # =============================================

            st.markdown(
                assistant_response
            )


            # =============================================
            # 최종 추천 메뉴 찾기
            # =============================================

            final_menu = extract_final_menu(
                assistant_response
            )


            # =============================================
            # 최종 추천 메뉴 이미지
            # =============================================

            if final_menu:

                st.markdown(
                    "### 🖼️ 오늘의 추천 메뉴"
                )


                show_food_image(
                    final_menu,
                    width=350
                )


            # =============================================
            # 음성 답변
            # =============================================

            audio_bytes = None


            if (
                voice_mode
                and voice_answer
            ):

                try:

                    with st.spinner(
                        "🔊 음성 답변을 만들고 있어요..."
                    ):

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".mp3"
                        ) as temp_file:

                            speech_file_path = Path(
                                temp_file.name
                            )


                        speech_text = (
                            assistant_response[
                                :4000
                            ]
                        )


                        with (
                            client.audio.speech
                            .with_streaming_response
                            .create(

                                model=VOICE_MODEL,

                                voice="coral",

                                input=speech_text,

                                instructions=(
                                    "자연스럽고 밝은 한국어로 말하세요. "
                                    "친구가 오늘 메뉴를 골라주는 것처럼 "
                                    "따뜻하고 재미있게 말하세요."
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
                        "🔊 AI가 생성한 음성입니다."
                    )


                    st.audio(
                        audio_bytes,
                        format="audio/mp3",
                        autoplay=True
                    )


                except Exception as e:

                    st.warning(
                        f"음성 생성 오류: {e}"
                    )


            # =============================================
            # 답변 저장
            # =============================================

            assistant_message = {

                "role": "assistant",

                "content": assistant_response,

                "final_menu": final_menu
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
                f"AI 답변 생성 오류: {e}"
            )
