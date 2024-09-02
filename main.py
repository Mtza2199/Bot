import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from telegram import Bot

# إعداد بوت التلكرام
TELEGRAM_TOKEN = '6528637603:AAE2LizUBTuU9o6fMh47wDG6_dWNa7HhyFk'  # ضع هنا توكن بوت التلكرام
CHAT_ID = '295784396'  # ضع هنا الـ Chat ID الخاص بك

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# بدء MT5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# تسجيل الدخول إلى الحساب
account_number = 720780  # ضع هنا رقم حسابك
password = "sV3)j7;V"  # ضع هنا كلمة المرور
server = "Inzo-Demo"  # ضع هنا خادم الوسيط

login_status = mt5.login(account_number, password=password, server=server)

if login_status:
    print("Login successful")
else:
    print("Login failed")
    mt5.shutdown()

# الحصول على بيانات الشموع
symbol = "EURUSD"
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)

# تحويل البيانات إلى DataFrame لتحليلها باستخدام pandas
rates_frame = pd.DataFrame(rates)
rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

# حساب متوسط الحركة البسيط (SMA) لفترة 14 شمعة
rates_frame['SMA'] = rates_frame['close'].rolling(window=14).mean()

# حساب مؤشر القوة النسبية (RSI) لفترة 14 شمعة
delta = rates_frame['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rates_frame['RSI'] = 100 - (100 / (1 + rs))

# عرض البيانات المحللة
print(rates_frame[['time', 'close', 'SMA', 'RSI']])

# الحصول على آخر بيانات الشموع
latest_data = rates_frame.iloc[-1]
previous_data = rates_frame.iloc[-2]

# تنفيذ استراتيجية تداول بسيطة بناءً على SMA و RSI
if latest_data['close'] > latest_data['SMA'] and latest_data['RSI'] < 30:
    print("Buy Signal")
    # إعداد وتنفيذ أمر شراء
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.1,  # حجم الصفقة
        "type": mt5.ORDER_TYPE_BUY,  # نوع الأمر شراء
        "price": mt5.symbol_info_tick(symbol).ask,
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script buy order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(order_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Buy Order failed, retcode={result.retcode}")
        send_telegram_message(f"Buy Order failed for {symbol}, retcode={result.retcode}")
    else:
        print(f"Buy Order executed, {result}")
        send_telegram_message(f"Buy Order executed for {symbol}: Volume {order_request['volume']} at price {order_request['price']}")

elif latest_data['close'] < latest_data['SMA'] and latest_data['RSI'] > 70:
    print("Sell Signal")
    # إعداد وتنفيذ أمر بيع
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.1,  # حجم الصفقة
        "type": mt5.ORDER_TYPE_SELL,  # نوع الأمر بيع
        "price": mt5.symbol_info_tick(symbol).bid,
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script sell order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(order_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Sell Order failed, retcode={result.retcode}")
        send_telegram_message(f"Sell Order failed for {symbol}, retcode={result.retcode}")
    else:
        print(f"Sell Order executed, {result}")
        send_telegram_message(f"Sell Order executed for {symbol}: Volume {order_request['volume']} at price {order_request['price']}")
else:
    print("No clear signal, no trade executed")

# إنهاء اتصال MT5
mt5.shutdown()
