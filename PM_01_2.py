"""
2026/03/02  花粉推定
2026/03/04  max
            測定はlib_pms7003.pyに任せる
            1分値を作る
            ambient送信
2026/03/05  送信エラー処理
2026/03/08  pollenの値がうまくいかないので、削除
2026/03/22  config対応
2026/03/24  LED対応
2026/03/28  ambientタイムアウトを追加
"""

import time
import http.client
import json
import ssl
import pigpio

import config
import lib_pms7003

# センサーのオープン
fd = lib_pms7003.pms7003_open()

CHANNEL_ID, WRITE_KEY= config.ambi()
print(CHANNEL_ID, WRITE_KEY)

LED1 = 17
led = pigpio.pi()
# 出力設定
led.set_mode(LED1, pigpio.OUTPUT)

for _ in range(5):
    led.write(LED1, 1) # LED点灯
    time.sleep(0.5)
    led.write(LED1, 0) # LED消灯
    time.sleep(0.1)

# センサーからデータを取得して、1分平均値を得る
def read_pollen():
    pm1_buffer = []
    pm25_buffer = []
    pm10_buffer = []
    while True:
        result = lib_pms7003.pms7003_read(fd)
        if result:
            pm1, pm25, pm10 = result
            pm_all = pm1 + pm25 + pm10
            print("PM1.0:", pm1," PM2.5:", pm25," PM10 :", pm10, "PM_add=",pm_all,end='', flush=True)
            
            for _ in range(pm_all // 6):
                print("*",end='', flush=True)
            print()
        else:
            print('sensor err')
            pm1, pm25, pm10 = 0,0,0

        pm1_buffer.append(pm1)
        pm25_buffer .append(pm25)
        pm10_buffer.append(pm10)

        " 1分平均値を作る"
        if len(pm10_buffer) >= 60:
            minute_pm1  = round(sum(pm1_buffer)  / len(pm1_buffer),1)
            minute_pm25 = round(sum(pm25_buffer) / len(pm25_buffer),1)
            minute_pm10 = round(sum(pm10_buffer) / len(pm10_buffer),1)
            pm10_buffer.clear()
            break

        # pm_allが15以上であれば、LEDを点灯
        time.sleep(0.2)
        if pm_all > 15:
            led.write(LED1, 1) # LED点灯
        time.sleep(0.8)
        led.write(LED1, 0) # LED消灯
        

    return minute_pm1,minute_pm25,minute_pm10

# pipを使わずにambientにデータ送信
def sen_ambient(data):
        json_data = json.dumps(data)
        conn = http.client.HTTPSConnection(
            "ambidata.io",
            timeout=5
        )
        headers = {"Content-Type": "application/json"}
        # mbient err処理
        try:
            conn.request(
                "POST",
                f"/api/v2/channels/{CHANNEL_ID}/data",
                json_data,headers
                )
            response = conn.getresponse()
            conn.close()
            # print(response.status, response.read())
        except:
            print("ambient err")
        

# ==============================
# メイン
# ==============================
def main():
    
    print("PMS7003 安全版 + 花粉推定開始")
    while True:
        minute_pm1,minute_pm25,minute_pm10 = read_pollen()
        print(" 1分平均値 ",minute_pm1,minute_pm25,minute_pm10 )

        # ambientにデータを送信
        PM_total = minute_pm1 + minute_pm25 + minute_pm10
        data = {
            "writeKey": WRITE_KEY,
            "d1": minute_pm1,   # PM10
            "d2": minute_pm25,  # PM2.5
            "d3": minute_pm10,  # PM10   
            "d4": PM_total,     # PM total 
            }
        sen_ambient(data)


if __name__ == "__main__":
    main()


"""
データ	内容
単位：μg/m³

🔳 運用ポイント
起動直後は数十秒安定しない
連続測定より 10秒間隔がおすすめ
ファンがあるので消費電力約100mA

🔳 µg/m³（マイクログラム毎立方メートル）とは？
読み方：マイクログラム パー 立方メートル
意味：「空気 1立方メートルの中に、どれだけの重さの粒子が含まれているか」

🔳 イメージすると
1m³の空気の中に：
PM2.5	   意味
5 µg/m³	   とてもきれい
20 µg/m³	少し汚れている
50 µg/m³	健康注意レベル
100 µg/m³	かなり悪い

🔳 PMの意味
種類	粒の大きさ
PM1.0	1µm以下
PM2.5	2.5µm以下
PM10	10µm以下

1µm = 髪の毛の太さの約1/70
"""
