# 블로그 유입 검색량 순위 분석 웹사이트

GitHub API와 Google Trends를 활용하여 블로그 플랫폼의 유입 검색량을 분석하고 순위를 보여주는 웹사이트입니다.

## 🚀 주요 기능

### 1. 블로그 플랫폼 순위
- Tistory, Naver Blog, Medium, Velog, GitHub Pages, Daum Blog 등의 순위
- 트래픽 점수, 트렌드 점수, 사용자 수, 성장률을 종합한 순위
- 실시간 대시보드 통계

### 2. GitHub 블로그 저장소 분석
- GitHub 사용자명으로 블로그 관련 저장소 검색
- 저장소별 Stars, Forks, 업데이트 날짜 정보
- 블로그 관련 키워드로 필터링

### 3. Google Trends 트렌드 분석
- 블로그 URL들의 검색 트렌드 분석
- 시계열 차트로 트렌드 시각화
- 관련 검색어 및 인기 키워드 제공

## 🛠️ 기술 스택

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **APIs**: GitHub API, Google Trends API (pytrends)
- **Data Processing**: Pandas, NumPy

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd blog-traffic-analyzer
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (선택사항)
```bash
cp env_example.txt .env
# .env 파일을 편집하여 GitHub 토큰 설정
```

### 5. 애플리케이션 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 🔧 설정

### GitHub API 토큰 (선택사항)
더 높은 API 요청 한도를 위해 GitHub 개인 액세스 토큰을 설정할 수 있습니다:

1. [GitHub Settings > Tokens](https://github.com/settings/tokens)에서 새 토큰 생성
2. `.env` 파일에 토큰 추가:
```
GITHUB_TOKEN=your_token_here
```

## 📊 사용법

### 블로그 순위 확인
1. 메인 페이지에서 자동으로 로드되는 순위 테이블 확인
2. 각 플랫폼의 트래픽 점수, 트렌드 점수, 성장률 비교

### GitHub 분석
1. "GitHub 분석" 섹션에서 사용자명 입력
2. "분석" 버튼 클릭
3. 해당 사용자의 블로그 관련 저장소 목록 확인

### 트렌드 분석
1. "Google Trends 분석" 섹션에서 블로그 URL 입력 (쉼표로 구분)
2. "트렌드 분석" 버튼 클릭
3. 트렌드 차트와 관련 검색어 확인

## 📈 데이터 소스

- **GitHub API**: 사용자 저장소 정보
- **Google Trends API**: 검색 트렌드 데이터
- **가상 데이터**: 순위 및 통계 데이터 (실제 데이터로 교체 가능)

## 🎨 UI/UX 특징

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **현대적인 UI**: Bootstrap 5와 커스텀 CSS
- **인터랙티브 차트**: Chart.js를 활용한 데이터 시각화
- **실시간 피드백**: 로딩 스피너와 알림 시스템
- **스무스 애니메이션**: CSS 트랜지션과 JavaScript 애니메이션

## 🔍 API 엔드포인트

- `GET /api/ranking`: 블로그 플랫폼 순위 데이터
- `GET /api/github/<username>`: GitHub 사용자 저장소 분석
- `GET /api/trends`: 인기 블로그 플랫폼 트렌드
- `POST /api/analyze`: 사용자 정의 블로그 URL 트렌드 분석

## 🚀 배포

### Heroku 배포
```bash
# Procfile 생성
echo "web: gunicorn app:app" > Procfile

# Heroku CLI로 배포
heroku create your-app-name
git push heroku main
```

### Docker 배포
```bash
# Dockerfile 생성 후
docker build -t blog-analyzer .
docker run -p 5000:5000 blog-analyzer
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**참고**: 이 프로젝트는 교육 및 데모 목적으로 제작되었습니다. 실제 프로덕션 환경에서 사용하기 전에 보안 및 성능 최적화를 권장합니다. 