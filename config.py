# -*- coding: utf-8 -*-
#!/usr/bin/python3


# PM閾値 15分強
def pm_threshold():
    return 15

# PM閾値 auto
def air_auto():
    return 10

# ambientキー
def ambi():
    # ambientのテストチャンネル ID,ライトキー
    # ご自身のambient設定に変更してください。
    ch_ID,write_KEY = 123456,"11fxxxx0f22d"
    return ch_ID,write_KEY 
