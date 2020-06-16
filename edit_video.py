import vlc
import keyboard
import argparse
import os

set_timestamp_start = 'x'
set_timestamp_end = 'c'
set_text = 't'
pause_player = 'space'
go_forward = 'right'
go_backward = 'left'
time_step = 5000 #ms

def get_time_frame_start(player, timestamps, turn):
    if turn[0]:
        time = player.get_time()/1000
        timestamps.append(">" + str(time))
        turn[0] = False

def get_time_frame_end(player, timestamps, turn):
    if not turn[0]:
        time = player.get_time()/1000
        timestamps.append("<" + str(time))
        turn[0] = True

def get_text_time(player, timestamps, texts):
    time = player.get_time()/1000
    timestamps.append("*" + str(time))
    player.pause()
    cls()
    text = input("Syötä teksti. Jos kyseessä on alkuteksti, erota tapahtuma ja pelaaja teksti ; merkillä : ")
    texts.append(text)
    player.play()

def pause(player):
    player.pause()

def move_forward(player, time_step):
    if (player.get_time() + time_step) <= player.get_length():
        player.set_time(player.get_time() + time_step)

def move_backward(player, time_step):
    if (player.get_time() - time_step) >= 0:
        player.set_time(player.get_time() - time_step)

def edit_video(file):
    turn = [True]
    timestamps = []
    texts = []
    player = vlc.MediaPlayer(file)
    player.play()
    keyboard.add_hotkey(set_timestamp_start, get_time_frame_start, args=[player, timestamps, turn])
    keyboard.add_hotkey(set_timestamp_end, get_time_frame_end, args=[player, timestamps, turn])
    keyboard.add_hotkey(set_text, get_text_time, args=[player, timestamps, texts])
    keyboard.add_hotkey(pause_player, pause, args=[player])
    keyboard.add_hotkey(go_forward, move_forward, args=[player, time_step])
    keyboard.add_hotkey(go_backward, move_backward, args=[player, time_step])
    # keyboard.add_hotkey('esc', cut_video, args=[timestamps, file])
    print("Lopettaaksesi paina ESC.")
    keyboard.wait('esc')
    write_file(timestamps, file.split(".")[0])
    write_file(texts, file.split("\\")[0] + "\\titles")

def write_file(timestamps, file):
    with open(file + ".txt", "w") as f:
        for line in timestamps:
            f.write("%s\n" % line)

def cls():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--input", type=str)

    args = args.parse_args()

    input_dir = args.input
    files = os.listdir(input_dir)
    videofiles = []
    print("Mitä tiedostoa haluat editoita?")
    for fname in files:
        if fname.lower().endswith("mp4"):
            if not input_dir:
                videofiles.append(os.path.join(fname))
            else:
                videofiles.append(os.path.join(input_dir, fname))
            print(str(len(videofiles)) + "." + fname)
    if len(videofiles) == 0:
        print("yhtään tiedostoa ei ole")
    else:
        edit_video(videofiles[int(input("=")) - 1])
