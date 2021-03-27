# date : 2020/12/11
# FLOWING
# 매수 : 입력가 대비 buy_percent 오르면 매수
# 매도 : 
#   익절 : 매수가 대비  sell_percent 오르면
#   손절 : 매수가 대비  losscut 내리면

# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/41
#
import json

class TR_FOLLOW_TREND() :
    def __init__(self, interval, num) :
        self.interval = interval # min', 'day'
        self.interval_num = num # 1, 5, 20, 60
        self.history = []
        self.buy_percent = 0
        self.sell_percent = 0
        self.losscut = 0

        self.bought_price = 0   # 매수하였으면 매수가. > 0 매수 중
        self.open = 0           # 시작가

    def init_set(self, buy_perc, sell_perc, losscut) :
        self.buy_percent = buy_perc
        self.sell_percent = sell_perc
        self.losscut = losscut

    def set_start_price(self, open_price) :
        self.open = open_price
    
    def add_tick(self, info) :
        # 향후 tick 정보로 candle을 만든다.
        pass
    # 진입조건 조사
    def is_enter_condition(self, info) :
        # buy_price는 시작가 * 상승률
        buy_price = self.open * (1+self.buy_percent) 
        if info['close'] >= buy_price :
            self.bought_price = info['close']  # 매수 가격 저장
            return info['close']
        return 0

    # 조건 조사
    # cut : 익절(1) 혹은 손절 (2)
    def is_exit_condition(self, info) :
        sell_price = self.bought_price * (1+self.sell_percent)  # 매수 가격 대비 올랐으면
        if info['close'] >= sell_price :
            self.bought_price = 0
            return info['close'], 1    # 1: 익절

        sell_price = self.bought_price * (1-self.losscut)  # 매수 가격 대비 내렸으면
        if info['close'] <= sell_price :
            self.bought_price = 0
            return info['close'], 2    # 2: 손절

        return 0, 0
if __name__ == '__main__':
    
    print('TR_FOLLOWING')