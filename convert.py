#!/usr/bin/env python3
import configparser
import sys
import os
import subprocess
import platform
import time
import argparse
import textwrap
from pymediainfo import MediaInfo

def getScriptPath():
    "Returns absolute path of script"
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def readConfig(var):
    configPath = 'convert.ini'
    config = configparser.ConfigParser()
    config.read(configPath)
    curPath = getScriptPath()
    if var == 'ffmpeg':
        if platform.system() == 'Windows':
            if config.has_option('Paths','FFmpeg Path') and \
                not config['Paths']['FFmpeg Path'] == '':
                configReturn = config['Paths']['FFmpeg Path']
                if not os.path.exists(configReturn):
                    print("ffmpeg.exe missing! Exiting script!")
                    time.sleep(5)
                    sys.exit()
            else:
                configReturn = os.path.join(curPath,'bin','ffmpeg.exe')
        else:
            configReturn = 'ffmpeg'
    elif var == 'inPath':
        if config.has_option('Paths','Input Path'):
            configReturn = config['Paths']['Input Path']
        else:
            configReturn = os.path.join(curPath,'in')
        os.makedirs(configReturn, exist_ok=True)
    elif var == 'outPath':
        if config.has_option('Paths','Output Path'):
            configReturn = config['Paths']['Output Path']
        else:
            configReturn = os.path.join(curPath,'out')
        os.makedirs(configReturn, exist_ok=True)
    elif var == 'fileTypes':
        if config.has_option('Misc','Accepted Filetypes') and \
            not config['Misc']['Accepted Filetypes'] == '':
            configReturn = (config['Misc']['Accepted Filetypes'].split())
        else:
            configReturn = ('.mp4','.mkv','.webm')
    return configReturn


class videoFile:
    "File to be manipulated by script"

    def __init__(self, fPath):
        mInfo = MediaInfo.parse(fPath)
        self.sInfo = {}
        self.sInfo['fileName'] = os.path.split(fPath)[1]
        self.sInfo['fullPath'] = '%s' % fPath
        self.sInfo['movieName']='%s' % mInfo.tracks[0].movie_name
        for track in mInfo.tracks:
            tType = track.track_type
            if tType == 'Video' or tType == 'Audio' or tType == 'Text':
                self.sInfo['%s_ID'       % track.track_id]='%s' % track.track_id
                self.sInfo['%s_title'    % track.track_id]='%s' % track.title
                self.sInfo['%s_format'   % track.track_id]='%s' % track.format
                self.sInfo['%s_language' % track.track_id]='%s' % track.language
                if tType == 'Video':
                    if not 'vTracks' in self.sInfo:
                        self.sInfo['vTracks'] = [track.track_id]
                    else:
                        self.sInfo['vTracks'].append(track.track_id)
                if tType == 'Audio':
                    if not 'aTracks' in self.sInfo:
                        self.sInfo['aTracks'] = [track.track_id]
                    else:
                        self.sInfo['aTracks'].append(track.track_id)
                if tType == 'Text':
                    if not 'tTracks' in self.sInfo:
                        self.sInfo['tTracks'] = [track.track_id]
                    else:
                        self.sInfo['tTracks'].append(track.track_id)

    def showVideoInfo(self):
        print("File Name:", self.sInfo['fileName'])
        print("Video Name:", self.sInfo['movieName'])
        print("--------------------------------------------------")
        print("Video Information:")
        self.showTrackInfo('vTracks')
        print("--------------------------------------------------")
        print("Audio Information")
        self.showTrackInfo('aTracks')
        print("--------------------------------------------------")
        print("Subtitle Information")
        self.showTrackInfo('tTracks')
        print("--------------------------------------------------")

    def showTrackInfo(self, current_track):
        for track in self.sInfo[current_track]:
            print("Stream ID:", self.sInfo['%s_ID'       % track])
            print("Title:"    , self.sInfo['%s_title'    % track])
            print("Format:"   , self.sInfo['%s_format'   % track])
            print("Language:" , self.sInfo['%s_language' % track])


    def selectTrack(vObj, current_track, track_type, multi_flag=True):
        if   track_type == 1:
             track_type = " Video"
        elif track_type == 2:
             track_type = "n Audio"
        else:
             track_type = " Subtitle"
        if type(vObj.sInfo[current_track]) == int:
            if multi_flag == False:
                loopNext = False
                loopExit = 2
            else:
                loopNext = 2
                loopExit = 3
            print("Select a%s track:" % track_type)
            print("1:", vObj.sInfo['%s_title'    % vObj.sInfo[current_track]],\
                        vObj.sInfo['%s_format'   % vObj.sInfo[current_track]],\
                        vObj.sInfo['%s_language' % vObj.sInfo[current_track]])
            if loopNext:
                print("%d: Skip file" % loopNext)
            print("%d: Return to main menu" % loopExit)
            x = input("Select an option[1-%d]: " % loopExit)
        else:
            if multi_flag == False:
                loopNext = False
                loopExit = len(vObj.sInfo[current_track]) + 1
            else:
                loopNext = len(vObj.sInfo[current_track]) + 1
                loopExit  = loopNext + 1
            print("Select a%s track" % track_type)
            for c, tracks in enumerate(vObj.sInfo[current_track]):
                print("%s:" % str(c+1), \
                    vObj.sInfo['%s_title'    % tracks],\
                    vObj.sInfo['%s_format'   % tracks],\
                    vObj.sInfo['%s_language' % tracks])
            if loopNext:
                print("%s: Skip file" % loopNext)
            print("%s: Return to main menu" % loopExit)
            x  = input("Select an option[1-%d]" % loopExit)
        print("--------------------------------------------------")
        if x.isdigit():
            x = int(x)
            if loopNext:
                if 0 < x < loopNext:
                    x = x-1
                    return x
                elif x == loopNext:
                    print("Skipping file...")
                    return -1
                elif x == loopExit:
                    input("Returning to main menu. Press enter to continue...")
                    return -2
                else:
                    print("Assuming first option...")
                    return 0
            else:
                if 0 < x < loopExit:
                    x = x-1
                    return x
                elif x == loopExit:
                    input("Returning to main menu. Press enter to continue...")
                    x = -1
                    return x
        else:
            print("Assuming first option...")
            return 0
def main():
    ans = True
    while ans:
        print(textwrap.dedent('''\
            Welcome to PyVideoHardsub!
            What would you like to do?
            1: Quick Hardsub (uses first video,audio,subtitle tracks)
            2: Advanced Hardsub (select which streams to encode)
            3: Video Information
            4: Quit'''))
        x = input("Select an option[1-4]: ")
        clearScreen()
        if x == '1':
            quickConvert(promptForPath())
            input('Process complete! Press enter to continue return to menu...')
            clearScreen()
        if x == '2':
            advConvert(promptForPath())
            input('Process complete! Press enter to continue return to menu...')
            clearScreen()
        if x == '3':
            videoInfo(promptForPath())
            input('Process complete! Press enter to continue return to menu...')
            clearScreen()
        if x == '4':
            ans = None
    sys.exit()

def promptForPath():
    x = input('Please specify the file or folder[empty for default path]:')
    #Remove " from path (copy as path in windows)
    if x.find('\"') >= 0:
        x = x.strip('\"')
    #If empty, set as default directory
    if x == '':
        x = readConfig('inPath')
    x = os.path.realpath(x)
    y = []
    #Determine if input is file or directory
    if os.path.isdir(x):
        for items in sorted(os.listdir(x)):
            #Only add valid video files to list
            if items.endswith(readConfig('fileTypes')):
                y.append(os.path.join(x,items))
    elif os.path.isfile(x) and x.endswith(readConfig('fileTypes')):
        y.append(x)
    #return nothing if no files found
    if len(y) == 0:
        print('No files to process found!')
        input()
        return
    return y

def quickConvert(promptPath):
    "Harsubs input with first video, audio, and subtitle tracks"
    clearScreen()
    if not promptPath:
        return
    for item in promptPath:
        convertVideo(item, os.path.basename(item), 0, 0, 0)

def advConvert(promptPath):
    "Hardsubs inputs w/ choice of specific video, audio, and subtitle tracks"
    clearScreen()
    if not promptPath:
        return
    convertQueue = []
    if len(promptPath) > 1:
        multi_flag = True
    else:
        multi_flag = False
    for item in promptPath:
        vObj = videoFile(item)
        fPath = vObj.sInfo['fullPath']
        fName = vObj.sInfo['fileName']
        print(fName)
        vTrack = vObj.selectTrack('vTracks',1, multi_flag)
        if vTrack == -1:
            continue
        elif vTrack == -2:
            del convertQueue
            break
        aTrack = vObj.selectTrack('aTracks',1, multi_flag)
        if aTrack == -1:
            continue
        elif aTrack == -2:
            del convertQueue
            break
        tTrack = vObj.selectTrack('tTracks',1, multi_flag)
        if tTrack == -1:
            continue
        elif tTrack == -2:
            del convertQueue
            break
        convertQueue.append((fPath, fName, vTrack, aTrack, tTrack))
    if 'convertQueue' in locals():
        for item in convertQueue:
            convertVideo(*item)

def argsConvert():
    "For converting items command line arguments"
    parser = argparse.ArgumentParser(prog='PyVideoHardsub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        PyVideoHardsub
        ------------------------------------------------

        This script will allow you to burn subtitles into a video
        quickly by choosing first video, audio, and subtitle tracks or
        in an advanced manner by letting you choose which tracks are
        mapped and subsequently burned into video.

        Run this script without arguments for an interactive menu.
        '''))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q','--quick',help='''
        Run quick conversion (First video, audio, and subtitle streams)
        ''', action='store_const', const='q', dest='conType')
    group.add_argument('-a','--advanced',help='''
        Run advanced conversion (Pick and choose video, audio, and
        subtitle streams)
        ''', action='store_const', const='a', dest='conType')
    group.add_argument('-i','--info',help='''
        Displays video, audio, and subtitle track information
        ''', action='store_const', const='i', dest='conType')
    parser.add_argument('-p', metavar='PATH', nargs='+', help='''
        Paths to files or directories to be processed. Subdirectories
        will NOT be processed. Assumes default path if none given.
        ''', dest='path', default=[readConfig('inPath')])
    args = parser.parse_args()

    convertQueue = []
    #Check if all arguments satisfied
    if args.conType:
        for paths in args.path:
            fullPath = os.path.realpath(paths)
            #Check if path is file or directory
            if os.path.isfile(fullPath):
                #check if file is valid video file
                if paths.endswith(readConfig('fileTypes')):
                    convertQueue.append(fullPath)
            if os.path.isdir(fullPath):
                #Run through files in directory
                for files in sorted(os.listdir(fullPath)):
                    #Check if file in directory is valid video file
                    if files.endswith(readConfig('fileTypes')):
                        convertQueue.append(os.path.join(fullPath,files))
        #Check if any valid paths were added to the queue
        if len(convertQueue) > 0:
            if   args.conType == 'q':
                quickConvert(convertQueue)
            elif args.conType == 'a':
                advConvert(convertQueue)
            elif args.conType == 'i':
                videoInfo(convertQueue)
        else:
            print('No valid items in queue')
            print('Exiting...')
            sys.exit()
    else:
        #Check if conversion or path arguments are missing
        if not args.conType:
            print('Missing conversion argument. See help for more info.',
                    '(run',getScriptPath(),'-h)')
            print('Exiting...')
            sys.exit(2)

def convertVideo(fPath, fName, vTrack, aTrack, tTrack):
    "Creates ffmpeg subprocess based on inputs from conversion methods"
    # ffmpeg -vf option escape chars are '\' and ':'
    # must escape escape chars in Windows environments
    subPath = "\'%s\'" \
        % fPath.replace("\\","\\\\").replace(":","\\:")
    subOpt = "subtitles=%s:si=%s" % (subPath, tTrack)
    vMap = "0:v:%s" % vTrack
    aMap = "0:a:%s" % aTrack
    outFile = os.path.join(readConfig('outPath'), fName[:-4]) + ".mp4"
    cmd = [readConfig('ffmpeg'), '-i', fPath, '-vf', subOpt, '-acodec', 'aac', \
        '-map', vMap, '-map', aMap, '-f', 'mp4', outFile]
    process = subprocess.Popen(cmd)
    process.wait()

def videoInfo(promptPath):
    "Show Info about all video, audio, and subtitle tracks"
    for item in promptPath:
        videoFile(item).showVideoInfo()

def clearScreen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        clearScreen()
        main()
    else:
        argsConvert()
