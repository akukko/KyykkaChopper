import argparse
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

text_i = 0

def parse_cuts(vid, filename, texts):
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
                    clip, text_i = build_title(vid, title_start, start, texts, text_i)

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
                
                clip, text_i = build_title(vid, title_start, title, texts, text_i)
                cuts.append(clip)

                title_start = None
    return cuts
            

def build_title(vid, title_start, title_end, texts, text_i):
    t = texts[text_i]
    t = t.replace('\\n', '\n')
    
    clip = vid.subclip(title_start, title_end)

    text = TextClip(f"{t}", fontsize=145, font="Roboto Mono", color="white").set_pos(("center", "bottom"))
    
    comp_clip = CompositeVideoClip([clip, text])
    comp_clip.duration = clip.duration

    return comp_clip, text_i + 1


def process_with_moviepy(filenames, datafiles, outfile, scores):
    clips = []
    for video_file, data_file in zip(filenames, datafiles):
        input_vid = VideoFileClip(video_file)
        cuts = parse_cuts(input_vid, data_file, scores)

        for cut in cuts:
            clips.append(cut)

    final_clip = concatenate_videoclips(clips)

    final_clip.write_videofile(outfile)

def get_scores(scorefile):
    with open(scorefile, "r", encoding='utf-8') as f:
        lines = [l for l in (line.strip() for line in f) if l] 
    print(lines)
    return lines

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--input", type=str)
    args.add_argument("--output", type=str, default="out.mp4")
    args.add_argument("--titles", type=str, default="titles.txt")

    args = args.parse_args()

    input_dir = args.input
    files = os.listdir(input_dir)

    videofiles = []
    datafiles = []
    titles = []

    for fname in files:
        if fname.lower().endswith("mp4"):
            videofiles.append(os.path.join(input_dir, fname))
            datafiles.append(os.path.join(input_dir, f"{fname.split('.')[0]}.txt"))
        elif fname.lower() == args.titles:
            titles = get_scores(os.path.join(input_dir, args.titles))

    process_with_moviepy(videofiles, datafiles, args.output, titles)
