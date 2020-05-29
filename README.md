# KyykkaChopper

Automatic video editor for quickly editing Kyykkä videos.


## Basic usage

``` python process.py --input <path-to-folder> --output <output-file> --titles <title-file>```

The input folder should contain one or more mp4 videos, and cut files corresponding to the video filename. The cut file contains the timestamps of the desired cuts that chopper should make.

An example folder could contain files:
* vid1.mp4
* vid2.mp4
* vid1.txt
* vid2.txt

Cut file (the text files) format is the following:

```
> clip start (in seconds)
< clip end (in seconds)
```

## Titles

Cut file format with titles is the following:
```
* title1 start
> clip start / title1 end / title2 start
* title2 end
< clip end / title3 start
* title3 end / title4 start
* title4 end
```

For example, to make one title from 1.5 s to 2 s, a second one from 3 s to 5 s and a third and final one from 5 s to 7.5 s:
```
* 1.5
> 2
< 3
* 5
* 7.5
```

The title functionality assumes that a file matching with the --titles argument (or if no --titles argument is given, default of "titles.txt") is within the input directory. The titles file needs to have the same amount of lines as there are titles in the cut file. The text within each line of the titles file is then displayed at the bottom center of the video for the duration determined in the cut file.

## Automatic timestamps from VLC

To automatically get timestamps from VLC player, use VLC version 2.0.x and place the elapsed_time_to_file.lua script to the extension folder. Enable the extension and after this, press 'x' to start a clip, and 'c' to stop it.

Original script: https://addons.videolan.org/p/1154002/

## Known issues
* Automatic timestamp file generation doesn't work between hard drives: the video needs to be in the same drive as VLC player.
* When merging multiple videos, the order of the videos is only determined by the output of `os.listdir`

