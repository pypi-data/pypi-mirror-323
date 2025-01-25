#!/usr/bin/env python
# -*- coding:utf-8 -*-


class FingerPrint:
    def __init__(self, tab):
        self.tab = tab

    def set_timezone(self, timezone="Europe/London"):
        timezone = {
            "method": "Emulation.setTimezoneOverride",
            "params": {
                "timezoneId": timezone
            }
        }
        self.tab.run_cdp(timezone.get('method'), **timezone.get('params'))
        return self

    def set_setGeolocation(self, latitude=51.5074, longitude=-0.1276):
        setGeolocation = {
            "method": "Emulation.setGeolocationOverride",
            "params": {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": 100
            }
        }
        self.tab.run_cdp(setGeolocation.get('method'), **setGeolocation.get('params'))
        return self



    def set_user_agent(self,user_agent,platform='iPhone',acceptLanguage='en-GB'):

        apple_ua={
        "method": "Network.setUserAgentOverride",
        "params": {
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "platform": "iPhone",
            "acceptLanguage": "en-GB"
          }
        }
        ua={
        "method": "Network.setUserAgentOverride",
        "params": {
            "userAgent": user_agent,
            "platform": platform,
            "acceptLanguage": acceptLanguage
          }
        }
        self.tab.run_cdp(ua.get('method'),**ua.get('params'))
        return self    
    def set_touch_mode(self, enabled=True, maxTouchPoints=1):
        # 如果 maxTouchPoints 为 0，强制禁用 touch 模式
        if maxTouchPoints == 0:
            enabled = False

        # 构造触摸模式参数，仅在 enabled 为 True 时包含 maxTouchPoints
        touch_mode = {
            "method": "Emulation.setTouchEmulationEnabled",
            "params": {"enabled": enabled}
        }

        if enabled:  # 只有启用触摸模式时才添加 maxTouchPoints 参数
            touch_mode["params"]["maxTouchPoints"] = maxTouchPoints

        # 调用 CDP 方法
        self.tab.run_cdp(touch_mode.get("method"), **touch_mode.get("params"))
        return self
    def clear_rpa_feature(self):

        ClearRPAFeature={
        "method": "Emulation.setAutomationOverride",
        "params": {
            "enabled": False  # 启用或禁用自动化行为伪装 如果为 true，浏览器会伪装成正常的用户交互行为；如果为 false，则恢复自动化脚本的行为。
            }
        }
        self.tab.run_cdp(ClearRPAFeature.get('method'),**ClearRPAFeature.get('params'))
        return self

    def disable_cookies(self):
        DisableCookies={
        "method": "Emulation.setDocumentCookieDisabled",
        "params": {
            "disabled": True  # 禁用 document.cookie 访问
         }
        }
        self.tab.run_cdp(DisableCookies.get('method'),**DisableCookies.get('params'))
        return self
    def set_CPU_core(self,core=2):
        SetCPUCore={
            "method": "Emulation.setHardwareConcurrencyOverride",
            "params": {
                "hardwareConcurrency": core # 设置模拟的硬件并发数（CPU 核心数）
            }
        }
        self.tab.run_cdp(SetCPUCore.get('method'),**SetCPUCore.get('params'))
        return self    
    def time_speed(self,policy='advance',budget=1000):

        if policy=="pause":
            config={  
                "policy": "pause"
            }
        if policy=="advance":
            config={
                "policy": "advance",
                "budget": budget
            }
        if policy=="realtime":
            config={
                "policy": "realtime"
            }        
        self.tab.run_cdp("Emulation.setVirtualTimePolicy",**config)
        return self
    # def set_Locale(self):  # 设置模拟的地理位置、语言和时区
    #     SetLocale={
    #         "locale": "en-US",
    #         "acceptLanguage": "en-US,en;q=0.9",
    #         "timezoneId": "America/New_York",
    #         "platform": "ios",
    #         "geolocation": {
    #             "latitude": 40.7128,
    #             "longitude": -74.0060,
    #             "accuracy": 100
    #         }
    #     }
    #     self.tab.run_cdp("Emulation.setLocaleOverride",**SetLocale)
    #     return self 
    def set_3D(self,x=1,y=0,z=0,alpha=10,beta=20,gamma=30):
        json={
        "type":  "gyroscope" ,
        "reading":{
            "xyz":[x,y,z],

            }
        }
        self.tab.run_cdp("Emulation.setSensorOverrideReadings",**json)
        return self


    def set_size(self,width=360,height=740,mobile=True,scale=1):
        """
        mobile必须为true才能设置屏幕尺寸否则开启模拟后将被检测到使用固定屏幕尺寸，浏览器内窗口尺寸却会变化
        """
        zoom = {
            "command": "Emulation.setDeviceMetricsOverride",
            "parameters": {
                "width": width,                # 移动设备宽度
                "height": height,               # 移动设备高度
                "deviceScaleFactor": 1,      # DPI 比例
                "mobile": True,              # 设置为手机模式
                "scale": scale                   # 页面缩放比例
            }
        }
        self.tab.run_cdp(zoom["command"], **zoom["parameters"])

    def reset_size(self):
        self.tab.run_cdp('Emulation.clearDeviceMetricsOverride')
    