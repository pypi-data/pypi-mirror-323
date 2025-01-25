import random
import time
from enum import Enum
from DrissionPage._pages.mix_tab import MixTab
from DrissionPage.common import Keys
class SleepTime(Enum):
    MOUSE_RELEASE = (0.1, 0.2)
    KEY_RELEASE = (0.1, 0.5)
    HUMAN_THINK = (0.2, 3)
    WAIT_PAGE = (1, 1.5)
    MOUSE_MOVE = (0.5, 3.0)
    NONE_OPERATION = (1, 5)
    DELETE_TEXT = (5, 10)

def sleep(sleep_time: SleepTime):
    time.sleep(random.uniform(sleep_time.value[0], sleep_time.value[1]))

def move_to(tab: MixTab, ele_or_loc):
    act = tab.actions
    return act.move_to(ele_or_loc, random.randint(5, 7), random.randint(5, 7), random.uniform(SleepTime.MOUSE_MOVE.value[0], SleepTime.MOUSE_MOVE.value[1]))

def click(tab: MixTab, ele_or_loc, more_real=True):
    act = tab.actions
    sleep(SleepTime.HUMAN_THINK)
    if more_real:
        move_to(tab, ele_or_loc).hold()
        sleep(SleepTime.MOUSE_RELEASE)
        act.release()
    else:
        move_to(tab, ele_or_loc)
        tab.ele(ele_or_loc).click()
        
    sleep(SleepTime.WAIT_PAGE)

def type(tab: MixTab, ele_or_loc, message: str, more_real=True):
    act = tab.actions
    sleep(SleepTime.HUMAN_THINK)
    # 没有指定元素，则直接模拟键盘输入
    if not ele_or_loc:
        act.type(message)
    else:
        if more_real:
            click(tab, ele_or_loc)
            act.type(message)
        else:
            tab.ele(ele_or_loc).input(message)
        
    sleep(SleepTime.WAIT_PAGE)

def send_key(tab: MixTab, key: Keys):
    act = tab.actions
    tab.actions.key_down(key)
    sleep(SleepTime.KEY_RELEASE)
    tab.actions.key_up(key)

def scroll(tab: MixTab, ele_or_loc, delta_y, delta_x):
    act = tab.actions
    move_to(tab,ele_or_loc)
    act.scroll(delta_y, delta_x)

def simulated_human(tab: MixTab):
    try:
        act = tab.actions
        # 1. 随机移动鼠标
        width, height = tab.rect.size
        x = random.randint(0, width)
        y = random.randint(0, height)
        act.move_to((x, y), duration=random.uniform(SleepTime.MOUSE_MOVE.value[0], SleepTime.MOUSE_MOVE.value[1]))
        
        # 模拟人类在移动完鼠标后略作停顿
        sleep(SleepTime.HUMAN_THINK)

        # 2. 随机决定是否进行滚轮滚动
        if random.random() < 0.6:  # 60% 的概率进行滚动操作
            # 滚动距离可以是向上或向下
            # delta_y 向下滚动为正，向上滚动为负
            delta_y = random.randint(-300, 300)  
            # 如果需要横向滚动，可设置 delta_x
            delta_x = 0  

            act.scroll(delta_y=delta_y, delta_x=delta_x)

            # 停顿一小段时间，模拟卷动后的停顿或浏览
            sleep(SleepTime.HUMAN_THINK)

        # 3. 随机等待，模拟人与人差异
        sleep(SleepTime.NONE_OPERATION)
    except Exception:
        pass