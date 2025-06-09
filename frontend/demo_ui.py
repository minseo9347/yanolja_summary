import streamlit as st
import requests
import json
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="숙소 리뷰 요약 서비스",
    page_icon="🏨",
    layout="wide"
)

# FastAPI 서버 URL 설정
FASTAPI_URL = "http://localhost:8000"  # FastAPI 서버 주소

@st.cache_data(ttl=300)  # 5분간 캐시
def get_accommodation_list():
    """FastAPI에서 숙소 목록을 가져오는 함수"""
    try:
        response = requests.get(f"{FASTAPI_URL}/")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"서버 오류: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("서버에 연결할 수 없습니다. FastAPI 서버가 실행중인지 확인해주세요.")
        return []
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        return []

def get_review_summary(accommodation_id):
    """FastAPI에서 리뷰 요약을 가져오는 함수"""
    print(accommodation_id)
    try:
        response = requests.get(f"{FASTAPI_URL}/review_summary/{accommodation_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None  # 리뷰 요약이 없는 경우
        else:
            st.error(f"리뷰 요약 조회 오류: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("서버에 연결할 수 없습니다. FastAPI 서버가 실행중인지 확인해주세요.")
        return None
    except Exception as e:
        st.error(f"리뷰 요약 조회 중 오류가 발생했습니다: {str(e)}")
        return None

def display_review_summary(summary_data, accommodation_name):
    """리뷰 요약 데이터를 화면에 표시하는 함수"""
    if not summary_data:
        st.warning("이 숙소의 리뷰 요약 데이터가 없습니다.")
        return
    
    # 메인 헤더
    st.markdown(f"## 🏨 {accommodation_name} - 리뷰 요약")
    
    # 메타 정보 표시
    # meta_col1, meta_col2 = st.columns(2)
    # with meta_col1:
    #     st.write(f"**요약 ID:** {summary_data.get('id', 'N/A')}")
    # with meta_col2:
    #     st.write(f"**숙소 ID:** {summary_data.get('accommodation_id', 'N/A')}")
    
    # 날짜 정보
    if summary_data.get('date'):
        try:
            # 날짜 문자열을 파싱하여 표시
            if isinstance(summary_data['date'], str):
                # ISO 형식 날짜 파싱 시도
                date_str = summary_data['date'].replace('Z', '+00:00')
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str)
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y년 %m월 %d일')
            else:
                formatted_date = str(summary_data['date'])
            st.caption(f"📅 요약 생성일: {formatted_date}")
        except Exception as e:
            st.caption(f"📅 요약 생성일: {summary_data['date']}")
    
    st.divider()
    
    # 두 개의 컬럼으로 좋은 점/아쉬운 점 구분
    good_col, bad_col = st.columns(2)
    
    with good_col:
        st.markdown("### 👍 좋은 점")
        if summary_data.get('summary_good'):
            # 좋은 점을 박스로 표시
            st.success(summary_data['summary_good'])
        else:
            st.info("좋은 점에 대한 요약이 없습니다.")
    
    with bad_col:
        st.markdown("### 👎 아쉬운 점")
        if summary_data.get('summary_bad'):
            # 아쉬운 점을 박스로 표시
            st.warning(summary_data['summary_bad'])
        else:
            st.info("아쉬운 점에 대한 요약이 없습니다.")

# 메인 애플리케이션 시작
def main():
    # 메인 제목
    st.title("🏨 숙소 리뷰 요약 서비스")
    st.markdown("AI가 분석한 숙소 리뷰 요약을 확인해보세요!")
    
    st.divider()
    
    # 숙소 목록 로드
    with st.spinner("숙소 목록을 불러오는 중..."):
        accommodation_list = get_accommodation_list()
    
    if not accommodation_list:
        st.error("숙소 목록을 불러올 수 없습니다.")
        st.info("FastAPI 서버(http://localhost:8000)가 실행중인지 확인해주세요.")
        return
    
    # 레이아웃 구성
    selection_col, info_col = st.columns([1.2, 0.8])
    
    with selection_col:
        st.subheader("🏠 숙소 선택")
        
        # 숙소 선택 드롭다운
        accommodation_options = {f"{item['name']}": item for item in accommodation_list}
        selected_option = st.selectbox(
            "숙소를 선택하세요:",
            list(accommodation_options.keys()),
            index=0
        )
        
        selected_accommodation = accommodation_options[selected_option]
        
        # 공간 추가
        st.write("")
        
        # 리뷰 요약하기 버튼
        if st.button("📊 리뷰 요약 조회", use_container_width=True, type="primary"):
            with st.spinner(f"'{selected_accommodation['name']}' 리뷰 요약을 조회하는 중..."):
                # 리뷰 요약 API 호출
                review_summary = get_review_summary(selected_accommodation['id'])
                
                # 세션 상태에 결과 저장
                st.session_state['current_summary'] = review_summary
                st.session_state['current_accommodation'] = selected_accommodation
                
                # 결과에 따른 메시지 표시
                if review_summary:
                    st.success(f"✅ '{selected_accommodation['name']}' 리뷰 요약을 성공적으로 조회했습니다!")
                else:
                    st.warning(f"⚠️ '{selected_accommodation['name']}'의 리뷰 요약 데이터가 없습니다.")
    
    with info_col:
        st.subheader("📍 선택된 숙소")
        
        if selected_accommodation:
            with st.container():
                st.write(f"**숙소 이름:** {selected_accommodation['name']}")
        
        # 안내 정보
        st.info("💡 왼쪽에서 숙소를 선택하고 '리뷰 요약 조회' 버튼을 클릭하세요.")
    
    # 리뷰 요약 결과 표시 섹션
    if 'current_summary' in st.session_state and st.session_state.get('current_summary'):
        st.divider()
        
        current_accommodation = st.session_state.get('current_accommodation', {})
        
        # 리뷰 요약 표시
        display_review_summary(
            st.session_state['current_summary'], 
            current_accommodation.get('name', '알 수 없는 숙소')
        )
        
        # 액션 버튼들
        action_col1, action_col2, action_col3 = st.columns([1, 1, 1])
        
        with action_col2:
            if st.button("🗑️ 결과 지우기", use_container_width=True):
                # 세션 상태 초기화
                if 'current_summary' in st.session_state:
                    del st.session_state['current_summary']
                if 'current_accommodation' in st.session_state:
                    del st.session_state['current_accommodation']
                st.rerun()
    
    # 하단 안내 정보 (리뷰 요약이 표시되지 않을 때만)
    if 'current_summary' not in st.session_state or not st.session_state.get('current_summary'):
        st.divider()
        
        # 3개 컬럼으로 하단 정보 표시
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.info("🔍 **AI 리뷰 요약**\n\n다양한 리뷰를 분석해서 핵심 내용을 요약해드립니다")
        
        with info_col2:
            st.info("⭐ **장단점 분석**\n\n좋은 점과 아쉬운 점을 명확하게 구분해서 보여드립니다")
        
        with info_col3:
            st.info("📝 **빠른 파악**\n\n긴 리뷰들을 읽지 않아도 핵심 정보를 빠르게 확인하세요")

# 사이드바 - 디버그 및 관리 도구
def sidebar():
    st.sidebar.title("🔧 관리 도구")
    
    # 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        if 'current_summary' in st.session_state:
            del st.session_state['current_summary']
        if 'current_accommodation' in st.session_state:
            del st.session_state['current_accommodation']
        st.rerun()
    
    st.sidebar.divider()
    
    # 디버그 정보
    if st.sidebar.checkbox("🐛 디버그 모드", value=False):
        st.sidebar.write("**서버 정보:**")
        st.sidebar.code(f"FastAPI URL: {FASTAPI_URL}")
        
        # 숙소 목록 정보
        accommodation_list = get_accommodation_list()
        st.sidebar.write("**숙소 목록:**")
        if accommodation_list:
            for idx, accommodation in enumerate(accommodation_list, 1):
                st.sidebar.write(f"{idx}. {accommodation['name']} (ID: {accommodation['id']})")
        else:
            st.sidebar.write("❌ 숙소 목록 없음")
        
        # 세션 상태 정보
        st.sidebar.write("**세션 상태:**")
        if 'current_summary' in st.session_state:
            st.sidebar.write("✅ 리뷰 요약 데이터 있음")
            summary = st.session_state['current_summary']
            st.sidebar.json({
                "id": summary.get('id'),
                "accommodation_id": summary.get('accommodation_id'),
                "has_good_summary": bool(summary.get('summary_good')),
                "has_bad_summary": bool(summary.get('summary_bad')),
                "date": summary.get('date')
            })
        else:
            st.sidebar.write("❌ 리뷰 요약 데이터 없음")
    
    # 도움말
    st.sidebar.divider()
    st.sidebar.markdown("""
    ### 📖 사용 방법
    1. 숙소를 선택합니다
    2. '리뷰 요약 조회' 버튼을 클릭합니다
    3. AI가 분석한 리뷰 요약을 확인합니다
    
    ### ⚠️ 문제 해결
    - 서버 연결 오류: FastAPI 서버 실행 확인
    - 데이터 없음: 해당 숙소의 리뷰 요약 데이터 확인
    """)

# 애플리케이션 실행
if __name__ == "__main__":
    sidebar()
    main()