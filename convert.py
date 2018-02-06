#!/usr/bin/env python3
# TODO: Make script work with command line arguments
# TODO: Make GUI
# TODO: editable config
# TODO: make cross platform
import configparser
import sys
import os
import subprocess
import platform
import time
from pymediainfo import MediaInfo

#NOTES

#Accepted filetypes
fileTypes = ('.mp4', '.mkv', '.webm')

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def startup():
    # Check if configfile exists
    configPath = os.path.join(getScriptPath(),'convert.ini')
    if not os.path.isfile(configPath):
        config = configparser.ConfigParser()
        curPath = getScriptPath()
        if platform.system() == 'Windows':
            config['paths'] = {
                'ffmpeg path':         os.path.join(curPath,'bin','ffmpeg.exe'),
                'default input path':  os.path.join(curPath,'in'),
                'default output path': os.path.join(curPath,'out')
            }
        else:
            config['paths'] = {
                'default input path': os.path.join(curPath, 'in'),
                'default output path': os.path.join(curPath, 'out')
            }
        with open(configPath, 'w') as configfile:
            config.write(configfile)
    # Read config file and add info to global variables
    global ffmpeg, inPath, outPath
    config = configparser.ConfigParser()
    config.read(configPath)
    if platform.system() == 'Windows':
        ffmpeg =  config['paths']['ffmpeg path']
    else:
        ffmpeg = 'ffmpeg'
    inPath =  config['paths']['default input path']
    outPath = config['paths']['default output path']
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
            print("Title:",     self.sInfo['%s_title'   % \
                self.sInfo[current_track]])
            print("Format:",    self.sInfo['%s_format'  % \
                self.sInfo[current_track]])
            print("Language:",  self.sInfo['%s_language'% \
                self.sInfo[current_track]])
        else:
            for track in self.sInfo[current_track]:
                print("Stream ID:", self.sInfo['%s_ID'       % track])
                print("Title:",     self.sInfo['%s_title'    % track])
                print("Format:",    self.sInfo['%s_format'   % track])
                print("Language:",  self.sInfo['%s_language' % track])


    def selectTrack(vObj, current_track, track_type):
        if   track_type == 1:
            track_type = " Video"
        elif track_type == 2:
            track_type = "n Audio"
        else:
            track_type = " Subtitle"
        if type(vObj.sInfo[current_track]) == int:
            loopNext = 2
            loopExit = 3
            print("Select a%s track:" % track_type)
            print("1:", vObj.sInfo['%s_title'    % vObj.sInfo[current_track]],\
                        vObj.sInfo['%s_format'   % vObj.sInfo[current_track]],\
                        vObj.sInfo['%s_language' % vObj.sInfo[current_track]])
            print("2: Skip file")
            print("3: Return to main menu")
            x = input("Select an option[1-3]: ")
        else:
            loopNext = len(vObj.sInfo[current_track]) + 1
            loopExit  = len(vObj.sInfo[current_track]) + 2
            print("Select a%s track" % track_type)
            for c, tracks in enumerate(vObj.sInfo[current_track]):
                print("%s:" % str(c+1), \
                    vObj.sInfo['%s_title'    % tracks],\
                    vObj.sInfo['%s_format'   % tracks],\
                    vObj.sInfo['%s_language' % tracks])
            print("%s: Skip file" % loopNext)
            print("%s: Return to main menu" % loopExit)
            x  = input("Select an option[1-%d]" % loopExit)
        print("--------------------------------------------------")
        if x.isdigit():
            x = int(x)
            if 0 < x < loopNext:
                x = x-1
                return x
            elif x == loopNext:
                print("Skipping file...")
                return "continue"
            elif x == loopExit:
                input("Returning to main menu. Press enter to continue...")
                return "break"
            else:
                print("Assuming first option...")
                return 0
        else:
            print("Assuming first option...")
            return 0



def convertMenu():
    "Looping menu for selecting working with files and folders directly"
    ans = True
    while ans:
        clearScreen()
        print("Welcome to Video Hardsub Reborn!")
        print("What would you like to do?")
        print("1: Quick Hardsub (uses first video,audio,subtitle tracks)")
        print("2: Advanced Hardsub (select which streams to encode)")
        print("3: Video Information")
        print("4: Test stuff")
        print("5: Quit")
        x = input("Select an option[1-5]: ")
        if x == '1':
            quickConvert()
        if x == '2':
            advConvert()
        if x == '3':
            videoInfo()
        if x == '4':
            testStuff2()
        if x == '5':
            ans = None

def quickConvert():
    "Harsubs input with first video, audio, and subtitle tracks"
    clearScreen()
    promptPath = input(
            "Please specify a file or folder[leave empty for default path]: ")
    if promptPath.find("\"") >= 0:
        promptPath = promptPath.strip("\"")
    if os.path.isdir(promptPath) or promptPath == '':
        if promptPath == '':
            os.chdir(inPath)
        else:
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

def advConvert():
    "Hardsubs inputs w/ choice of specific video, audio, and subtitle tracks"
    clearScreen()
    batchConvert = []
    promptPath = input(
            "Please specify a file or folder[leave empty for default path]: ")
    if promptPath.find('"') >= 0:
        promptPath = promptPath.strip("\"")
    if os.path.isdir(promptPath) or promptPath == '':
        if promptPath == '':
            os.chdir(inPath)
            print("Working in default input path...")
        else:
            os.chdir(promptPath)
            batchConvert = []
        for item in os.listdir(os.getcwd()):
            if os.path.isfile(os.path.join(os.getcwd(), item)) \
                and item.endswith(('.mkv','.mp4')):
                vObj = videoFile(os.path.join(os.getcwd(), item))
                fPath = vObj.sInfo['fullPath']
                fName = vObj.sInfo['fileName']
                print(fName)
                vTrack = vObj.selectTrack('vTracks', 1)
                if vTrack == "continue":
                    continue
                elif vTrack == "break":
                    del batchConvert
                    break
                aTrack = vObj.selectTrack('aTracks', 2)
                if aTrack == "continue":
                    continue
                elif aTrack == "break":
                    del batchConvert
                    break
                tTrack = vObj.selectTrack('tTracks', 3)
                if tTrack == "continue":
                    continue
                elif tTrack == "break":
                    del batchConvert
                    break
                batchConvert.append((fPath, fName, vTrack, aTrack, tTrack))
        if 'batchConvert' in locals():
            for convert in batchConvert:
                #print(convert)
                convertVideo(*convert)
            input("All videos converted. Press enter to return to menu...")
    if os.path.isfile(promptPath):
        vObj = videoFile(promptPath)
        fPath = vObj.sInfo['fullPath']
        fname = vObj.sInfo['fileName']
        fPath = vObj.sInfo['fullPath']
        fName = vObj.sInfo['fileName']
        print(fName)
        vTrack = vObj.selectTrack('vTracks', 1)
        if type(vTrack) != 'int':
            print("Returning to main menu. Press enter to continue...")
            return
        aTrack = vObj.selectTrack('aTracks', 2)
        if type(aTrack) != 'int':
            print("Returning to main menu. Press enter to continue...")
            return
        tTrack = vObj.selectTrack('tTracks', 3)
        if type(tTrack) != 'int':
            print("Returning to main menu. Press enter to continue...")
            return
        convertVideo(fPath, fName, vTrack, aTrack, tTrack)
        input("Video converted. Press enter to return to menu...")

def convertVideo(fPath, fName, vTrack, aTrack, tTrack):
    "Creates ffmpeg subprocess based on inputs from conversion methods"
    # ffmpeg -vf option escape chars are '\' and ':'
    # must escape escape chars in Windows environments
    # not sure how necessary this is since linux uses other path characters
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

def videoInfo():
    "Show Info about all video, audio, and subtitle tracks"
    clearScreen()
    promptPath = input("Please enter file or path: ")
    if promptPath.find("\"") >= 0:
        promptPath = promptPath.strip("\"")
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

def clearScreen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    startup()
    convertMenu()
    sys.exit()
