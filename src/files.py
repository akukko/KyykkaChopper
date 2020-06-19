from terminal_colors import *

import glob
import os

def get_lines(titlefile, ignore_comments=True):
    try:
        with open(titlefile, "r", encoding='utf-8') as f:
            lines = f.readlines()
        if ignore_comments:
            without_comments = []
            for line in lines:
                if not line.strip().startswith("#"):
                    without_comments.append(line)
            return without_comments
        return lines
    except:
        return []

def get_project_files(input_dir, titlefile, recursive):
    videofiles = []
    datafiles = []
    titles = []

    ignored_files = get_ignored_files(input_dir, recursive)

    if ignored_files:
        print(bold("Ignoring files matching with .chopignore file:"))
        for ign in ignored_files:
            print(ign)

        print("")

    for root, _, files in os.walk(input_dir):
        file_set = set(files)
        new_titles = []
        found_valid_videos = False
        for fname in files:
            if fname.lower().endswith("mp4"):
                cut_file = f"{fname.split('.')[0]}.txt"
                if cut_file in file_set and os.path.join(root, fname) not in ignored_files:
                    if new_titles:
                        titles.extend(new_titles)
                    videofiles.append(os.path.join(root, fname))
                    datafiles.append(os.path.join(root, cut_file))
                    found_valid_videos = True

            elif fname.lower() == titlefile:
                t = get_lines(os.path.join(root, titlefile))
                if found_valid_videos:
                    titles.extend(t)
                else:
                    new_titles.extend(t)

        if not recursive:
            break

    return videofiles, datafiles, titles

def get_ignored_files(input_dir, recursive):
    ignored_files = set()

    globs = get_lines(os.path.join(input_dir, ".chopignore"))
    for g in globs:
        stripped = g.strip()

        def add_ignore(match):
            ignored = os.path.join(input_dir, match)
            if os.path.isdir(ignored):
                if recursive:
                    for f in os.listdir(ignored):
                        add_ignore(os.path.join(ignored, f))
            elif os.path.isfile(ignored):
                ignored_files.add(ignored)
        
        for match in glob.glob(stripped, recursive=True):
            add_ignore(match)
    return ignored_files