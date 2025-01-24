
import pyautogui, keyboard, pickle, time
import win32api, win32gui

class draw:
    def __init__(self):
        hwnd = win32gui.GetDesktopWindow()
        self.hdc = win32gui.GetDC(hwnd)
        
    def rect(self, x, y, w, h, thickness=2, color=False):
        left = x - w // 2
        top = y - h // 2
        color = win32api.RGB(0,255,0) if not color else win32api.RGB(color[0], color[1], color[2])
        
        for i in range(left, left + w):
            for t in range(thickness):                                  # 두께만큼 반복
                win32gui.SetPixel(self.hdc, i, top + t, color)          # 상단
                win32gui.SetPixel(self.hdc, i, top + h - t - 1, color)  # 하단
        
        for j in range(top, top + h):
            for t in range(thickness):                                  # 두께만큼 반복
                win32gui.SetPixel(self.hdc, left + t, j, color)         # 좌측
                win32gui.SetPixel(self.hdc, left + w - t - 1, j, color) # 우측

pyautogui.FAILSAFE = False

setting = True
num = 0
data = []

print('매크로 사용자 설정을 시작합니다.')
print('마우스 포인트 있는 좌표로 설정합니다.')
print('Ctrl 키: 마우스 좌표 설정, Alt 키: 설정 중단 후 매크로 시작')

#setting
while setting:
    if keyboard.is_pressed('Ctrl'):
        num += 1
        print(str(num) + '번째 좌표를 설정했습니다. ' + str(pyautogui.position()))
        mouse_position = pyautogui.position()

        delay = input('지연 시간을 입력하세요: ')
        event = input('이벤트를 입력하세요: ')
        clicks = input('클릭 횟수를 입력하세요: ')

        print('지연 시간: ' + delay + '초, 이벤트: ' + event + ', 클릭 횟수: ' + clicks)
        data_setting = (int(delay), event, int(clicks))

        data.append(mouse_position + data_setting)
        time.sleep(0.5)
        continue

    if keyboard.is_pressed('Alt'):
        print('매크로 사용자 설정을 마칩니다.')
        time.sleep(0.5)
        break

with open('setting.txt', 'wb') as file:
    pickle.dump(data, file)

app = draw()

while True:
    if keyboard.is_pressed('esc'):
        print('매크로를 종료합니다.')
        break
    
    for i in data:
        app.rect(i[0], i[1], 25, 25)
        
        pyautogui.moveTo(i[0], i[1])

        if i[3] == 'cr':
            pyautogui.click(button='right', clicks=i[4])
        elif i[3] == 'cl':
            pyautogui.click(button='left', clicks=i[4])
        
        time.sleep(i[2])