import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback

# 샘플 데이터
df = px.data.gapminder()

# Dash 앱 생성
app = Dash(__name__)

# 레이아웃 정의
app.layout = html.Div([
    html.H1("인터랙티브 차트 예제"),
    
    # 메인 차트
    dcc.Graph(id='main-chart'),
    
    # 상세 차트
    html.Div(id='detail-container', children=[
        html.H3("국가별 상세 데이터"),
        dcc.Graph(id='detail-chart')
    ])
])

# 메인 차트 콜백
@callback(
    Output('main-chart', 'figure'),
    Input('main-chart', 'clickData')
)
def update_main_chart(click_data):
    # 2007년 데이터만 사용
    df_2007 = df.query("year == 2007")
    
    fig = px.scatter(
        df_2007, 
        x="gdpPercap", 
        y="lifeExp", 
        size="pop", 
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=60
    )
    
    fig.update_layout(
        title="2007년 GDP와 기대수명",
        xaxis_title="1인당 GDP (로그 스케일)",
        yaxis_title="기대수명",
        clickmode='event+select'  # 클릭 이벤트 활성화
    )
    
    return fig

# 상세 차트 콜백 - 클릭한 국가의 연도별 데이터 표시
@callback(
    Output('detail-chart', 'figure'),
    Input('main-chart', 'clickData')
)
def display_detail_chart(click_data):
    if click_data is None:
        # 기본값 - 한국 데이터
        country_name = "Korea, Rep."
    else:
        # 클릭한 국가 정보 추출
        country_name = click_data['points'][0]['hovertext']
    
    # 해당 국가의 모든 연도 데이터 필터링
    country_data = df[df.country == country_name]
    
    # 상세 차트 생성
    fig = px.line(
        country_data, 
        x="year", 
        y="lifeExp",
        title=f"{country_name}의 연도별 기대수명 변화"
    )
    
    fig.update_traces(mode="markers+lines", marker=dict(size=10))
    
    return fig

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)