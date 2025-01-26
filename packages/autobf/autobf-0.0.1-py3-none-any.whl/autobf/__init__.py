import numpy as np
import pyautogui
import pydirectinput
import time
import keyboard
import cv2

Xc=1920/2
Yc=1080/2
def row(x,y,dx=0,dy=0,button='right',delay=0.2):
    '''
    在 (x,y) 處，按下滑鼠 button 鍵後拖曳 dx,dy
    '''
    pydirectinput.mouseDown(x,y,button=button);time.sleep(delay)
    pydirectinput.moveTo(x+dx,y+dy);    time.sleep(delay)
    pydirectinput.mouseUp(button=button)
    
def zoom2max():
    '''
    拉最遠並把視角放到頭頂
    '''
    global Xc,Yc
    for i in range(10):    pyautogui.scroll(-500)
    row(Xc,Yc,dy=50)
    row(Xc,Yc,dy=50)
    
def click(x,y,repeat=1,delay=0):
    '''
    點擊 x,y 重複 repeat 次，每次延遲 delay 秒
    '''
    for i in range(repeat):
        pydirectinput.click(x,y);pydirectinput.click(x+1,y+1);time.sleep(delay)
        
def slide(key='down',repeat=1):
    '''
    按q滑行，由 key 指定方向， 重複repeat次
    '''
    for i in range(repeat):
        pydirectinput.keyDown(key)
        pydirectinput.press('q')
        pydirectinput.keyUp(key)
    
def keyDown(key,duration=2):
    '''
    按下 key , 等待 duration 秒後放開
    '''
    pydirectinput.keyDown(key);time.sleep(duration);pydirectinput.keyUp(key)

def reset(delay=8):
    '''
    重設色角色 esc + r + enter
    '''
    pydirectinput.press('esc');time.sleep(1)
    pydirectinput.press('r');time.sleep(1)
    pydirectinput.press('enter')
    time.sleep(sleep)
    
def findColors(image, target_color, tolorance=0):
    '''
    給定 image ，在上面找到和 target_color 相近顏色的座標
    並回傳座標陣列，tolorance 為容忍範圍
    '''
    a=np.array(image)
    b=np.array(target_color)
    dist = np.linalg.norm(a-b, axis=-1)
    return np.argwhere(dist <= tolorance)

def findNearestColor(color):
    '''
    找到離角色(螢幕中心)最近的指定顏色 color
    '''
    global Xc,Yc
    img = pyautogui.screenshot()
    try:
        a = findColors(img,color,0)
        if len(a)<0:return -1,-1
        b = np.array([Yc,Xc])
        i = np.argmin(np.linalg.norm(a-b,axis=-1))
        y,x = a[i]
    except:return -1,-1
    return x,y

def instinctOn(size=100):
    '''
    檢查是否開啟見聞色，落未開啟啟見聞色就按下e開啟它，
    檢查範圍預設為 [Yc-size:Yc+size,Xc-size:Xc+size]
    '''
    global Xc,Yc
    img = np.array(pyautogui.screenshot())[Yc-size:Yc+size,Xc-size:Xc+size]
    G=len(findColors(img,[184,184,184],2))
    Y=len(findColors(img,(255, 255, 100),100))
    if Y>20000 and G<1000:press('e')

def getMission(p1=(1448,562),p2=(1360,513)):
    global Xc,Yc
#     1433,566
    click(Xc,Yc,delay=2)
    click(p1[0],p1[1]);time.sleep(2)
#     click(1448,562);time.sleep(2)
    row(Xc,Yc)
    click(p2[0],p2[1]);time.sleep(2)
    click(p2[0],p2[1]);time.sleep(2)
    
def findNearestEnemy():
    img = pyautogui.screenshot()
    try:
        a = findColors(img,[255,0,0],0)
        if len(a)<0:return -1,-1
        b = np.array([Yc,Xc])
        i = np.argmin(np.linalg.norm(a-b,axis=-1))
        y,x = a[i]
    except:return -1,-1
    return x,y

def shotEnemy():
    x,y = findNearestEnemy()
    if x>0:
        press('4');row(x,y,dx=1,sleep=0)
        click(x,y);press('2')
        return True
    return False   