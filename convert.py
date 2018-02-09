#!/usr/bin/env python3
import configparser
import sys
import os
import subprocess
import platform
import time
from pymediainfo import MediaInfo

#Accepted filetypes
fileTypes = ('.mp4', '.mkv', '.webm')

def getScriptPath():
    "Returns absolute path of script"
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def startup():
    # Check if configfile exists
    configPath = os.path.join(getScriptPath(),'convert.ini')
    if not os.path.isfile(configPath):
        config = configparser.ConfigParser(allow_no_value=True)
        curPath = getScriptPath()
        if platform.system() == 'Windows':
            config['DEFAULT'] = {
                'ffmpeg path': os.path.join(curPath,'bin','ffmpeg.exe'),
                'Input path':  os.path.join(curPath,'in'),
                'Output path': os.path.join(curPath,'out')
            }
            config.add_section('Paths')
            configPathComments = (
                '# This is where you configure paths',
                '# Make sure to use full paths',
                '# For example, to set input path',
                r'# Input path: C:\Path\To\input\folder'
            )
            for comment in configPathComments:
                config.set('Paths', comment)
        else:
            config['DEFAULT'] = {
                'Input path': os.path.join(curPath, 'in'),
                'Output path': os.path.join(curPath, 'out')
            }
            config.add_section('Paths')
            configPathComments = (
                '# This is where you configure paths',
                '# Make sure to use full paths',
                '# For example, to set input path',
                '# Input path: /path/to/input/folder'
            )
            for comment in configPathComments:
                config.set('Paths', comment)
        with open(configPath, 'w') as configfile:
            config.write(configfile)
    # Read config file and add info to global variables
    global ffmpeg, inPath, outPath
    config = configparser.ConfigParser()
    config.read(configPath)
    if platform.system() == 'Windows':
        ffmpeg =  config['Paths']['ffmpeg path']
    else:
        ffmpeg = 'ffmpeg'
    inPath =  config['Paths']['Input path']
    outPath = config['Paths']['Output path']
    # Check if paths exists
    if platform.system() == 'Windows':
        if not os.path.exists(ffmpeg):
            print("ffmpeg.exe missing! Exiting script!")
            time.sleep(5)
            sys.exit()
    for path in (inPath, outPath):
        os.makedirs(path, exist_ok=True)


class videoFile:
    "File to be manipulated by script"

    def __init__(self, fPath):
        mInfo = MediaInfo.parse(fPath)
        self.sInfo = {}
        if platform.system() == 'Windows':
            self.sInfo['fileName'] = fPath.split('\\')[-1]
        else:
            self.sInfo['fileName'] = fPath.split('/')[-1]
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
                        self.sInfo['vTracks'] = track.track_id
                    else:
                        self.sInfo['vTracks'] = \
                            [self.sInfo.pop('vTracks'), track.track_id]
                if tType == 'Audio':
                    if not 'aTracks' in self.sInfo:
                        self.sInfo['aTracks'] = track.track_id
                    else:
                        self.sInfo['aTracks'] = \
                            [self.sInfo.pop('aTracks'), track.track_id]
                if tType == 'Text':
                    if not 'tTracks' in self.sInfo:
                        self.sInfo['tTracks'] = track.track_id
                    else:
                        self.sInfo['tTracks'] = \
                            [self.sInfo.pop('tTracks'), track.track_id]

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
        if type(self.sInfo[current_track]) == int:
            print("Stream ID:", self.sInfo['%s_ID'      % \
                self.sInfo[current_track]])
            print("Title:"    , self.sInfo['%s_title'   % \
                self.sInfo[current_track]])
            print("Format:"   , self.sInfo['%s_format'  % \
                self.sInfo[current_track]])
            print("Language:" , self.sInfo['%s_language'% \
                self.sInfo[current_track]])
        else:
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
                    x = -1
                    return x
                else:
                    print("Assuming first option...")
                    x = -2
                    return x
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

def promptForPath():
    x = input('Please specify the file or folder[empty for default path]:')
    if x.find('\"') >= 0:
        x = x.strip('\"')
    if x == '':
        x = inPath
    return x

def quickConvert(promptPath):
    "Harsubs input with first video, audio, and subtitle tracks"
    clearScreen()
    if os.path.isdir(promptPath):
        os.chdir(promptPath)
        for item in os.listdir(os.getcwd()):
            if os.path.isfile(os.path.join(os.getcwd(),item)) \
                and item.endswith(fileTypes):
                 vObj = videoFile(os.path.join(os.getcwd(), item))
                 fPath = vObj.sInfo['fullPath']
                 fName = vObj.sInfo['fileName']
                 convertVideo(fPath, fName, 0,0,0)
    elif os.path.isfile(promptPath):
        convertVideo(promptPath, os.path.basename(promptPath), 0,0,0)
    else:
        print("Unable to find files to process!")
    input("Process complete! Press enter to return to main menu.")

def advConvert(promptPath):
    "Hardsubs inputs w/ choice of specific video, audio, and subtitle tracks"
    if os.path.isdir(promptPath):
        os.chdir(promptPath)
        batchHardsub = []
        for item in os.listdir(os.getcwd()):
            if os.path.isfile(os.path.join(os.getcwd(), item)) \
                and item.endswith(('.mkv','.mp4')):
                vObj = videoFile(os.path.join(os.getcwd(), item))
                fPath = vObj.sInfo['fullPath']
                fName = vObj.sInfo['fileName']
                print(fName)
                vTrack = vObj.selectTrack('vTracks', 1)
                if vTrack == -1:
                    continue
                elif vTrack == -2:
                    del batchHardsub
                    break
                aTrack = vObj.selectTrack('aTracks', 2)
                if aTrack == -1:
                    continue
                elif aTrack == -2:
                    del batchHardsub
                    break
                tTrack = vObj.selectTrack('tTracks', 3)
                if tTrack == -1:
                    continue
                elif tTrack == -2:
                    del batchHardsub
                    break
                batchHardsub.append((fPath, fName, vTrack, aTrack, tTrack))
        if 'batchHardsub' in locals() and batchHardsub != []:
            for convert in batchHardsub:
                convertVideo(*convert)
            print("All videos converted")
            input("Press enter to return to main menu...")
        elif 'batchHardsub' in locals() and batchHardsub == []:
            print("No videos converted")
            input("Press enter to return to main menu...")
    if os.path.isfile(promptPath):
        vObj = videoFile(promptPath)
        fPath = vObj.sInfo['fullPath']
        fName = vObj.sInfo['fileName']
        print(fName)
        vTrack = vObj.selectTrack('vTracks', 1, False)
        if vTrack < 0:
            return
        aTrack = vObj.selectTrack('aTracks', 2, False)
        if aTrack < 0:
            return
        tTrack = vObj.selectTrack('tTracks', 3, False)
        if tTrack < 0:
            return
        convertVideo(fPath, fName, vTrack, aTrack, tTrack)
        input("Video converted. Press enter to return to menu...")
    clearScreen()

def argsConvert(args):
    "For converting items command line arguments"
    pass

def convertVideo(fPath, fName, vTrack, aTrack, tTrack):
    "Creates ffmpeg subprocess based on inputs from conversion methods"
    # ffmpeg -vf option escape chars are '\' and ':'
    # must escape escape chars in Windows environments
    subPath = "\'%s\'" \
        % fPath.replace("\\","\\\\").replace(":","\\:")
    subOpt = "subtitles=%s:si=%s" % (subPath, tTrack)
    vMap = "0:v:%s" % vTrack
    aMap = "0:a:%s" % aTrack
    outFile = os.path.join(outPath, fName[:-4]) + ".mp4"
    cmd = [ffmpeg, '-i', fPath, '-vf', subOpt, '-acodec', 'aac', \
        '-map', vMap, '-map', aMap, '-f', 'mp4', outFile]
    process = subprocess.Popen(cmd)
    process.wait()

def videoInfo(promptPath):
    "Show Info about all video, audio, and subtitle tracks"
    if os.path.isdir(promptPath) or promptPath == '':
        if promptPath == '':
            os.chdir(inPath)
        else:
            os.chdir(promptPath)
        for item in os.listdir(os.getcwd()):
            if os.path.isfile(os.path.join(os.getcwd(),item)) \
                and item.endswith(fileTypes):
                videoFile(os.path.join(os.getcwd(), item)).showVideoInfo()
    elif os.path.isfile(promptPath):
        videoFile(promptPath).showVideoInfo()
    else:
        "Unable to find file or path!"
    input("Press enter to continue.......")
    clearScreen()

def clearScreen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    clearScreen()
    startup()
    if len(sys.argv) == 1:
        ans = True
        while ans:
            print("Welcome to PyVideoHardsub!")
            print("What would you like to do?")
            print("1: Quick Hardsub (uses first video,audio,subtitle tracks)")
            print("2: Advanced Hardsub (select which streams to encode)")
            print("3: Video Information")
            print("4: Quit")
            x = input("Select an option[1-4]: ")
            clearScreen()
            if x == '1':
                quickConvert(promptForPath())
            if x == '2':
                advConvert(promptForPath())
            if x == '3':
                videoInfo(promptForPath())
            if x == '4':
                ans = None
        sys.exit()
    else:
        argsConvert(sys.argv[1:])
