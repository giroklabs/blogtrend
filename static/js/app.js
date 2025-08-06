// 전역 변수
let trendsChart = null;
let currentRankingData = [];

// DOM이 로드되면 실행
document.addEventListener('DOMContentLoaded', function() {
    // 초기 데이터 로드
    loadRankingData();
    
    // 이벤트 리스너 등록
    document.getElementById('analyzeTrends').addEventListener('click', analyzeTrends);
    
    // 트렌드 기간 선택 이벤트
    document.querySelectorAll('input[name="trendPeriod"]').forEach(radio => {
        radio.addEventListener('change', function() {
            loadTrendsByPeriod(this.value);
        });
    });
    
    // 엔터 키 이벤트
    document.getElementById('blogUrls').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') analyzeTrends();
    });
    
    // 초기 오늘 베스트 트렌드 로드
    loadTrendsByPeriod('today');
});

// 로딩 스피너 표시/숨김
function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('d-none');
}

// 순위 데이터 로드
async function loadRankingData() {
    try {
        showLoading();
        const response = await fetch('/api/ranking');
        const data = await response.json();
        
        if (data.success) {
            currentRankingData = data.ranking;
            displayRankingTable(data.ranking);
        } else {
            showAlert('순위 데이터를 불러오는데 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('순위 데이터 로드 오류:', error);
        showAlert('순위 데이터를 불러오는데 실패했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 순위 테이블 표시
function displayRankingTable(rankingData) {
    const tbody = document.getElementById('rankingTableBody');
    tbody.innerHTML = '';
    
    rankingData.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'fade-in-up';
        
        const rankClass = item.rank <= 3 ? `rank-${item.rank}` : 'rank-other';
        
        row.innerHTML = `
            <td>
                <span class="rank-badge ${rankClass}">${item.rank}</span>
            </td>
            <td><strong>${item.platform}</strong></td>
            <td><code>${item.domain}</code></td>
            <td>
                <span class="score-display ${getScoreClass(item.traffic_score)}">
                    ${item.traffic_score}
                </span>
            </td>
            <td>
                <span class="score-display ${getScoreClass(item.trend_score)}">
                    ${item.trend_score}
                </span>
            </td>
            <td>${formatNumber(item.user_count)}</td>
            <td>
                <span class="text-${item.growth_rate > 0 ? 'success' : 'danger'}">
                    ${item.growth_rate > 0 ? '+' : ''}${item.growth_rate}%
                </span>
            </td>
            <td>
                <span class="score-display score-high">
                    ${item.total_score.toFixed(1)}
                </span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// 점수에 따른 CSS 클래스 반환
function getScoreClass(score) {
    if (score >= 90) return 'score-high';
    if (score >= 70) return 'score-medium';
    return 'score-low';
}

// 숫자 포맷팅
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}





// 날짜 포맷팅
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '오늘';
    if (diffDays <= 7) return `${diffDays}일 전`;
    if (diffDays <= 30) return `${Math.floor(diffDays / 7)}주 전`;
    return date.toLocaleDateString('ko-KR');
}

// 기간별 트렌드 로드
async function loadTrendsByPeriod(period) {
    try {
        showLoading();
        let endpoint = '';
        
        switch(period) {
            case 'today':
                endpoint = '/api/trends/daily';
                break;
            case 'week':
                endpoint = '/api/trends/week';
                break;
            case 'month':
                endpoint = '/api/trends/month';
                break;
            case 'year':
                endpoint = '/api/trends/year';
                break;
            default:
                endpoint = '/api/trends/daily';
        }
        
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (data.success) {
            displayBestTrends(data, period);
        } else {
            showAlert(data.error || '트렌드 데이터를 불러오는데 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('트렌드 로드 오류:', error);
        showAlert('트렌드 데이터를 불러오는데 실패했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 베스트 트렌드 표시
function displayBestTrends(data, period) {
    const container = document.getElementById('bestTrendsList');
    
    let periodText = '';
    switch(period) {
        case 'today':
            periodText = '오늘';
            break;
        case 'week':
            periodText = '이번주';
            break;
        case 'month':
            periodText = '이번달';
            break;
        case 'year':
            periodText = '올해';
            break;
        default:
            periodText = '오늘';
    }
    
    let html = `
        <div class="alert alert-info mb-3">
            <i class="fas fa-info-circle me-2"></i>
            <strong>${periodText}의 베스트 검색어</strong> (기간별로 다른 데이터가 표시됩니다)
        </div>
        <div class="row">
    `;
    
    if (data.trends && data.trends.trending_searches && data.trends.trending_searches.length > 0) {
        data.trends.trending_searches.slice(0, 20).forEach((item, index) => {
            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="trend-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-success me-2">${index + 1}</span>
                            <h6 class="mb-0">${item}</h6>
                        </div>
                    </div>
                </div>
            `;
        });
    } else {
        html += '<div class="col-12"><p class="text-muted">데이터를 불러오는 중입니다...</p></div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// 트렌드 분석
async function analyzeTrends() {
    const keywords = document.getElementById('blogUrls').value.trim();
    
    if (!keywords) {
        showAlert('키워드를 입력해주세요.', 'warning');
        return;
    }
    
    const keywordList = keywords.split(',').map(keyword => keyword.trim()).filter(keyword => keyword);
    
    if (keywordList.length === 0) {
        showAlert('유효한 키워드를 입력해주세요.', 'warning');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ urls: keywordList })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayTrendsResults(data.analysis, keywordList);
        } else {
            showAlert(data.error || '트렌드 분석에 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('트렌드 분석 오류:', error);
        showAlert('트렌드 분석에 실패했습니다.', 'danger');
    } finally {
        hideLoading();
    }
}

// 트렌드 결과 표시
function displayTrendsResults(analysis, urls) {
    const resultsContainer = document.getElementById('trendsResults');
    
    let html = `
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h6 class="mb-0">
                    <i class="fas fa-chart-line me-2"></i>
                    분석 결과
                </h6>
            </div>
            <div class="card-body">
    `;
    
    if (analysis.analyzed_domains) {
        html += `
            <div class="mb-3">
                <h6><i class="fas fa-link me-2"></i>분석된 도메인</h6>
                <div class="d-flex flex-wrap gap-2">
                    ${analysis.analyzed_domains.map(domain => 
                        `<span class="badge bg-secondary">${domain}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    if (analysis.interest_over_time.length === 0) {
        html += `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                트렌드 데이터를 찾을 수 없습니다. 다른 키워드를 시도해보세요.
            </div>
        `;
    } else {
        // 차트 생성 (데이터가 있을 때만)
        if (analysis.interest_over_time && analysis.interest_over_time.length > 0) {
            createTrendsChart(analysis.interest_over_time, urls);
        }
        
        // 관련 쿼리 표시
        html += '<h6><i class="fas fa-search me-2"></i>관련 검색어</h6>';
        
        if (analysis.related_queries) {
            Object.keys(analysis.related_queries).forEach(keyword => {
                const queries = analysis.related_queries[keyword];
                if (queries && queries.top && queries.top.length > 0) {
                    html += `
                        <div class="trend-item">
                            <h6>${keyword}</h6>
                            <ul class="list-unstyled mb-0">
                                ${queries.top.slice(0, 5).map(item => 
                                    `<li><i class="fas fa-arrow-up text-success me-1"></i>${item.query} (${item.value})</li>`
                                ).join('')}
                            </ul>
                        </div>
                    `;
                }
            });
        } else {
            html += '<p class="text-muted">관련 검색어 데이터가 없습니다.</p>';
        }
    }
    
    // 점수 해석 팁 추가
    html += `
        <div class="mt-4">
            <div class="alert alert-info">
                <h6><i class="fas fa-info-circle me-2"></i>관심도 점수 해석 가이드</h6>
                <div class="row">
                    <div class="col-md-3">
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-danger me-2">90-100</span>
                            <small>최고</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-warning me-2">70-89</span>
                            <small>높음</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-success me-2">30-69</span>
                            <small>보통</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-secondary me-2">0-29</span>
                            <small>낮음</small>
                        </div>
                    </div>
                </div>
                <small class="text-muted">
                    <i class="fas fa-lightbulb me-1"></i>
                    Google Trends 기준으로 해당 기간의 검색 관심도를 0-100점으로 표시합니다. 
                    100점은 해당 기간의 최고 관심도를 의미합니다.
                </small>
            </div>
        </div>
    `;
    
    html += '</div></div>';
    resultsContainer.innerHTML = html;
}

// 트렌드 차트 생성
function createTrendsChart(data, labels) {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    
    // 기존 차트 제거
    if (trendsChart) {
        trendsChart.destroy();
    }
    
    // 데이터가 없으면 차트를 생성하지 않음
    if (!data || data.length === 0) {
        return;
    }
    
    // 첫 번째 데이터 포인트에서 키워드 키들을 찾습니다
    const firstDataPoint = data[0];
    // keyword1, keyword2 형태와 실제 키워드 이름 모두 처리
    const keywordKeys = Object.keys(firstDataPoint).filter(key => 
        key.startsWith('keyword') || labels.includes(key)
    );
    
    const datasets = keywordKeys.map((key, index) => {
        // 실제 키워드 이름을 찾습니다
        let label = key;
        if (key.startsWith('keyword')) {
            label = labels[index] || key;
        }
        
        return {
            label: label,
            data: data.map(item => item[key] || 0),
            borderColor: getChartColor(index),
            backgroundColor: getChartColor(index, 0.1),
            tension: 0.4,
            fill: false
        };
    });
    
    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((item, index) => {
                // date 필드가 있으면 사용, 없으면 인덱스 기반으로 생성
                if (item.date) {
                    return new Date(item.date).toLocaleDateString('ko-KR');
                } else {
                    return `데이터 ${index + 1}`;
                }
            }),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '키워드 트렌드 분석'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: '관심도 점수 (0-100)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '점';
                        }
                    }
                }
            }
        }
    });
}

// 차트 색상 생성
function getChartColor(index, alpha = 1) {
    const colors = [
        `rgba(54, 162, 235, ${alpha})`,
        `rgba(255, 99, 132, ${alpha})`,
        `rgba(255, 205, 86, ${alpha})`,
        `rgba(75, 192, 192, ${alpha})`,
        `rgba(153, 102, 255, ${alpha})`,
        `rgba(255, 159, 64, ${alpha})`
    ];
    return colors[index % colors.length];
}

// 알림 표시
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 기존 알림 제거
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // 새 알림 추가
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// 스무스 스크롤
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 페이지 로드 시 애니메이션
window.addEventListener('load', function() {
    document.body.classList.add('fade-in-up');
}); 