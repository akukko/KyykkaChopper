import vlc
import keyboard
import argparse
import os

set_timestamp_start = 'x'
set_timestamp_end = 'c'
remove_last_input_timestamp = 'z'
set_text = 't'
pause_player = 'space'
go_forward = 'right'
go_backward = 'left'
time_step = 5000 #ms
input_dir = ""
turn = [True]
timestamps = []
texts = []

def get_time_frame_start(player, timestamps, turn):
    if turn[0]:
        time = player.get_time()/1000
        timestamps.append(">" + str(time))
        turn[0] = False
        print("Alku")


def get_time_frame_end(player, timestamps, turn):
    if not turn[0]:
        time = player.get_time()/1000
        timestamps.append("<" + str(time))
        turn[0] = True
        print("Loppu")

def get_text_time(player, timestamps, texts):
    time = player.get_time()/1000
    timestamps.append("*" + str(time))
    if str(player.get_state()) == "State.Playing":
        player.pause()
    clear_input()
    text = input("Syötä teksti. Jos kyseessä on alkuteksti, erota tapahtuma ja pelaaja teksti ; merkillä : ")
    texts.append(text)
    player.play()

def remove_last_from_list(timestamps, turn):
    del timestamps[-1]
    turn[0] = not turn[0]
    print("Edellinen poistettu")

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
    del timestamps[:]
    del texts[:]
    # player = vlc.MediaPlayer(file)
    vlc_file = vlc.Instance().media_new(file)
    player.set_media(vlc_file)
    player.play()
    print("Lopettaaksesi paina ESC.")
    keyboard.wait('esc')
    if len(timestamps) > 1:
        write_file(timestamps, file.split(".")[0])
    if len(texts) > 0:
        write_file(texts, file.split(".")[0] + "_titles")
    player.stop()
    clear_input()
    get_video_files()

def write_file(timestamps, file):
    with open(file + ".txt", "w") as f:
        for line in timestamps:
            f.write("%s\n" % line)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def clear_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def get_video_files():
        cls()
        files = os.listdir(input_dir)
        videofiles = []
        print("Mitä tiedostoa haluat editoita? (Exit valitse 0)")
        for fname in files:
            if fname.lower().endswith(("mp4", "avi", "mts")):
                text_file = ""
                if not input_dir:
                    videofiles.append(os.path.join(fname))
                    if os.path.isfile(os.path.join(fname.split(".")[0] + ".txt")):
                        text_file = "Leikkaustiedosto löytyy jo"
                else:
                    videofiles.append(os.path.join(input_dir, fname))
                    if os.path.isfile(os.path.join(input_dir, fname.split(".")[0] + ".txt")):
                        text_file = "Leikkaustiedosto löytyy jo"
                print(str(len(videofiles)) + "." + fname, text_file)
        if len(videofiles) == 0:
            print("yhtään tiedostoa ei ole")
        else:
            option = int(input(":")) - 1
            if option != -1:
                edit_video(videofiles[option])
            else:
                return 0

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--input", type=str)
    args = args.parse_args()
    input_dir = args.input
    player = vlc.Instance().media_player_new()
    keyboard.add_hotkey(set_timestamp_start, get_time_frame_start, args=[player, timestamps, turn])
    keyboard.add_hotkey(set_timestamp_end, get_time_frame_end, args=[player, timestamps, turn])
    keyboard.add_hotkey(set_text, get_text_time, args=[player, timestamps, texts])
    keyboard.add_hotkey(pause_player, pause, args=[player])
    keyboard.add_hotkey(go_forward, move_forward, args=[player, time_step])
    keyboard.add_hotkey(go_backward, move_backward, args=[player, time_step])
    keyboard.add_hotkey(remove_last_input_timestamp, remove_last_from_list, args=[timestamps, turn])
    get_video_files()
