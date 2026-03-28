#!/usr/bin/python
"""
2026/3/25   ライセンスフリー pms7003ドライバー
            serialを使わない
"""
import os
import termios
import time
import struct

# --- 初期化 ---
def pms7003_open(device="/dev/serial0"):
    try:
        fd = os.open(device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except:
        try:
            fd = os.open("/dev/ttyS0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        except:
            fd = os.open("/dev/ttyAMA0", os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    # ボーレート設定
    baud = termios.B9600
    attrs[4] = baud
    attrs[5] = baud
    # rawモード
    attrs[0] = 0
    attrs[1] = 0
    attrs[2] = attrs[2] | termios.CS8
    attrs[3] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd


# --- クローズ ---
def pms7003_close(fd):
    if fd:
        os.close(fd)


# --- パース ---
def pms7003_parse(frame):
    pm1  = struct.unpack('>H', frame[10:12])[0]
    pm25 = struct.unpack('>H', frame[12:14])[0]
    pm10 = struct.unpack('>H', frame[14:16])[0]
    return pm1, pm25, pm10


# --- データ取得 ---
def pms7003_read(fd):
    buffer = b""
    while True:
        try:
            buffer += os.read(fd, 32)
        except BlockingIOError:
            time.sleep(0.05)
            continue
        if len(buffer) < 32:
            continue
        start = buffer.find(b'\x42\x4d')
        if start == -1:
            buffer = b""
            continue
        frame = buffer[start:start+32]
        if len(frame) < 32:
            continue
        checksum = sum(frame[0:30])
        received = struct.unpack(">H", frame[30:32])[0]
        if checksum != received:
            buffer = b""
            continue
        return pms7003_parse(frame)


# --- メイン ---
def main():
    fd = pms7003_open()

    try:
        while True:
            pm1, pm25, pm10 = pms7003_read(fd)

            PM_add = pm1 + pm25 + pm10
            print("PM1.0:", pm1, "PM2.5:", pm25, "PM10:", pm10, "PM_add=", PM_add, " ", end='', flush=True)

            pm_all = PM_add // 6
            for _ in range(pm_all):
                print("*", end='', flush=True)
            print()

    except KeyboardInterrupt:
        pass

    finally:
        pms7003_close(fd)


if __name__ == "__main__":
    main()