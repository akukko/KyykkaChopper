from config import *
from terminal_colors import *
from helpers import get_lines

import argparse
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

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
                    clip, text_i = build_title(vid, title_start, start, texts, text_i, conf)

                    cuts.append(clip)
                    title_start = None
                end = None
                title = None
            elif line.startswith("<"):
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

    final_clip = concatenate_videoclips(clips)

    final_clip.write_videofile(outfile)

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
        input_dir = os.getcwd()


    videofiles = []
    datafiles = []
    titles = []
    for root, subdirs, files in os.walk(input_dir):
        file_set = set(files)
        for fname in files:
            if fname.lower().endswith("mp4"):
                cut_file = f"{fname.split('.')[0]}.txt"
                if cut_file in file_set:
                    videofiles.append(os.path.join(root, fname))
                    datafiles.append(os.path.join(root, cut_file))
            elif fname.lower() == args.titles:
                titles.extend(get_lines(os.path.join(root, args.titles)))
        if not args.recursive:
            break
    
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
