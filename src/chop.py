from config import *
from terminal_colors import *
from files import *

import argparse
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ImageClip
from math import tanh
import numpy as np
import cv2

text_i = 0

def parse_cuts(vid, filename, texts, conf):
    global text_i
    """Parse file with the following format:
    >clip start (in seconds)
    <clip end (in seconds)
    """
    cuts = []

    with open(filename, "r") as f:
        lines = [l for l in (line.strip() for line in f) if l]

        start = None
        end = None
        title = None
        clip = None
        title_start = None

        for line in lines:
            if line.startswith(">"):
                start = float(line[1:].strip())
                if title_start:
                    # title at the very beginning
                    # clip, text_i = build_title(vid, title_start, start, texts, text_i, conf)
                    clip, text_i = build_start_title(vid, start, texts, text_i)
                    cuts.append(clip)
                    title_start = None
                end = None
                title = None
            elif line.startswith("<"):

                if line.startswith("<vol"):
                    end = float(line[4:].strip())
                    clip = vid.subclip(start, end).volumex(conf.volfactor)
                else:
                    end = float(line[1:].strip())
                    clip = vid.subclip(start, end)


                cuts.append(clip)
                title = None
            elif line.startswith("*"):
                if title:
                    # title is after another title
                    title_start = title
                elif start and not end:
                    # title is after a clip start (>)
                    title_start = start
                elif end:
                    # title is after a clip end (<)
                    title_start = end
                else:
                    # title is at the very beginning
                    title_start = float(line[1:].strip())
                    continue

                title = float(line[1:].strip())

                clip, text_i = build_title(vid, title_start, title, texts, text_i, conf)
                cuts.append(clip)

                title_start = None
    return cuts


def build_title(vid, title_start, title_end, texts, text_i, conf):
    t = texts[text_i]
    t = t.replace('\\n', '\n')

    clip = vid.subclip(title_start, title_end)

    text = TextClip(f"{t}", fontsize=conf.titlesize, font=conf.titlefont, color=conf.titlecolor).set_pos(("center", "bottom"))

    comp_clip = CompositeVideoClip([clip, text])
    comp_clip.duration = clip.duration

    return comp_clip, text_i + 1


def process_with_moviepy(filenames, datafiles, outfile, titles, conf):
    clips = []
    for video_file, data_file in zip(filenames, datafiles):
        input_vid = VideoFileClip(video_file)
        cuts = parse_cuts(input_vid, data_file, titles, conf)

        for cut in cuts:
            clips.append(cut)

    if clips:
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(outfile)
    else:
        print(warn("\nNo clips to process. Exiting."))

def build_start_title(vid, title_end, texts, text_i):

    dirname = os.path.dirname(__file__) # Relative path to the folder
    # Images
    maila = "Karttu.png"
    logo = "logo.png"
    # Fonts
    font = "Ebrima-Bold"
    # font = "Fixedsys Regular"
    fontsize = 150
    color = "#e94b3cff"
    stroke_color = "#1d1b1b"

    if float(title_end) - 4.0 > 0.0:
        clip = vid.subclip(float(title_end) - 4.0, title_end)
    else: # if start is shorter than 4 s
        rate = title_end / 4
        clip = vid.subclip(0, title_end).speedx(rate)
    t = texts[text_i]
    t = t.replace('\\n', '\n')
    t = t.split(";")    # separate event and players
    if len(t) == 2:
        players = t[0]
        event = t[1]
    else:
        event = t[0]
        players = ""

    maila_img = ImageClip(os.path.join(dirname ,maila), duration = 4)\
                .resize(height = int(clip.size[1] * 0.7))
    logo_img = ImageClip(os.path.join(dirname ,logo), duration = 4)\
                .resize(width = maila_img.size[0] + 100)\
                .set_position(("center", "top"))
    maila_img = maila_img.margin(top = logo_img.size[1],\
                                 left = int((logo_img.size[0] - maila_img.size[0]) / 2),\
                                 right = int((logo_img.size[0] - maila_img.size[0]) / 2),\
                                 opacity = 0)
    images = CompositeVideoClip([maila_img,logo_img])
    images_rot = images.set_position("center")\
                .resize(lambda t: min(0.2 + t*1.5 , 1))\
                .rotate(lambda t: 500 * (tanh(t*4 + 0.5) * -5 + 5), resample = "nearest")
    event_txt = TextClip(event,
                         stroke_color = stroke_color,\
                         stroke_width = 4, color=color,\
                         font= font,\
                         kerning = 5,\
                         fontsize=fontsize)\
                .set_duration(4)
    event_txt = event_txt.resize(width = clip.size[0] / 2 - 300)
    event_txt = event_txt.set_pos(lambda t:(min(clip.size[0]/2 + 100,-800 + t * 1500),clip.size[1]/2))
    player_txt = TextClip(players,\
                          stroke_color = stroke_color,\
                          stroke_width = 4, color=color,\
                          font=font,\
                          kerning = 5,\
                          fontsize=fontsize)\
                .set_duration(4)
    player_txt = player_txt.set_pos(lambda t:(max(clip.size[0]/2 - player_txt.size[0]- 100, clip.size[0] + 600 + t * -1800),clip.size[1]/2 - player_txt.size[1]/2))
    mask_left = np.zeros((clip.size[1],clip.size[0], 4))
    mask_right = B = np.copy(mask_left)
    mask_left = cv2.rectangle(mask_left, (0, 0), (int(clip.size[0]/2), clip.size[1]), (255,255,255,255), -1)
    mask_right = cv2.rectangle(mask_right, (int(clip.size[0]/2), 0), (clip.size[0], clip.size[1]),  (255,255,255,255), -1)
    mask_left = ImageClip(mask_left, duration=2, ismask=True)
    mask_right = ImageClip(mask_right, duration=2, ismask=True)
    # cv2.imwrite("kala.png",mask_right)
    comp_clip = CompositeVideoClip([clip, event_txt, clip.set_mask(mask_left)])
    comp_clip = CompositeVideoClip([comp_clip, player_txt, comp_clip.set_mask(mask_right), images_rot])
    return comp_clip, text_i + 1


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--input", type=str, metavar="INPUT_DIR", help="Input directory that contains the cut-to-be files", required=False)
    args.add_argument("-r", "--recursive", action="store_true", help="Whether to look for input files recursively", required=False)
    args.add_argument("-o", "--output", type=str, metavar="OUTPUT_NAME", default="out.mp4", help="Desired name for the output file", required=False)
    args.add_argument("-t", "--titles", type=str, metavar="TITLE_FILE", default="titles.txt", help="Name of the file containing titles for the video", required=False)
    conf_help = "Name of the configuration file. If not given and no file named \"chop.conf\" exists in the current directory, default values will be used"
    args.add_argument("-c", "--config", type=str, metavar="CONFIG_FILE", default="chop.conf", help=conf_help, required=False)
    args.add_argument("-g", "--gen-config", action="store_true", help="Generate configuration file with default values and exit", required=False)
    args.add_argument("-d", "--dry-run", action="store_true", help="Only scan and display the files to be cut but don't start chopping them")
    args = args.parse_args()

    if args.gen_config:
        make_default_config(args.config)
        exit()

    conf = read_config(args.config)

    input_dir = args.input
    if not args.input:
        # If no input dir is given, use the working directory (where this script is ran)
        input_dir = os.getcwd()

    videofiles, datafiles, titles = get_project_files(input_dir, args.titles, args.recursive)

    print(bold("Chopping following files:"))
    for v in videofiles:
        print(v)

    print(bold("\nUsing following titles:"))
    for t in titles:
        print(t.strip())

    if args.dry_run:
        print(bold(warn("\nStopping execution because of the dry-run argument")))
        exit()

    print(bold("\nStarting the chopping process:"))

    process_with_moviepy(videofiles, datafiles, args.output, titles, conf)
