##### THIS README IS WRITTEN WITH LINUX ENVIRONMENTS IN MIND ONLY.

## Usage

These scripts can be used to create a cutfile with the mpv media player. 

Place `input.conf` into `~/.config/mpv/`.

Place `chopper.lua` into `~/.config/mpv/scripts`.

After that the key bindings defined in `input.conf` can be used to create timestamps into the cutfile.

The script will create the cutfile in the same directory as the video that is being cut.

## Known issues

When opening the video from a file manager (Thunar) and from a different drive than the OS is installed on, the cutfile gets created to the home directory instead of the directory where the video file is. Using the terminal to open the video file with mpv does not produce this issue.
