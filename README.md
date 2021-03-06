# OwnCourse
당신의 코스를 소유하세요.
## 프로젝트 소개
- 유저의 취향과 장소 데이터 분석에 기반한 최적의 일정 코스 추천 어플리케이션 
- 리뷰에 가장 많이 등장하는 맛(Taste), 서비스(Service), 가격(Cost)을 지표로 활용하여 사용자의 취향에 맞는 장소 추천 방식 (TSC)

<img width="1206" alt="온코스 이미지" src="https://user-images.githubusercontent.com/39994337/166482595-f745e024-4244-44ce-bdd5-7b35151801e3.png">

## 기술 스택
    - Python Flask
    - MySQL
    
## 주요 기능
### 1. 코스 API
- 코스 추천 - 사용자의 TSC 타입과 사용자의 입력 값(비용, 반경, 장소 카테고리)를 반영한 코스를 추천 
- 코스 저장 - 추천 받은 코스 중 사용자가 선택한 코스 저장
- 타 사용자의 코스 정보 - 사용자의 TSC 타입과 같은 타 사용자들이 저장한 코스 목록 제공
### 2. 인증 API
- 이메일 회원가입 - 이메일 인증 후 회원가입
- 소셜 로그인
### 3. 사용자 API
- 분위기 키워드 입력 - 회원 가입 시 사용자의 취향에 맞는 분위기 키워드 선택
- TSC 테스트 - 장소 추천시 사용되는 TSC 테스트
### 4. 장소 API
- 장소 제공 - 취향 순, 거리 순, 인기 순으로 정렬하고 장소 카테고리 별로 필터링 한 장소 목록 제공
- 장소 추천 - 사용자의 TSC 타입을 반영한 장소를 추천
- 장소 리뷰 - 특정 장소에 대한 리뷰 등록
### 데이터베이스 구조도
<img width="700" height="500" alt="데이터베이스 구조도" src="https://user-images.githubusercontent.com/39994337/166485701-e48e936f-f3f5-4e5b-a99a-3434cd47ef76.png">

## 기타
    🏆 세종대학교 창의설계경진대회 우수상, 인기상 수상 (2021-2학기)
    🏆 세종대학교 컴퓨터공학과 학술제 최우수상 수상 (2021-2학기)
