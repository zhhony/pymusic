import mp3play
import json
from time import sleep
from pathlib import Path
from threading import Thread
from typing import *


# 定义发声函数
def __voice(note: str, voice: int) -> None:
    path = Path('D:/WorkShop/Python/standard_pitch')  # 88标准音位置
    mp3Path = path / (note + '.mp3')
    note = mp3play.load(str(mp3Path))
    note.volume(voice)
    note.play()
    sleep(4)
    note.stop()


# 根据提供的路径获取乐谱并转化为pythonlist对象
def __MusicLoad(musicPath: Path) -> list:
    return json.load(open(musicPath))


# 对输入的乐谱从0拍开始往下计数，编出每一个基本拍所要演奏的音符组，形成含有拍数的乐谱并返回
def __TimeStamp(music: list) -> list:
    beat = 0  # 从0开始计算拍数
    notesWithBeat = []
    musicScoreWithBeat = []
    for notes in music:
        notesWithBeat = notes.copy()
        notesWithBeat.append(int(beat))
        musicScoreWithBeat.append(notesWithBeat)
        beat += notes[1]*32
    return musicScoreWithBeat


# 返回一个装载乐谱的生成器,按顺序每next一次放出一个音符组
def __MusicGenerator(music: list) -> list:
    for notes in music:
        yield notes


# 后台同步进程，每过MUSIC_TIME_STAMP秒，往前推进一基本拍，并进行一次乐谱检测。如果监测到音符组，则对此音符执行子进程。
def __DaemonSynchronizationThread(musicGeneratorA: Generator, musicGeneratorB: Generator, speed: int) -> float:
    MUSIC_MIN_TIME_STAMP = 60/speed/8  # 一基本拍的时间(基本拍：一个32分音符为一拍，区别于一般意义的拍)
    beat = 0
    notesA = next(musicGeneratorA)  # 获取A的音符组
    notesB = next(musicGeneratorB)  # 获取B的音符组
    while True:
        if notesA[-1] == beat:
            __addThread(notesA)
            notesA = next(musicGeneratorA)  # 获取下一个音符组
        if notesB[-1] == beat:
            __addThread(notesB)
            notesB = next(musicGeneratorB)  # 获取下一个音符组
        beat += 1
        sleep(MUSIC_MIN_TIME_STAMP)


# 针对传递过来的音符组，建立演奏线程
def __addThread(notes: list) -> None:
    ThreadList = []
    for note in notes[0]:
        t = Thread(target=__voice, args=(note, notes[2]))
        ThreadList.append(t)
    for j in ThreadList:
        j.start()


# 读取文件获取基础参数
userCmd = ['紫竹调A轨.json', '紫竹调B轨.json', 440]
music = __MusicLoad(Path(userCmd[0]))
chord = __MusicLoad(Path(userCmd[1]))
speed = userCmd[2]

# 转化为带有基本拍的乐谱
musicScoreWithBeat = __TimeStamp(music)
chordScoreWithBeat = __TimeStamp(chord)

# 创造乐谱生成器
musicGenerator = __MusicGenerator(musicScoreWithBeat)
chordGenerator = __MusicGenerator(chordScoreWithBeat)


__DaemonSynchronizationThread(musicGenerator, chordGenerator, speed)
