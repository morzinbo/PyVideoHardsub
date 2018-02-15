This script will allow you to burn subtitles into a video
quickly by choosing first video, audio, and subtitle tracks or
in an advanced manner by letting you choose which tracks are
mapped and subsequently burned into video.

## Requirements

* python3+
* ffmpeg
  * Ubuntu 16.04:
    * sudo apt-add-repository ppa:jonathonf:/ffmpeg-3
    * sudo apt-get update
    * sudo apt-get install ffmpeg libav-tools x264 x265
  * Windows:
    * download latest ffmpeg build from: https://ffmpeg.zeranoe.com/builds/
    * extract ffmpeg.exe to 'bin' folder in script directory
* pymediainfo
  * Ubuntu 16.04:
    * pip3 install git+git://github.com/sbraz/pymediainfo
  * Windows:
    * From <python_install_location>/Scripts' pip3.exe install pymediainfo

## Usage

    usage: convert.py [-h] [-q | -a | -i] [-p PATH [PATH ...]]

    Run this script without arguments for an interactive menu.

    optional arguments:
      -h, --help          show this help message and exit
      -q, --quick         Run quick conversion (First video, audio, and subtitle
                          streams)
      -a, --advanced      Run advanced conversion (Pick and choose video, audio,
                          and subtitle streams)
      -i, --info          Displays video, audio, and subtitle track information
      -p PATH [PATH ...]  Paths to files or directories to be processed.
                          Subdirectories will NOT be processed. Assumes default
                          path if none given.
                          
#### Interactive Menu

For quick hardsubbing, place video files inside
input path (default: path/to/script/in) and choose option 1
with no path to convert everything inside of the input path with
first video, audio, and subtitle stream.

For track selection, choose option 2 and follow prompts.
