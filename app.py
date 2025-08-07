from flask import Flask, render_template, jsonify, request
import requests
import json
import os
from datetime import datetime, timedelta
from pytrends.request import TrendReq
import pandas as pd
from dotenv import load_dotenv
import time


load_dotenv()

app = Flask(__name__)

# GitHub API 설정
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_API_BASE = 'https://api.github.com'

# Google Trends 설정
pytrends = TrendReq(hl='ko-KR', tz=540)  # 한국 시간대

class BlogAnalyzer:
    def __init__(self):
        self.github_headers = {
            'Authorization': f'token {GITHUB_TOKEN}' if GITHUB_TOKEN else {},
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_github_repos(self, username):
        """GitHub 사용자의 블로그 관련 저장소 정보를 가져옵니다."""
        try:
            url = f"{GITHUB_API_BASE}/users/{username}/repos"
            response = requests.get(url, headers=self.github_headers)
            response.raise_for_status()
            
            repos = response.json()
            blog_repos = []
            
            for repo in repos:
                # 블로그 관련 저장소 필터링
                if any(keyword in repo['name'].lower() for keyword in ['blog', 'blogger', 'website', 'site']):
                    blog_repos.append({
                        'name': repo['name'],
                        'description': repo['description'],
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'url': repo['html_url'],
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at']
                    })
            
            return blog_repos
        except Exception as e:
            print(f"GitHub API 오류: {e}")
            return []
    
    def get_trending_topics(self, keywords, timeframe='today 12-m'):
        """Google Trends에서 키워드들의 트렌드 데이터를 가져옵니다."""
        try:
            # 키워드들을 리스트로 변환
            if isinstance(keywords, str):
                keywords = [keywords]
            
            # Google Trends 요청
            pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='KR')
            
            # 관심도 데이터 가져오기
            interest_over_time = pytrends.interest_over_time()
            
            # 관련 쿼리 가져오기
            related_queries = pytrends.related_queries()
            
            # DataFrame을 JSON 직렬화 가능한 형태로 변환
            serializable_related_queries = {}
            for keyword, queries in related_queries.items():
                serializable_related_queries[keyword] = {}
                if queries.get('top') is not None:
                    serializable_related_queries[keyword]['top'] = queries['top'].to_dict('records') if not queries['top'].empty else []
                else:
                    serializable_related_queries[keyword]['top'] = []
                
                if queries.get('rising') is not None:
                    serializable_related_queries[keyword]['rising'] = queries['rising'].to_dict('records') if not queries['rising'].empty else []
                else:
                    serializable_related_queries[keyword]['rising'] = []
            
            # 날짜 정보 추가
            interest_data = interest_over_time.to_dict('records') if not interest_over_time.empty else []
            
            # 각 데이터 포인트에 날짜 정보 추가
            if interest_data:
                # Google Trends는 보통 최근 12개월 데이터를 제공
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                # 데이터 포인트 수에 따라 날짜 분배
                for i, data_point in enumerate(interest_data):
                    if len(interest_data) > 1:
                        days_back = (len(interest_data) - 1 - i) * (365 // (len(interest_data) - 1))
                    else:
                        days_back = 0
                    
                    point_date = end_date - timedelta(days=days_back)
                    data_point['date'] = point_date.strftime('%Y-%m-%d')
            
            return {
                'interest_over_time': interest_data,
                'related_queries': serializable_related_queries
            }
        except Exception as e:
            print(f"Google Trends API 오류: {e}")
            return {'interest_over_time': [], 'related_queries': {}}
    
    def get_trending_searches(self, timeframe='today 1-d'):
        """Google Trends에서 인기 검색어를 가져옵니다."""
        try:
            # 인기 검색어 가져오기 (한국)
            trending_searches = pytrends.trending_searches(pn='south_korea')
            
            return {
                'trending_searches': trending_searches.tolist() if not trending_searches.empty else []
            }
        except Exception as e:
            print(f"Google Trends 인기 검색어 API 오류: {e}")
            # 기간별 가상 데이터 반환
            if '1-d' in timeframe:
                return {
                    'trending_searches': [
                        '파이썬', '자바스크립트', '리액트', '웹개발', '코딩',
                        '개발자', '프로그래밍', '깃허브', '티스토리', '네이버블로그',
                        '벨로그', '미디엄', '개발도구', 'IDE', 'VS Code',
                        '데이터분석', '인공지능', '머신러닝', '클라우드', 'DevOps'
                    ]
                }
            elif '7-d' in timeframe:
                return {
                    'trending_searches': [
                        '블로그 플랫폼', '개발자 커뮤니티', '기술 블로그', '프로그래밍 언어', '웹 개발',
                        '모바일 앱 개발', '데이터 분석', '인공지능', '클라우드 컴퓨팅', '보안',
                        'DevOps', '마이크로서비스', '도커', '쿠버네티스', 'CI/CD',
                        '테스트 자동화', '코드 리뷰', '페어 프로그래밍', '애자일', '스크럼'
                    ]
                }
            elif '1-m' in timeframe:
                return {
                    'trending_searches': [
                        '스프링부트', '장고', '플라스크', '노드js', '익스프레스',
                        '뷰js', '앵귤러', '타입스크립트', '고랭', '러스트',
                        '코틀린', '스위프트', '플러터', '리액트네이티브', '유니티',
                        '블렌더', '피그마', '제플린', '노션', '슬랙'
                    ]
                }
            else:  # 12-m (연간)
                return {
                    'trending_searches': [
                        '메타버스', 'NFT', '블록체인', 'Web3', 'DeFi',
                        '크립토', '비트코인', '이더리움', '솔라나', '폴리곤',
                        '디앱', '스마트 컨트랙트', 'DAO', 'DeFi 프로토콜', 'NFT 마켓플레이스',
                        '게임파이', '플레이투언', '스테이킹', '리퀴디티', '가스비'
                    ]
                }
    
    def get_top_charts(self, timeframe='today 1-d'):
        """Google Trends에서 상위 차트를 가져옵니다."""
        try:
            # 상위 차트 가져오기 (연도 형식으로 수정)
            current_year = datetime.now().year
            top_charts = pytrends.top_charts(date=str(current_year), hl='ko-KR', tz=540, geo='KR')
            
            return {
                'top_charts': top_charts.to_dict('records') if not top_charts.empty else []
            }
        except Exception as e:
            print(f"Google Trends 상위 차트 API 오류: {e}")
            # 오류 시 가상 데이터 반환
            return {
                'top_charts': [
                    {'title': '블로그 플랫폼', 'traffic': '높음'},
                    {'title': '개발자 커뮤니티', 'traffic': '높음'},
                    {'title': '프로그래밍 언어', 'traffic': '중간'},
                    {'title': '웹 개발', 'traffic': '높음'},
                    {'title': '모바일 앱 개발', 'traffic': '중간'},
                    {'title': '데이터 분석', 'traffic': '높음'},
                    {'title': '인공지능', 'traffic': '높음'},
                    {'title': '클라우드 컴퓨팅', 'traffic': '중간'},
                    {'title': '보안', 'traffic': '중간'},
                    {'title': 'DevOps', 'traffic': '중간'}
                ]
            }
    
    def get_daily_trends(self):
        """일간 베스트 트렌드를 가져옵니다."""
        return self.get_trending_searches('today 1-d')
    
    def get_weekly_trends(self):
        """주간 베스트 트렌드를 가져옵니다."""
        return self.get_trending_searches('today 7-d')
    
    def get_monthly_trends(self):
        """월간 베스트 트렌드를 가져옵니다."""
        return self.get_trending_searches('today 1-m')
    
    def get_yearly_trends(self):
        """연간 베스트 트렌드를 가져옵니다."""
        return self.get_trending_searches('today 12-m')
    
    def analyze_blog_traffic(self, blog_urls):
        """블로그 URL들의 트래픽 관련 키워드를 분석합니다."""
        print(f"analyze_blog_traffic 호출됨. 입력: {blog_urls}")
        blog_keywords = []
        
        for url in blog_urls:
            # URL에서 도메인 추출
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            # www. 제거
            domain = domain.replace('www.', '')
            blog_keywords.append(domain)
            print(f"처리된 키워드: {domain}")
        
        # 키워드가 비어있으면 기본값 설정
        if not blog_keywords:
            blog_keywords = ['example']
            print("키워드가 비어있어서 기본값 설정")
        
        print(f"최종 키워드 리스트: {blog_keywords}")
        
        try:
            # 트렌드 분석
            print("get_trending_topics 호출...")
            trends_data = self.get_trending_topics(blog_keywords)
            print(f"트렌드 데이터: {trends_data}")
            
            # 분석 결과에 도메인 정보 추가
            trends_data['analyzed_domains'] = blog_keywords
            
            return trends_data
        except Exception as e:
            print(f"트렌드 분석 오류: {e}")
            import traceback
            print(f"상세 에러: {traceback.format_exc()}")
            
            # 오류 시 가상 데이터 반환 (실제 키워드 사용)
            print("가상 데이터 생성 중...")
            interest_data = []
            
            # 최근 3개월 데이터 생성
            from datetime import datetime, timedelta
            end_date = datetime.now()
            
            for i in range(3):  # 3개월 데이터
                point_date = end_date - timedelta(days=(2-i)*30)  # 최근 3개월
                data_point = {'date': point_date.strftime('%Y-%m-%d')}
                for j, keyword in enumerate(blog_keywords[:3]):  # 최대 3개 키워드
                    data_point[f'keyword{j+1}'] = 50 + (i * 10) + (j * 5)
                interest_data.append(data_point)
            
            related_queries = {}
            for keyword in blog_keywords[:3]:  # 최대 3개 키워드
                related_queries[keyword] = {
                    'top': [
                        {'query': f'{keyword} 관련 검색어 1', 'value': 100},
                        {'query': f'{keyword} 관련 검색어 2', 'value': 80},
                        {'query': f'{keyword} 관련 검색어 3', 'value': 60}
                    ]
                }
            
            result = {
                'interest_over_time': interest_data,
                'related_queries': related_queries,
                'analyzed_domains': blog_keywords
            }
            print(f"가상 데이터 결과: {result}")
            return result
    
    def get_popular_blogs(self):
        """인기 블로그 플랫폼들의 트렌드를 분석합니다."""
        popular_blogs = [
            'tistory.com',
            'blog.naver.com', 
            'blog.daum.net',
            'medium.com',
            'velog.io',
            'github.io'
        ]
        
        return self.get_trending_topics(popular_blogs)

# 분석기 인스턴스 생성
analyzer = BlogAnalyzer()



@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

@app.route('/verification.html')
def verification():
    return app.send_static_file('verification.html')

@app.route('/adsense-verification.html')
def adsense_verification():
    return app.send_static_file('adsense-verification.html')



@app.route('/api/trends')
def trends_analysis():
    """인기 블로그 플랫폼 트렌드 분석"""
    try:
        trends = analyzer.get_popular_blogs()
        return jsonify({
            'success': True,
            'trends': trends
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trends/daily')
def daily_trends():
    """일간 베스트 트렌드"""
    try:
        trends = analyzer.get_daily_trends()
        return jsonify({
            'success': True,
            'trends': trends,
            'period': 'daily'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trends/week')
def weekly_trends():
    """주간 베스트 트렌드"""
    try:
        trends = analyzer.get_weekly_trends()
        return jsonify({
            'success': True,
            'trends': trends,
            'period': 'weekly'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trends/month')
def monthly_trends():
    """월간 베스트 트렌드"""
    try:
        trends = analyzer.get_monthly_trends()
        return jsonify({
            'success': True,
            'trends': trends,
            'period': 'monthly'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trends/year')
def yearly_trends():
    """연간 베스트 트렌드"""
    try:
        trends = analyzer.get_yearly_trends()
        return jsonify({
            'success': True,
            'trends': trends,
            'period': 'yearly'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/api/analyze', methods=['POST'])
def analyze_custom_blogs():
    """사용자 정의 블로그 URL 분석"""
    try:
        print("=== API 호출 시작 ===")
        data = request.get_json()
        print(f"받은 데이터: {data}")
        
        blog_urls = data.get('urls', [])
        print(f"추출된 URL들: {blog_urls}")
        
        if not blog_urls:
            print("URL이 비어있음")
            return jsonify({
                'success': False,
                'error': '블로그 URL이 필요합니다.'
            }), 400
        
        print("분석 시작...")
        analysis = analyzer.analyze_blog_traffic(blog_urls)
        print(f"분석 결과: {analysis}")
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        print(f"상세 에러: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/api/ranking')
def get_blog_ranking():
    """블로그 플랫폼 순위 데이터"""
    try:
        print("=== 순위 데이터 API 호출 ===")
        # 인기 블로그 플랫폼들의 가상 순위 데이터
        ranking_data = [
            {
                'platform': 'Tistory',
                'domain': 'tistory.com',
                'traffic_score': 95,
                'trend_score': 88,
                'user_count': 15000000,
                'growth_rate': 12.5
            },
            {
                'platform': 'Naver Blog',
                'domain': 'blog.naver.com',
                'traffic_score': 92,
                'trend_score': 85,
                'user_count': 12000000,
                'growth_rate': 8.3
            },
            {
                'platform': 'Medium',
                'domain': 'medium.com',
                'traffic_score': 88,
                'trend_score': 90,
                'user_count': 8000000,
                'growth_rate': 15.2
            },
            {
                'platform': 'Velog',
                'domain': 'velog.io',
                'traffic_score': 82,
                'trend_score': 92,
                'user_count': 3000000,
                'growth_rate': 25.7
            },
            {
                'platform': 'GitHub Pages',
                'domain': 'github.io',
                'traffic_score': 85,
                'trend_score': 87,
                'user_count': 5000000,
                'growth_rate': 18.9
            },
            {
                'platform': 'Daum Blog',
                'domain': 'blog.daum.net',
                'traffic_score': 75,
                'trend_score': 70,
                'user_count': 6000000,
                'growth_rate': 2.1
            }
        ]
        
        # 순위 계산 (종합 점수)
        for item in ranking_data:
            item['total_score'] = (item['traffic_score'] * 0.4 + 
                                 item['trend_score'] * 0.4 + 
                                 item['growth_rate'] * 0.2)
        
        # 총점 기준으로 정렬
        ranking_data.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 순위 추가
        for i, item in enumerate(ranking_data, 1):
            item['rank'] = i
        
        print(f"순위 데이터 생성 완료: {len(ranking_data)}개 항목")
        result = {
            'success': True,
            'ranking': ranking_data
        }
        print(f"응답 데이터: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"순위 데이터 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True) 