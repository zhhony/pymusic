import mp3play
import json
import argparse
from time import sleep
from pathlib import Path
from threading import Thread
from typing import *


# 定义发声函数
def __voice(note: str, voice: int) -> None:
    path = Path('./standard_pitch')  # 88标准音位置
    mp3Path = str(path / (note + '.mp3'))
    note = mp3play.load(mp3Path)
    note.volume(voice)
    note.play()
    sleep(4)
    note.stop()


# 根据提供的路径获取乐谱
def __MusicLoad(musicPath: Path) -> list:
    return json.load(open(musicPath))


# 对输入的乐谱从0(基本)拍开始往下计拍，返回含有(基本)拍数的乐谱
def __TimeStamp(music: list) -> list:
    beat = 0  # 从0开始计算拍数
    notesWithBeat = []
    musicScoreWithBeat = []
    for notes in music:
        notesWithBeat = notes.copy()
        notesWithBeat.append(int(beat))
        musicScoreWithBeat.append(notesWithBeat)
        beat += notes[1]*8
    return musicScoreWithBeat


# 返回一个装载乐谱的生成器,按顺序放出谱内的音符组
def __MusicGenerator(music: list) -> list:
    for notes in music:
        yield notes


# 同步函数，每过MUSIC_TIME_STAMP秒，往前推进一基本拍，并与乐谱进行一次关联。如果关联到音符组，则对此音符组执行__addThread调用。
def __DaemonSynchronizationThread(musicGeneratorA: Generator, musicGeneratorB: Generator, speed: int) -> None:
    MUSIC_MIN_TIME_STAMP = 60/speed/8  # 一基本拍的时间(基本拍：一个32分音符为一拍，区别于一般意义的拍)
    beat = 0
    notesA = next(musicGeneratorA)  # 获取A的音符组
    notesB = next(musicGeneratorB)  # 获取B的音符组
    errorcountA = errorcountB = False  # 用于记录谱子生成器终止的信号
    while True:
        try:
            if notesA[-1] == beat:
                __addThread(notesA)
                notesA = next(musicGeneratorA)  # 获取下一个音符组
        except StopIteration:
            errorcountA = True  # 捕获A谱子终止的信号
        try:
            if notesB[-1] == beat:
                __addThread(notesB)
                notesB = next(musicGeneratorB)  # 获取下一个音符组
        except StopIteration:
            errorcountB = True  # 捕获B谱子终止的信号
        finally:
            if errorcountA * errorcountB == True:  # 两个谱子都放完的情况下退出此函数
                break
            beat += 1
            sleep(MUSIC_MIN_TIME_STAMP)


# 针对传递过来的音符组，建立演奏线程，在线程中调用__voice处理
def __addThread(notes: list) -> None:
    for note in notes[0]:
        t = Thread(target=__voice, args=(note, notes[2]))
        t.start()


# 封装为控制台命令
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--music', help='主弦律所在路径')
    parser.add_argument('-c', '--chord', help='和弦所在路径')
    parser.add_argument('-s', '--speed', type=int, help='演奏速度')

    arge = parser.parse_args()

    # 读取文件
    music = __MusicLoad(Path(arge.music))
    chord = __MusicLoad(Path(arge.chord))
    speed = arge.speed

    # 转化为带有基本拍的乐谱
    musicWithBeat = __TimeStamp(music)
    chordWithBeat = __TimeStamp(chord)

    # 创造乐谱生成器
    musicGenerator = __MusicGenerator(musicWithBeat)
    chordGenerator = __MusicGenerator(chordWithBeat)

    # 预热接口
    warmUp = mp3play.load("./standard_pitch/4E.mp3")
    warmUp.volume(0)
    warmUp.play()
    sleep(0.1)
    warmUp.stop()

    # 播放音乐
    __DaemonSynchronizationThread(musicGenerator, chordGenerator, speed)

# python musicplay.py -m ./score/紫竹调A轨.json -c ./score/紫竹调B轨.json -s 96
# python musicplay.py -m ./score/canonCLeft.json -c ./score/canonCRight.json -s 80
