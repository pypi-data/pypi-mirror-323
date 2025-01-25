from abc import ABC, abstractmethod
import os
import threading
import time
from DrissionPage import Chromium, ChromiumOptions
import loguru
from wakepy import keep
from .plugin.intercept import Intercept
from .utils.port import find_free_port
from DrissionPage.errors import PageDisconnectedError
class BaseBrowser(ABC):
    """
    Browser类负责业务逻辑与页面操作。
    """

    def __init__(self, browser_id, data_dir= "", proxy_ip = "", addr = ""):
        """
        初始化一个 BaseBrowser 实例
        
        :param browser_id: (str) 该浏览器实例的唯一标识，用于区分不同的浏览器实例。
        :param data_dir:   (str) 指定浏览器用户数据（User Data）与缓存（Cache）等文件的存储路径。
        :param proxy_ip:   (str) 代理 IP，当前仅支持无验证代理。
        :param addr:       (str) 如果需要连接到已在运行的浏览器实例，可传入其远程调试地址；若为空则新建一个浏览器实例。
        """
        self.browser_id = browser_id
        self.data_dir= data_dir
        self.proxy_ip = proxy_ip
        self.addr = addr
        from .website import BaseWebsite
        self.website: "BaseWebsite" = None
        self._stop_event = threading.Event()
        self._init_browser()
        self._after_init_browser()
        

    def _init_browser(self):
        try:
            if self.addr:
                self.dbrowser = Chromium(addr_or_opts=self.addr)
                self.tab = self.dbrowser.latest_tab
            else:
                options = ChromiumOptions().set_paths(local_port=find_free_port(),
                    user_data_path=os.path.join(self.data_dir ,f"user/{self.browser_id}"),
                    cache_path=os.path.join(self.data_dir ,"cache"))
            
                # 代理ip只支持无验证的代理
                if self.proxy_ip:
                    options.set_proxy(self.proxy_ip)

                try:
                    self.dbrowser = Chromium(addr_or_opts=options)
                    self.tab = self.dbrowser.latest_tab
                except Exception as e:
                    loguru.logger.exception(e)
                    tip="\n启动浏览器失败！请按照以下步骤检查错误：\n" \
                    "1. 请检查是否安装了Chrome浏览器（谷歌浏览器）\n" \
                    "2. 关闭正在运行的Chrome浏览器后重启本程序。\n" \
                    "3. 请不要同时运行多个本程序。\n"
                    loguru.logger.exception(tip)
                    time.sleep(1e9)
            self._init_website()
            if not self.website:
                raise ValueError('请重写_init_website方法并在其中对self.website进行赋值')
            self.tab.set.auto_handle_alert(accept=True)
            self.tab.set.window.max()
            self.tab.console.start()
            self.tab.listen.start(self.website.listen_paths)
            threading.Thread(target=self._listen_console, daemon=True).start()
            threading.Thread(target=self._listen_path, daemon=True).start()
            threading.Thread(target=self._prevent_system_sleep, daemon=True).start()
            threading.Thread(target=self._browser_is_alive, daemon=True).start()
            self._start_intercept()
            self.website.open_base_url()
        except Exception as e:
            loguru.logger.exception(f"[BrowserInit] 异常: {e}")
            self.close()

    def _prevent_system_sleep(self):
        with keep.running():
            while not self._stop_event.is_set():
                time.sleep(1)
    
    def _start_intercept(self):
        Intercept(self.tab, self.dbrowser)

    def _after_init_browser(self):
        """
        在浏览器初始化完成后执行的操作。
        
        默认实现为空，可在子类中重写此方法，以在浏览器初始化完成后执行自定义逻辑，
        如：预加载页面、设置cookie、执行登录操作等。
        """
        pass

    @abstractmethod
    def _init_website(self):
        """
        初始化 Website（站点）对象。

        默认实现为空，请在子类中重写此方法，创建自定义站点（继承BaseWebsite）的初始化工作，并设置self.website
        """
        pass

    def _before_close(self):
        pass

    def _after_close(self):
        pass

    def close(self):
        """关闭浏览器"""
        try:
            self._before_close()
        except Exception as e:
            loguru.logger.exception(e)
        try:
            self._stop_event.set()
            self.dbrowser.quit()
        except Exception:
            pass
        self._after_close()

    def _browser_is_alive(self):
        while not self._stop_event.is_set():
            try:
                self.tab.url
            except (PageDisconnectedError, Exception):
                self.close()
                loguru.logger.warning(f"检测到浏览器已关闭！ID: {self.browser_id}")

    def _listen_path(self):
        """进行请求监听"""
        while not self._stop_event.is_set():
            try:
                for response in self.tab.listen.steps():
                    if self.website.listen_path_callback:
                        self.website.listen_path_callback(response)
            except Exception as e:
                loguru.logger.exception(f"[_listen_path]错误{e}")

    def _listen_console(self):
        """进行控制台监听"""
        while not self._stop_event.is_set():
            try:
                for response in self.tab.console.steps():
                    if self.website.listen_console_callback:
                        self.website.listen_console_callback(response)
            except Exception as e:
                loguru.logger.exception(f"[_listen_console] 错误{e}")

