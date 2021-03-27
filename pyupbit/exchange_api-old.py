import time
from pyupbit.quotation_api import *
import jwt
from urllib.parse import urlencode
import requests

getframe_expr = 'sys._getframe({}).f_code.co_name'


def _send_post_request(url, headers=None, data=None):
    try:
        resp = requests_retry_session().post(url, headers=headers, data=data)
        remaining_req_dict = {}
        remaining_req = resp.headers.get('Remaining-Req')
        if remaining_req is not None:
            group, min, sec = _parse_remaining_req(remaining_req)
            remaining_req_dict['group'] = group
            remaining_req_dict['min'] = min
            remaining_req_dict['sec'] = sec
        contents = resp.json()
        return contents, remaining_req_dict
    except Exception as x:
        print("send post request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None


def _parse_remaining_req(remaining_req):
    try:
        p = re.compile("group=([a-z]+); min=([0-9]+); sec=([0-9]+)")
        m = p.search(remaining_req)
        return m.group(1), int(m.group(2)), int(m.group(3))
    except:
        return None, None, None


def _send_get_request(url, headers=None):
    try:
        resp = requests_retry_session().get(url, headers=headers)
        remaining_req_dict = {}
        remaining_req = resp.headers.get('Remaining-Req')
        if remaining_req is not None:
            group, min, sec = _parse_remaining_req(remaining_req)
            remaining_req_dict['group'] = group
            remaining_req_dict['min'] = min
            remaining_req_dict['sec'] = sec
        contents = resp.json()
        return contents, remaining_req_dict
    except Exception as x:
        print("send get request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None


def _send_delete_request(url, headers=None, data=None):
    try:
        resp = requests_retry_session().delete(url, headers=headers, data=data)
        remaining_req_dict = {}
        remaining_req = resp.headers.get('Remaining-Req')
        if remaining_req is not None:
            group, min, sec = _parse_remaining_req(remaining_req)
            remaining_req_dict['group'] = group
            remaining_req_dict['min'] = min
            remaining_req_dict['sec'] = sec
        contents = resp.json()
        return contents, remaining_req_dict
    except Exception as x:
        print("send post request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None


def get_tick_size(price):
    if price >= 2000000:
        tick_size = round(price / 1000) * 1000
    elif price >= 1000000:
        tick_size = round(price / 500) * 500
    elif price >= 500000:
        tick_size = round(price / 100) * 100
    elif price >= 100000:
        tick_size = round(price / 50) * 50
    elif price >= 10000:
        tick_size = round(price / 10) * 10
    elif price >= 1000:
        tick_size = round(price / 5) * 5
    elif price >= 100:
        tick_size = round(price / 1) * 1
    elif price >= 10:
        tick_size = round(price / 0.1) * 0.1
    else:
        tick_size = round(price / 0.01) * 0.01
    return tick_size


class Upbit:
    def __init__(self, access, secret):
        self.access = access
        self.secret = secret

    def _request_headers(self, data=None):
        payload = {
            "access_key": self.access,
            "nonce": int(time.time() * 1000)
        }
        if data is not None:
            payload['query'] = urlencode(data)
        jwt_token = jwt.encode(payload, self.secret, algorithm="HS256").decode('utf-8')
        authorization_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorization_token}
        return headers

    def get_balance(self, ticker="KRW"):
        """
        특정 코인/원화의 잔고 조회
        :param ticker:
        :return:
        """
        try:
            # KRW-BTC
            if '-' in ticker:
                ticker = ticker.split('-')[1]

            balances = self.get_balances()[0]
            balance = None

            for x in balances:
                if x['currency'] == ticker:
                    balance = float(x['balance'])
                    break
            return balance

        except Exception as x:
            print(x.__class__.__name__)
            return None


    def get_balances(self):
        '''
        전체 계좌 조회
        :return:
        '''
        url = "https://api.upbit.com/v1/accounts"
        headers = self._request_headers()
        return _send_get_request(url, headers=headers)

    def buy_limit_order(self, ticker, price, volume):
        '''
        지정가 매수
        :param ticker: 마켓 티커
        :param price: 주문 가격
        :param volume: 주문 수량
        :return:
        '''
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {"market": ticker,
                    "side": "bid",
                    "volume": str(volume),
                    "price": str(price),
                    "ord_type": "limit"}
            headers = self._request_headers(data)
            return _send_post_request(url, headers=headers, data=data)
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def buy_market_order(self, ticker, price, margin=0.01):
        """
        시장가 매수 (호가 조회 후 최우선 매도호가로 주문)
        :param ticker:  티커
        :param price:  매수금액
        :param margin:  매수 수량 계산에 사용되는 margin
        :return:
        """
        try:
            orderbooks = get_orderbook(ticker)
            orderbooks = orderbooks[0]['orderbook_units']

            for orderbook in orderbooks:
                ask_price = orderbook['ask_price']
                ask_size = orderbook['ask_size']

                bid_price = ask_price                                   # 매수가
                available_bid_size = (price / ask_price) * (1-margin)   # 매수 가능 수량 (마진 고려)
                bid_size = min(available_bid_size, ask_size)            # 현재 호가에 대한 매수 수량
                self.buy_limit_order(ticker, bid_price, bid_size)

                # 현재 호가에 수량이 부족한 경우
                if available_bid_size > ask_size:
                    price -= (bid_price * bid_size)
                else:
                    break
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def sell_market_order(self, ticker, size):
        """
        시장가 매도 (호가 조회 후 최우선 매수 호가로 주문)
        :param ticker:  티커
        :param size:  수량
        :return:
        """
        try:
            orderbooks = get_orderbook(ticker)
            orderbooks = orderbooks[0]['orderbook_units']

            for orderbook in orderbooks:
                # 매수호가
                bid_price = orderbook['bid_price']
                bid_size = orderbook['bid_size']

                ask_price = bid_price                                   # 매도가 = 최우선 매수가
                ask_size = min(size, bid_size)                          # 현재 호가에 대한 매수 수량
                self.sell_limit_order(ticker, ask_price, ask_size)

                # 현재 호가에 수량이 부족한 경우
                if bid_size < size:
                    size -= bid_size
                else:
                    break
        except Exception as x:
            print(x.__class__.__name__)
            return None


    def sell_limit_order(self, ticker, price, volume):
        '''
        지정가 매도
        :param ticker: 마켓 티커
        :param price: 주문 가격
        :param volume: 주문 수량
        :return:
        '''
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {"market": ticker,
                    "side": "ask",
                    "volume": str(volume),
                    "price": str(price),
                    "ord_type": "limit"}
            headers = self._request_headers(data)
            return _send_post_request(url, headers=headers, data=data)
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def cancel_order(self, uuid):
        '''
        주문 취소
        :param uuid: 주문 함수의 리턴 값중 uuid
        :return:
        '''
        try:
            url = "https://api.upbit.com/v1/order"
            data = {"uuid": uuid}
            headers = self._request_headers(data)
            return _send_delete_request(url, headers=headers, data=data)
        except Exception as x:
            print(x.__class__.__name__)
            return None


if __name__ == "__main__":
    with open("upbit.txt") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()

    # Upbit
    upbit = Upbit(access, secret)

    # 모든 잔고 조회
    #print(upbit.get_balances())

    # 원화 잔고 조회
    print(upbit.get_balance(ticker="KRW"))
    print(upbit.get_balance(ticker="KRW-BTC"))
    print(upbit.get_balance(ticker="KRW-XRP"))

    # 매도
    #print(upbit.sell_limit_order("KRW-XRP", 1000, 20))

    # 매수
    #print(upbit.buy_limit_order("KRW-XRP", 200, 20))

    # 주문 취소
    #print(upbit.cancel_order('82e211da-21f6-4355-9d76-83e7248e2c0c'))









