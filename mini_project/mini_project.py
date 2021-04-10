#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import subprocess
import pygame
import pifacecad
from time import sleep
from pyowm.owm import OWM
from pifacecad.tools.scanf import LCDScanf


def time_now():
    cad.lcd.clear()
    global now
    now = datetime.now()
    cad.lcd.set_cursor(0, 0)
    cad.lcd.write(now.strftime("%m/%d %a %H:%M "))


def weather_print(k):
    cad.lcd.clear()
    cad.lcd.write(City[k])
    cad.lcd.set_cursor(0, 1)
    cad.lcd.write(weather_[k])


cad = pifacecad.PiFaceCAD()
cad.lcd.backlight_on()
cad.lcd.cursor_off()

City = ['Harbin,CN', 'Tokyo,JP', 'Seoul,KR', 'Bangkok,TH', 'Vancouver,CA', 'Paris,FR']
mykey = 'fbfe70688650a2d288b6cceba3812496'
owm = OWM(mykey)
mgr = owm.weather_manager()
weather_ = ['0', '0', '0', '0', '0', '0']
for i in range(6):
    obs = mgr.weather_at_place(City[i])
    weather = obs.weather
    weather_[i] = weather.status

k = 0
time_now()
AlarmMusicStarted = 0
AlarmSet = 0
while 1:
    if datetime.now().minute != now.minute:
        # 1분 지날때마다 체크
        AlarmMusicStarted = 0
        time_now()
        if AlarmSet == 1 and AlarmMusicStarted == 0 and time[0] == now.hour and time[1] == now.minute:
            # 알람이 세팅되어있고 현재 시각이 알람시각과 같으면
            AlarmMusicStarted = 1
            pygame.init()
            pygame.mixer.music.load("/home/pi/mini_project/lava.mp3")
            pygame.mixer.music.play()
            cad.lcd.clear()
            cad.lcd.write("    A L A R M   ")
            cad.lcd.set_cursor(0, 1)
            cad.lcd.write("Press Joystick")
            # 알람 음악틀기
    if cad.switches[4].value:
        # 종료, 전체 while문 break
        break
    if cad.switches[0].value:
        # 날씨
        cad.lcd.clear()
        cad.lcd.write("weather mode!")
        sleep(1)
        weather_print(k)
        while 1:
            if cad.switches[7].value:
                sleep(0.2)
                k = (k + 1) % 6
                weather_print(k)
            if cad.switches[6].value:
                sleep(0.2)
                k = (k - 1) % 6
                weather_print(k)
            if cad.switches[1].value:
                cad.lcd.clear()
                time_now()
                break
    if cad.switches[2].value:
        # 알람모드
        breakSwitch2 = 0
        # 알람재설정시
        if AlarmSet == 1:
            # 이미 알람이 설정되어있다면
            cad.lcd.clear()
            cad.lcd.set_cursor(0, 0)
            cad.lcd.write("Alarm Change?")  # 변경 여부 묻기
            cad.lcd.set_cursor(0, 1)
            cad.lcd.write(">No     Yes")
            ChangeAlarm_idx = False
            while True:
                if cad.switches[6].value or cad.switches[7].value:  # 조이스틱 좌 우로 움직이면
                    ChangeAlarm_idx = not ChangeAlarm_idx

                    # Yes 또는 No에 따라서 > 위치 지정하기
                    cad.lcd.set_cursor(0, 1)
                    cad.lcd.write(" " if ChangeAlarm_idx else ">")
                    cad.lcd.set_cursor(7, 1)
                    cad.lcd.write(">" if ChangeAlarm_idx else " ")
                    sleep(0.2)  # 과다 입력 방지
                if cad.switches[5].value:  # 5번으로 선택하면
                    if ChangeAlarm_idx:  # Yes 선택시
                        AlarmSet = 0  # 설정된 알람 해제
                        break
                    else:
                        breakSwitch2 = 1  # No선택시 알람모드 탈출
                        time_now()
                        break
        if not breakSwitch2:
            # No를 선택하지 않았거나 이미 알람이 설정되어있지 않았을 경우
            cad.lcd.clear()
            cad.lcd.set_cursor(0, 0)
            cad.lcd.write("Alarm mode")
            sleep(1)
            scanner = LCDScanf("Alarm %2i:%2i%m%r",custom_values=(" "))
            time = scanner.scan()
            if time[0] > 24 or time[1] >59:
                cad.lcd.clear()
                cad.lcd.write("EXCEED")
                sleep(1)
                while 1:
                    scanner = LCDScanf("Alarm %2i:%2i%m%r",custom_values=(" "))
                    time = scanner.scan()
                    if time[0] <=24 or time[1] <= 59:
                        break
                    else:
                        cad.lcd.clear()
                        cad.lcd.write("EXCEED")
                        sleep(1)

            cad.lcd.clear()
            cad.lcd.write("Alarm set")
            sleep(1)
            time_now()
            AlarmSet = 1

    if cad.switches[3].value:
        if AlarmSet:  # 알람이 설정되어 있다면 알람 표시
            cad.lcd.clear()
            cad.lcd.write("Alarm set")
            cad.lcd.set_cursor(0, 1)
            cad.lcd.write(f'{time[0]:02d}:{time[1]:02d}')
            sleep(2)
            time_now()
        else:  # 알람이 설정되어있지 않다면 예외처리
            cad.lcd.clear()
            cad.lcd.write("No Alarm set")
            sleep(2)
            time_now()

    if cad.switches[5].value and AlarmMusicStarted == 1:
        # 알람 음악이 재생되는 상태에서 5번 버튼 누르기
        pygame.mixer.music.stop()
        AlarmMusicStarted = 0
        AlarmSet = 0
        time_now()

cad.lcd.clear()
cad.lcd.write("GOODBYE")
sleep(2)
cad.lcd.clear()
cad.lcd.backlight_off()
