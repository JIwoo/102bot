'''
pip install request beautifulsoup4 lxml python-telegram-bot
'''
import json
import time
from threading import Thread

import requests
import telegram
from bs4 import BeautifulSoup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

#################### ETC info ####################
# 추후 암호화 처리 예정

token = ''

bot = telegram.Bot(token)
# 크롤링 할 URL

#################### ETC info ####################

########## 가격 정보 가져오기 ##########
# 가격 정보 가공하기


def Get_PriceInfo(close_price, signed_change_rate, base_korean_name, name):
    won = format(round(float(close_price), 2), ",")
    percent = format(round(float(signed_change_rate) * 100, 2), ",")

    return '@코인빗@' + "\n" +  '-----------' + "\n" + name + '/ ' + base_korean_name + "\n" + won + "원 \n" + percent + "%"

def Get_PriceInfoCashierest(close_price, signed_change_rate, base_korean_name, name):
    won = format(round(float(close_price), 2), ",")
    percent = format(round(float(signed_change_rate), 2), ",")
    return '$캐셔레스트$' + "\n" +  '-----------' + "\n" + name + '/ ' + base_korean_name + "\n" + won + "원 \n" + percent + "%"


def Get_PriceInfoUpbit(close_price, signed_change_rate, base_korean_name, krw_price):
    if(krw_price > 0):
        won = format(round(float(close_price), 8), ",")
        krwwon = format(round(float(krw_price * close_price), 2), ",")
        percent = format(round(float(signed_change_rate) * 100, 2), ",")
        
        return '#업비트#'  + "\n" +  '-----------' + "\n" + base_korean_name + "\n" + won + " 사토시 \n" + krwwon + "원 \n" + percent + "%"
    else:
        won = format(round(float(close_price), 2), ",")
        percent = format(round(float(signed_change_rate) * 100, 2), ",")        
        return '#업비트#'  + "\n" +  '-----------' + "\n" + base_korean_name + "\n" + won + "원 \n" + percent + "%"    

def Get_PriceInfoStock(close_price, signed_change_rate, base_korean_name):
    won = format(round(float(close_price), 2), ",")
    signed_change_rate = float(signed_change_rate)
    if(signed_change_rate > 0):
        percent = "+"

    percent = percent + str(signed_change_rate)
    return '%주식%' + "\n" +  '-----------' +  '-----------' + "\n" + base_korean_name + "\n" + won + "원 \n" + percent + '%'   

def Get_PriceInfoStocks(lists):
    result = '%주식인기%'
    num = 0
    for coins in lists:
        num += 1
        result += "\n"
        won = format(round(float(coins['nv']), 2), ",")
        signed_change_rate = float(coins['cr'])
        if(signed_change_rate > 0):
            percent = "+"
        else:
            percent = ""

        percent = percent + str(signed_change_rate)
        result += '-----------' + "\n" + str(num) + '위 : ' + coins['nm'] + "\n" + won + "원 \n" + percent + '%'   

    return result  
    


# 코인명 / Symbol에 상응되는 가격 정보를 가져온다.
def Get_CoinPirce(coin_name):
    if(coin_name == 'CAP' or coin_name == '캡'):
        coin_name = 'cap'
        data_json_url = "https://rest.cashierest.com/v3.0/tickers/krw/" + coin_name
        
        headers = {'Content-Type': 'text/html; charset=utf-8'}
        cashierest = requests.get(data_json_url,headers=headers).text
        json_coin_list = json.loads(cashierest)
        return Get_PriceInfoCashierest(json_coin_list[0]['CurrentPrice'], json_coin_list[0]['DayDealRise'], '캡', 'CAP')

    if(coin_name == 'HRT' or coin_name == '하트'):

        coin_name = 'hrt'

        data_json_url = "https://rest.cashierest.com/v3.0/tickers/krw/" + coin_name

        headers = {'Content-Type': 'text/html; charset=utf-8'}
        cashierest = requests.get(data_json_url,headers=headers).text
        json_coin_list = json.loads(cashierest)
        
        return Get_PriceInfoCashierest(json_coin_list[0]['CurrentPrice'], json_coin_list[0]['DayDealRise'], '하트', 'HRT')    

    if(coin_name[0:1] == '#' or coin_name[0:1] == '-' or coin_name[0:1] == '@'
       or coin_name[0:1] == '!' or coin_name[0:1] == '%' or coin_name[0:1] == '$'):
        market = 'KRW-'
        coin_name = coin_name[1:]
        coin_code = market + coin_name
        
        data_json_url = "https://api.upbit.com/v1/ticker?markets=" + coin_code

        #json_string 값을 json 형식으로 변환시킨다.
        json_coin_list = json.loads(requests.get(data_json_url).text)

        for coin in json_coin_list:
            
            if(coin == 'error'):
                
                market = 'BTC-'
                coin_code = market + coin_name
                data_json_url = "https://api.upbit.com/v1/ticker?markets=" + coin_code
                json_coin_lists = json.loads(requests.get(data_json_url).text)
                
                for coinmarket in json_coin_lists:
                    
                    if(coinmarket == 'error'):
                        return Get_TickerCoinbit(coin_name)
                    else:
                
                        data_json_url = "https://api.upbit.com/v1/ticker?markets=KRW-BTC"
                        json_coin_list = json.loads(requests.get(data_json_url).text)

                        krw = 0
                        for btcprice in json_coin_list:

                            krw = btcprice['trade_price']  
                        
                        return Get_PriceInfoUpbit(coinmarket['trade_price'], coinmarket['signed_change_rate'], coinmarket['market'], krw)
                        
                            
            else:
                return Get_PriceInfoUpbit(coin['trade_price'], coin['signed_change_rate'], coin['market'], 0)   
    
    if(coin_name[0:1] == '/'):
        stock_name = coin_name[1:]  
        data_json_url = "https://m.stock.naver.com/api/json/search/searchListJson.nhn?keyword=삼성전자"
        return '------------' + "\n" + '버그있어용'  


def Get_TickerCoinbit(coin_name):

    data_json_url = "https://production-api.coinbit.global/api/v1.0/trading_pairs"

    #json_string 값을 json 형식으로 변환시킨다.
    json_coin_list = json.loads(requests.get(data_json_url).text)

    for coin in json_coin_list:
        
        if coin['quote_symbol'] == 'KRW':
            # coin_name이 한글로 입력되었을 경우
            if (coin['base_korean_name'] == coin_name or coin['base_korean_name'] == "·" + coin_name):
                
                return Get_PriceInfo(coin['close_price'], coin['signed_change_rate'], coin['base_korean_name'], coin['name'])

            # coin_name이 symbol명으로 입력되었을 경우
            elif (coin['base_symbol'] == coin_name or coin['base_symbol'] == "·" + coin_name):
                
                return Get_PriceInfo(coin['close_price'], coin['signed_change_rate'], coin['base_korean_name'], coin['name'])
         





            
########## 가격 정보 가져오기 ##########

########## 공지 가져오기 ##########


def get_notice_icon_count():
    url = "https://community.coinbit.co.kr/bbs/board.php?bo_table=free"
    r = requests.get(url, verify=False)
    bs = BeautifulSoup(r.content, "lxml")
    divs = bs.select("div.lst_left")  # select의 결과는 리스트이다.
    notice_icon_list = []

    for item in divs:
        icon = item.select("strong.notice_icon")

        # 값이 없을 경우
        if not icon:
            continue

        notice_icon_list.append(icon)
    return len(notice_icon_list)

# 가장 최근에 작성된 공지를 찾는다.


def get_topmost_notice():
    print('search top notice...')
    
    url = "https://community.coinbit.co.kr/bbs/board.php?bo_table=free"
    r = requests.get(url, verify=False)
    bs = BeautifulSoup(r.content, "lxml")

    # 가장 맨 위에 작성된 공지를 찾는다.
    divs = bs.find('div', class_="bo_subject")
    icon = divs.find('strong', class_="notice_icon")
    notice_html_tag = icon.parent.parent.parent
    result = notice_html_tag.find('a', class_='bo_subject')

    # 가장 맨 위에 작성된 공지를  크롤링 한다.
    topmost_notice_url = result.get('href')
    r2 = requests.get(topmost_notice_url, verify=False)
    bs2 = BeautifulSoup(r2.content, "lxml")

    board = bs2.find('article', id="bo_v")
    content_tag = bs2.find('div', id="bo_v_con")
    content_p_tag = content_tag.find_all('p')

    #날짜와 제목을 가져와서 inser한다.
    content_p_tag.insert(0, board.find('span', class_="bo_v_tit"))
    content_p_tag.insert(1, board.find('p'))

    content_str = ''
    for item in content_p_tag:
        content_str += ',' + item.text

    notice_msg = content_str.replace(',', '\n') + '\n\n' + '#코인빗공지'
    print(notice_msg)
    bot.send_message(chat_id=-791677982, text=notice_msg)  # 금융위원회
    return


def get_new_notice():
    print('thread test')
    while(True):
        print('threading...')
        notice_count = get_notice_icon_count()

        print('notice_count : ', notice_count)
        if notice_count < 3:
            print("공지각")
            bot.send_message(chat_id=-791677982, text="#공지각#") #금융위원회
            bot.send_message(chat_id=478474804, text="공지각")  # bot

            needLoop = True
            while(needLoop):
                notice_count = get_notice_icon_count()
                print('waiting...')
                if notice_count == 3:
                    get_topmost_notice()
                    needLoop = False

                time.sleep(1.5)
        time.sleep(1.5)
########## 공지 가져오기 ##########
def Get_Message(update, context):        
    _result = Get_CoinPirce(update.message.text.upper())
    if (str(_result) == "None" or str(_result) == "null"):
        return
    else:
        update.message.reply_text(_result)


def thread_start():
    print('thread_start')
if __name__ == "__main__":

    print('코인빗+업비트+CAP+주식 통합')
    #thread_start()

    updater = Updater(token, use_context=True)
    message_handler = MessageHandler(Filters.text, Get_Message)
    updater.dispatcher.add_handler(message_handler)
    updater.start_polling(timeout=3, clean=True)
    updater.idle()
