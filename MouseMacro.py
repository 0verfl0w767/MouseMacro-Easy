#
#            888                                               .d8888b.   .d8888b.  
#          888                                               d88P  Y88b d88P  Y88b 
#         888                                                     .d88P 888        
#     .d88888  .d88b.  888  888        888  888 .d8888b         8888"  888d888b.  
#   d88" 888 d8P  Y8b 888  888       888  888 88K               "Y8b. 888P "Y88b 
#  888  888 88888888 Y88  88P      888  888 "Y8888b.      888    888 888    888 
#  Y88b 888 Y8b.      Y8bd8P       Y88b 888      X88      Y88b  d88P Y88b  d88P 
#  "Y88888  "Y8888    Y88P         "Y88888  88888P'       "Y8888P"   "Y8888P"  
#                                     888                                       
#                               Y8b d88P                                       
#                                "Y88P"                                        
#
# Author: dev-ys-36 | Sahmyook Univ. CE. 22.
# Github: dev-ys-36 | https://github.com/dev-ys-36/MouseMacro-Easy
# License: MIT | https://github.com/dev-ys-36/MouseMacro-Easy/blob/main/LICENSE
# Version: 1.0.0v | First Released.
#
# The copyright indication and this authorization indication shall be
# recorded in all copies or in important parts of the Software.
#

import pyautogui, keyboard, pickle, time

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

for i in data:
    pyautogui.moveTo(i[0], i[1])

    if i[3] == 'cr':
        pyautogui.click(button='right', clicks=i[4])
    elif i[3] == 'cl':
        pyautogui.click(button='left', clicks=i[4])
    
    time.sleep(i[2])