# upbit websocket을 이용한 실제 매매 예제
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/41 : upbit websocket을 이용한 실제 매매 예제
# https://money-expert.tistory.com/42 : upbit 시세 주기적으로 받아서 매매 예제 (ticker 하나)
# https://money-expert.tistory.com/55 : upbit 시세 주기적으로 받아서 매매 예제 (복수 ticker)

import json
import csv
from  datetime import datetime
import time
#from myplot import *

from TR_FOLLOW import *
from Trader import *
from jpy_upbit import *
from jpy_dummy_ex import *  # 가상 거래소 debugging용

import websockets
import asyncio
import json

UPBIT_WEB_SOCKET_ADD = 'wss://api.upbit.com/websocket/v1'

recv_cnt = 0
async def my_connect(real, ticker, show) :
    global recv_cnt
    async with websockets.connect(UPBIT_WEB_SOCKET_ADD) as websocket:
        cmd = '[{"ticket":"test1243563478"},{"type":"trade","codes":["' + ticker + '"]}]'
        await websocket.send(cmd)
        print('upbit connected', recv_cnt)
        recv_cnt = 0
        while(1) :
            data_rev = await websocket.recv()
            my_json = data_rev.decode('utf8').replace("'", '"')
            data = json.loads(my_json)
            if show :
                print(data['code'], data['trade_time'], data['ask_bid'], data['trade_price'], data['trade_volume'])
            if 'type' in  data :
                if data['type'] == 'trade' :
                    info = make_info_from_upbit_real(data)
                    real.do_trading(info)
            recv_cnt += 1


if __name__ == '__main__':
    access = 'my acess'
    secret = 'my secret'

#    upbit = MyUpbit(access, secret)
    upbit = DummyExchange('upbit', access, secret)
    # 새로 추가함. 2021/3/28
    # multiple ticker에 대하여 매매

    # trading용 parameter 설정
    # 모든 ticker에 대하여 같은 설정 사용. 만약 ticker별로 별도 설정 값이 필요한 경우에는 ticker별로 설정 필요
    buy_perc = 0.03  # 시작가 대비 3% 오르면 매수
    sell_perc = 0.05 # 매수가 대비 5% 오르면 매도(익절)
    losscut = 0.03   # 매수가 대비 3% 내리면 losscut 매도(손절)
    seed_for_each_ticker = 10000

    tr_param = tr_params(buy_perc, sell_perc, losscut, seed_for_each_ticker)


    # 1. trading할 tickers는 tr_tickers.txt에 저장되어 있음   
    # 2. trader를 모아서 관리하는 trader_mgr 추가
    # 
    fname = '.\\tr_tickers.txt' 
    trader_mgr = TraderMgr(upbit, fname, tr_param)
    trader_mgr.prepare_to_start()
    
    # websocket을 이용하는 경우에는 1, 아니면 0
    USING_WEBSOCKET = 0
    # websocket 실간 시세를 이용하여 자동매매하기
    if USING_WEBSOCKET :
        print('not yet')
    else :
        # 10초에 한번씩 최근 거래 값을 받아서 자동매매
        while(1) :
            trader_mgr.do_trading()
            time.sleep(10)
        
