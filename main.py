import _thread
from pybit.unified_trading import HTTP
import websocket
import threading
import json
import time
import traceback
import requests
import telebot
from telebot import types
from threading import Thread


class SocketConn_Binance(websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url=url, on_open=self.on_open)

        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: self.on_errors(f'{traceback.format_exc()}')#print('ERROR: ', traceback.format_exc())
        self.on_close = lambda ws: self.on_closes('CLOSING')#print('CLOSING')

        self.ist_1m = []
        self.ist_5m = []
        self.ist_15m = []

        self._3m = []

        API = '7268129368:AAF6ueonH7QbyNbGddiBTKwRHcfDpLodynQ'
        bot = telebot.TeleBot(API)
        self.bot = bot

        self.par_1m = 2#float(input('Процент за 1m: '))#2
        self.par_5m = 3#float(input('Процент за 5m: '))#3
        self.par_15m = 5#float(input('Процент за 15m: '))#5

        self.run_forever()

    def on_closes(self,txt):
        print(txt)
        st_binance()

    def on_errors(self, error):
        print(error)
        bot = self.bot
        bot.send_message(-4519723605, f'Ошибка:\n\n{error}')
        self.reconnect()

    def reconnect(self):
        print('Reconnecting...')
        bot = self.bot
        bot.send_message(-4519723605, f'Reconnecting...')
        time.sleep(5)  # Wait for 5 seconds before reconnecting
        self.__init__(self.url)

    def on_open(self, ws):
        print("Websocket was opened")
        bot = self.bot
        bot.send_message(-4519723605, "Binance: Сonnection was opened")

    def message(self, msg):
        msg = json.loads(msg)

        if self.ist_1m == [] and self.ist_5m == [] and self.ist_15m == []:
            self.ist_1m.append(msg)
            self.ist_5m.append(msg)
            self.ist_15m.append(msg)

        sp1 = []
        sp2 = []
        sp3 = []

        for ist in self.ist_1m[0]:
            for now in msg:
                if ist['s'] == now['s']:
                    #if ist['s'][-1] == 'T':
                        nowe = float(now['p'])
                        back = float(ist['p'])

                        pr = (nowe - back) / nowe * 100

                        sp1.append({'symbol': now['s'], 'pr':round(pr,3), 't': int(now['E'])})

        for ist in self.ist_5m[0]:
            for now in msg:
                if ist['s'] == now['s']:
                    #if ist['s'][-1] == 'T':
                        nowe = float(now['p'])
                        back = float(ist['p'])
                        #print(f'{nowe}:{back}')

                        pr = (nowe - back) / nowe * 100
                        sp2.append({'symbol': now['s'], 'pr':round(pr,3), 't': int(now['E'])})


        for ist in self.ist_15m[0]:
            for now in msg:
                if ist['s'] == now['s']:
                   # if ist['s'][-1] == 'T':
                        nowe = float(now['p'])
                        back = float(ist['p'])

                        pr = (nowe - back) / nowe * 100

                        sp3.append({'symbol': now['s'], 'pr':round(pr,3), 't': int(now['E'])})

        data = []
        for _msg in msg:
            data1m = None
            data5m = None
            data15m = None

            for _sp1 in sp1:
                if _msg['s'] == _sp1['symbol']:
                    data1m = _sp1
            for _sp2 in sp2:
                if _msg['s'] == _sp2['symbol']:
                    data5m = _sp2
            for _sp3 in sp3:
                if _msg['s'] == _sp3['symbol']:
                    data15m = _sp3

            data.append({'symbol':_msg['s'], 'pr':[data1m['pr'],data5m['pr'],data15m['pr']], 't':data1m['t']})

        def OUT(out):
            bot = self.bot

            def priceChangePercent(S):
                url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
                response = requests.get(url, timeout=30)
                data_many_f = response.json()

                for coin in data_many_f:
                    symbol = coin['symbol']
                    if symbol == S:
                        return f"\n\n📌<b>Chg % 24h:</b>  <u>{coin['priceChangePercent']}%</u>"

            price = priceChangePercent(out['symbol'])



            if out['pr'][0] >= 0:
                m1 = (f"🟩<b>Price change:</b>  <u>{out['pr'][0]}%</u>\n"
                      f"👉<b>Interval:</b> 1m")
            else:
                m1 = (f"🟥<b>Price change:</b>  <u>{out['pr'][0]}%</u>\n"
                      f"👉<b>Interval:</b> 1m")

            if out['pr'][0] >= 0:
                m5 = (f"🟩<b>Price change:</b>  <u>{out['pr'][1]}%</u>\n"
                      f"👉<b>Interval:</b> 5m")
            else:
                m5 = (f"🟥<b>Price change:</b>  <u>{out['pr'][1]}%</u>\n"
                      f"👉<b>Interval:</b> 5m")
            if out['pr'][0] >= 0:
                m15 = (f"🟩<b>Price change:</b>  <u>{out['pr'][2]}%</u>\n"
                      f"👉<b>Interval:</b> 15m")
            else:
                m15 = (f"🟥<b>Price change:</b>  <u>{out['pr'][2]}%</u>\n"
                      f"👉<b>Interval:</b> 15m")


            txt = (f"🟡  <code>{out['symbol']}</code>\n"
                   f"#Binance  #{out['symbol']}\n\n"
                   f'{m1}\n\n'
                   f'{m5}\n\n'
                   f'{m15}{price}')



            markup = types.InlineKeyboardMarkup()

            b1 = types.InlineKeyboardButton(text='TV',
                                            url=f"https://ru.tradingview.com/chart/{out['symbol']}.P")
            b2 = types.InlineKeyboardButton(text='CG',
                                            url=f"https://www.coinglass.com/tv/ru/Binance_{out['symbol']}")
            b3 = types.InlineKeyboardButton(text='ПЕРЕХОД В БОТ',
                                            url=f"https://t.me/+NeaYSIqGPBtmYTNi")
            markup.add(b1, b2)
            markup.add(b3)
            bot.send_message(-1002276541068, txt, parse_mode='HTML', reply_markup=markup)
            print(txt)

        for out in data:
            if out['pr'][0] >= self.par_1m or out['pr'][1] >= self.par_5m or out['pr'][2] >= self.par_15m or out['pr'][0] <= -self.par_1m or out['pr'][1] <= -self.par_5m or out['pr'][2] <= -self.par_15m:
                have = True
                for _3m in self._3m:
                    if out['symbol'] == _3m['symbol']:
                        if out['t'] >= _3m['t'] + (3 * 60000):
                            OUT(out)
                            self._3m.remove(_3m)
                            self._3m.append(out)
                        have = False
                        break
                if have:
                    OUT(out)
                    self._3m.append(out)

        z1 = int(self.ist_1m[0][0]['E'])
        z2 = int(self.ist_5m[0][0]['E'])
        z3 = int(self.ist_15m[0][0]['E'])
        y2 = int(msg[0]['E'])
        self.ist_1m.append(msg)
        self.ist_5m.append(msg)
        self.ist_15m.append(msg)
        if y2 >= z1 + (1 * 60000):
            self.ist_1m.pop(0)
            self.ist_1m.pop(0)
        if y2 >= z2 + (5 * 60000):
            self.ist_5m.pop(0)
            self.ist_5m.pop(0)
        if y2 >= z3 + (15 * 60000):
            self.ist_15m.pop(0)
            self.ist_15m.pop(0)








def sombol_bybit():
    session = HTTP(
        testnet=False,
        api_key="9kBNn0gpUuXK6s80l4",
        api_secret="mZ3SJCj9FOuBQnVNnad3xqtrZZ0tp7aOm7qN",
        recv_window=60000
    )

    # spot
    # linear

    tickers_spot = session.get_tickers(category="linear")
    data_tickers = tickers_spot['result']['list']

    data_tickers = [f"tickers.{i['symbol']}" for i in data_tickers if i['symbol'][-1] == 'T']
    return data_tickers

class SocketConn_ByBit(websocket.WebSocketApp):
    def __init__(self, url, params=[]):
        super().__init__(url=url, on_open=self.on_open)

        self.params = params
        self.on_message = lambda ws, msg: self.message(msg)
        self.on_error = lambda ws, e: self.on_errors(f'{traceback.format_exc()}')#print('ERROR: ', traceback.format_exc())
        self.on_close = lambda ws: self.on_closes('CLOSING')#print('CLOSING')

        API = '7497253254:AAEtyB-S4C8-LoLhM9B6ShhErX7f76UatCY'
        bot = telebot.TeleBot(API)
        self.bot = bot

        self.ist_1m = []
        self.ist_5m = []
        self.ist_15m = []

        self._3m = []

        self.par_1m = 3
        self.par_5m = 7
        self.par_15m = 10

        self._5m = None
        self._5msum = 0

        self.run_forever()

    def on_closes(self,txt):
        print(txt)
        st_bybit()


    def on_errors(self, error):
        print(error)
        self.bot.send_message(-4519723605, f'Ошибка:\n\n{error}')
        self.reconnect()

    def reconnect(self):
        print('Reconnecting...')
        bot = self.bot
        bot.send_message(-4519723605, f'Reconnecting...')
        time.sleep(5)  # Wait for 5 seconds before reconnecting
        #self.__init__(self.url, params=self.params)
        params = sombol_bybit()
        self.__init__(self.url,params=params)

    def on_open(self, ws, ):
        print("Websocket was opened")
        bot = self.bot
        bot.send_message(-4519723605, "ByBit: Сonnection was opened")

        def run(*args):
            tradeStr = {'op': 'subscribe', 'args': self.params}
            ws.send(json.dumps(tradeStr))

        _thread.start_new_thread(run,())

    def message(self, msg):
        bot = self.bot
        msg = json.loads(msg)
        try:
            msg = {'s':msg['data']['symbol'],'p':msg['data']['lastPrice'], 't':int(msg['ts'])}
            if msg['s'][-1] != 'T':
                msg = False
        except Exception as e:
            msg = False

        if msg != False:
            self._5msum += 1

            if self._5m == None:
                bot = self.bot
                bot.send_message(-4519723605, str(self._5msum))
                self._5msum = 0
                self._5m = msg['t']
            else:
                if msg['t'] >= self._5m + (5 * 60000):
                    bot.send_message(-4519723605, str(self._5msum))
                    self._5msum = 0
                    self._5m = msg['t']



            z1 = None
            z2 = None
            z3 = None

            have = True
            for ist_1 in self.ist_1m:
                if ist_1['s'] == msg['s']:
                    now = float(msg['p'])
                    back = float(ist_1['p'])
                    pr = (now - back) / now * 100
                    self.ist_1m.append(msg)
                    z1 = round(pr,3)
                    have = False

                    if ist_1['t'] + (1 * 60000) <= msg['t']:
                        self.ist_1m.remove(ist_1)
                    break
            if have:
                self.ist_1m.append(msg)

            have = True
            for ist_5 in self.ist_5m:
                if ist_5['s'] == msg['s']:
                    now = float(msg['p'])
                    back = float(ist_5['p'])
                    pr = (now - back) / now * 100
                    self.ist_5m.append(msg)
                    z2 = round(pr,3)
                    have = False

                    if ist_5['t'] + (5 * 60000) <= msg['t']:
                        self.ist_5m.remove(ist_5)
                    break
            if have:
                self.ist_5m.append(msg)

            have = True
            for ist_15 in self.ist_15m:
                if ist_15['s'] == msg['s']:
                    now = float(msg['p'])
                    back = float(ist_15['p'])
                    pr = (now - back) / now * 100
                    self.ist_15m.append(msg)
                    z3 = round(pr,3)
                    have = False

                    if ist_15['t'] + (15 * 60000) <= msg['t']:
                        self.ist_15m.remove(ist_15)
                    break
            if have:
                self.ist_15m.append(msg)

            data = {'s':msg['s'], 'pr':[z1,z2,z3], 't': msg['t']}

            def OUT(out):
                bot = self.bot

                def priceChangePercent(S):
                    session = HTTP(
                        testnet=False,
                        api_key="9kBNn0gpUuXK6s80l4",
                        api_secret="mZ3SJCj9FOuBQnVNnad3xqtrZZ0tp7aOm7qN",
                        recv_window=60000
                    )

                    # spot
                    # linear

                    tickers_spot = session.get_tickers(category="linear")
                    data_tickers = tickers_spot['result']['list']

                    for i in data_tickers:
                        if i['symbol'] == S:
                            return f"\n\n📌<b>Chg % 24h:</b>  <u>{round(float(i['price24hPcnt'])*100,3)}%</u>"

                price = priceChangePercent(out['s'])

                if price == None:
                    price = ''

                if out['pr'][0] >= 0:
                    m1 = (f"🟩<b>Price change:</b>  <u>{out['pr'][0]}%</u>\n"
                          f"👉<b>Interval:</b> 1m")
                else:
                    m1 = (f"🟥<b>Price change:</b>  <u>{out['pr'][0]}%</u>\n"
                          f"👉<b>Interval:</b> 1m")

                if out['pr'][0] >= 0:
                    m5 = (f"🟩<b>Price change:</b>  <u>{out['pr'][1]}%</u>\n"
                          f"👉<b>Interval:</b> 5m")
                else:
                    m5 = (f"🟥<b>Price change:</b>  <u>{out['pr'][1]}%</u>\n"
                          f"👉<b>Interval:</b> 5m")
                if out['pr'][0] >= 0:
                    m15 = (f"🟩<b>Price change:</b>  <u>{out['pr'][2]}%</u>\n"
                          f"👉<b>Interval:</b> 15m")
                else:
                    m15 = (f"🟥<b>Price change:</b>  <u>{out['pr'][2]}%</u>\n"
                          f"👉<b>Interval:</b> 15m")


                txt = (f"⚫️  <code>{out['s']}</code>\n"
                       f"#Bybit  #{out['s']}\n\n"
                       f'{m1}\n\n'
                       f'{m5}\n\n'
                       f'{m15}{price}')



                markup = types.InlineKeyboardMarkup()

                b1 = types.InlineKeyboardButton(text='TV',
                                                url=f"https://ru.tradingview.com/chart/{out['s']}.P")
                b2 = types.InlineKeyboardButton(text='CG',
                                                url=f"https://www.coinglass.com/tv/ru/Bybit_{out['s']}")
                b3 = types.InlineKeyboardButton(text='ПЕРЕХОД В БОТ',
                                                url=f"https://t.me/+NeaYSIqGPBtmYTNi")
                markup.add(b1, b2)
                markup.add(b3)
                bot.send_message(-1002276541068, txt, parse_mode='HTML', reply_markup=markup)
                print(txt)

            have_3m = True
            if data['pr'] != [None, None, None]:
                for _3m in self._3m:
                    if data['s'] == _3m['s']:
                        if data['pr'][0] >= self.par_1m or data['pr'][0] <= -self.par_1m or data['pr'][1] >= self.par_5m or data['pr'][1] <= -self.par_5m or data['pr'][2] >= self.par_15m or data['pr'][2] <= -self.par_15m:
                            if data['t'] >= _3m['t'] + (3 * 60000):
                                OUT(data)
                                self._3m.remove(_3m)
                                self._3m.append(data)
                            have_3m = False
                            break

                if have_3m:
                    if data['pr'][0] >= self.par_1m or data['pr'][0] <= -self.par_1m or data['pr'][1] >= self.par_5m or data['pr'][1] <= -self.par_5m or data['pr'][2] >= self.par_15m or data['pr'][2] <= -self.par_15m:
                        OUT(data)
                        self._3m.append(data)



def st_binance():
    try:
        threading.Thread(target=SocketConn_Binance, args=(f'wss://fstream.binance.com/ws/!markPrice@arr',)).start()
    except:
        time.sleep(5)
        st_binance()

def st_bybit():
    try:
        sb = sombol_bybit()
        threading.Thread(target=SocketConn_ByBit, args=(f'wss://stream.bybit.com/v5/public/linear',sb)).start()
    except:
        time.sleep(5)
        sombol_bybit()


def GO():
    Binance = Thread(target=st_binance)
    Binance.start()
    bybit = Thread(target=st_bybit)
    bybit.start()



if __name__ == '__main__':
    GO()







































