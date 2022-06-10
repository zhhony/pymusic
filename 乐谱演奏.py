import time
import mp3play
import pathlib
from threading import Thread
import json
from typing import *


def voice(note: str, voice: int) -> None:  # 定义发声函数
    path = pathlib.Path('D:/WorkShop/Python/standard_pitch')  # 88标准音位置
    mp3Path = path / (note + '.mp3')
    note = mp3play.load(str(mp3Path))
    note.volume(voice)
    note.play()
    time.sleep(4)
    note.stop()


def __addThread(notes: list, speed: int) -> None:  # 针对每一个音符建立单个线程以支持多个音符同时按下
    ThreadList = []
    for note in notes[0]:
        t = Thread(target=voice, args=(note, notes[2]))
        ThreadList.append(t)
    for j in ThreadList:
        j.start()
    sleeptime = notes[1]/(speed/60)
    time.sleep(sleeptime)


def music_line(music: list, speed: int) -> None:  # 针对右手的每一行谱子传递给线程建立函数
    for notes in music:
        __addThread(notes, speed)


def chord_line(chord: list, speed: int) -> None:  # 针对左手的每一行谱子传递给线程建立函数
    for notes in chord:
        __addThread(notes, speed)


def run(music_json: str, chord_json: str, speed: int) -> None:  # 定义播放函数
    music = json.load(open(music_json))  # 右手乐谱
    t1 = Thread(target=music_line, args=(music, speed))  # 右手线程
    t1.start()

    if chord_json is not None:  # 左手乐谱
        chord = json.load(open(chord_json))
        t2 = Thread(target=chord_line, args=(chord, speed))  # 左手线程
        t2.start()

# run('紫竹调A轨.json','紫竹调B轨.json',70)
# run('music2.json','chord2.json',76)

