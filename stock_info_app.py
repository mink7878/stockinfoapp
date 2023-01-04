import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rc
from io import BytesIO


def get_stock_info(market_type = None):
    base_url = "https://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"

    if market_type == "kospi":
        marketType = "stockMkt"
    elif market_type == "kosdaq":
        marketType = "kosdaqMkt"
    elif market_type == None:
        marketType = ""
    
    url = "{0}?method={1}&marketType={2}".format(base_url, method, marketType)

    df = pd.read_html(url, header=0)[0]

    df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06d}")
    df = df[["회사명","종목코드"]]

    return df


def get_ticker_symbol(company_name, market_type):
    df = get_stock_info(market_type)
    code = df[df['회사명'] == company_name]['종목코드'].values
    code = code[0]

    if market_type == 'kospi':
        ticker_symbol = code + '.KS'
    elif market_type == 'kosdaq':
        ticker_symbol = code + '.KQ'

    return ticker_symbol


# 1. text_input(), date_input()으로 주식 종목 이름, 기간을 입력 받아서 stock_name, date_range 변수에 담기
stock_name = st.sidebar.text_input('회사 이름', value = 'NAVER')

date_range = st.sidebar.date_input('시작일과 종료일',
                                    [datetime.date(2019,1,1), 
                                    datetime.date(2022,12,31)])



# 2. button()으로 버튼 만들기
clicked = st.sidebar.button('주가 데이터 가져오기')

# 3. get_ticker_symbol을 호출해 티커 심볼 구하기
# 인자로 주식 종목 이름(stock_name)과 마켓 타입(kospi) 전달
if clicked == True:
    ticker_symbol = get_ticker_symbol(stock_name, 'kospi')
    # 4. 야후 파이낸스로부터 Ticker 객체 가져오기
    # 인자로 ticker_symbol 전달
    ticker_data = yf.Ticker(ticker_symbol)

    # 5. 시작일과 종료일을 start_p, end_p 변수에 담기
    # 종료일은 date_range 변수에 담긴 값에 하루를 더해주기
    start_p = date_range[0]
    end_p = date_range[1] + datetime.timedelta(days=1)

    # 6. 시작일과 종료일을 지정해 주가 데이터 가져오기
    # 종료일은 date_range 변수에 담긴 값에 하루를 더해주기
    df = ticker_data.history(start=start_p, end=end_p)
    
    # 7. 주식 데이터를 데이터 프레임 형태로 출력
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.head())

    # 8. 주식 데이터를 차트 형태로 출력
    matplotlib.rcParams['axes.unicode_minus'] = False
    rc('font', family='AppleGothic')

    ax = df['Close'].plot(grid=True, figsize=(15,5))
    ax.set_title('주가(종가) 그래프', fontsize=20)
    ax.set_xlabel('기간', fontsize=20)
    ax.set_ylabel('주가(원)', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    fig = ax.get_figure()
    st.pyplot(fig)


    # 9. 파일 다운로드
    st.markdown('**주가 데이터 파일 다운로드**')
    csv_data = df.to_csv()

    testdf = df.copy()
    testdf['Date'] = testdf.index
    testdf['Date'] = testdf['Date'].apply(lambda a: pd.to_datetime(a).date()) 
    testdf.set_index('Date', drop=True, inplace=True)
    excel_data = BytesIO()
    testdf.to_excel(excel_data)


    columns = st.columns(2)
    with columns[0]:
        st.download_button('CSV 파일 다운로드', csv_data, file_name='stock_data.csv')
    with columns[1]:
        st.download_button('엑셀 파일 다운로드', excel_data, file_name='stock_data.xlsx')

