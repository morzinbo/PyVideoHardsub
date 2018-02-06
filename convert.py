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
from pymediainfo import MediaInfo

#NOTES

#Accepted filetypes
fileTypes = ('.mp4', '.mkv', '.webm')

def createConfig():
    config = configparser.ConfigParser()
    curPath = os.getcwd()
    if platform.system() == 'Windows':
        config['paths'] = {
            'ffmpeg path':         os.path.join(curPath, 'bin', 'ffmpeg'),
            'default input path':  os.path.join(curPath, 'in'),
            'default output path': os.path.join(curPath, 'out')
        }
    else:
        config['paths'] = {
            'default input path': os.path.join(curPath, 'in'),
            'default output path': os.path.join(curPath, 'out')
        }
    with open('convert.ini', 'w') as configfile:
        config.write(configfile)

def readConfig():
    global ffmpeg, inPath, outPath
    config = configparser.ConfigParser()
    config.read('convert.ini')
    if platform.system() == 'Windows':
        ffmpeg =  config['paths']['ffmpeg path']
    else:
        ffmpeg = 'ffmpeg'
    inPath =  config['paths']['default input path']
    outPath = config['paths']['default output path']


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
    promptPath = input("Please specify a file or folder: ")
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
    promptPath = input("Please specify a file or folder: ")
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
        for item in os.listfir(os.getcwd()):
            if os.path.isfile(os.path.join(os.getcwd(),item)) \
                and item.endswith(fileTypes):
                videoFile(os.path.join(os.getcwd(), name)).showVideoInfo()
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

def testStuff():
    x = ""
    clearScreen()
    while x != 'q':
        inFile = input("Please enter file or path: ")
        if inFile.find("\"") >= 0:
            inFile = inFile.replace("\"", "")
        if inFile != '':
            if os.path.isdir(inFile):
                print("Directory detected. Changing working directory to", \
                    inFile)
                os.chdir(inFile)
                for item in os.listdir(os.getcwd()):
                    if os.path.isfile(os.path.join(os.getcwd(),item)) \
                        and item.endswith(fileTypes):
                        print(item)
                #for __, dirs, files in os.walk(".", topdown = False):
                #    dirs[:] = [d for d in dirs if d not in exclude]
                #    for name in files:
                #        print(os.path.join(os.getcwd(),name))
                        #filesInPath.append(os.path.join(os.getcwd(), name))
                        #vObj = videoFile(os.path.join(os.getcwd(), name))
                        #print("Showing video information for", name)
                        #videoFile.showVideoInfo(vObj)
                        #input("Press enter to continue")
                        #print()
                    #for name in dirs:
                    #    print(os.path.join(os.getcwd(), name))
                #print("Total files in path:", len(filesInPath))
                #print("Listing files...")
                #for c, files in enumerate(filesInPath):
                #    print(c+1, files)
                #for files in filesInPath:
                #    vObj = videoFile(files)
                #    print("Showing video information for", files)
                #    videoFile.showVideoInfo(vObj)
                #    input("Press enter to continue...")
            elif os.path.isfile(inFile):
                print("File detected.")
                print(os.path.basename(inFile))
        else:
            print("No input found!")
        x = input("Type q to exit: ")
    clearScreen()
    sys.exit()

def testStuff2():
    x = ''
    while x != 'q':
        #vFile = videoFile(r"E:\Documents\Actual Documents\Projects\Python\in\[Abesu] Sayonara Zetsubou Sensei - 01 (720p).mkv")
        vFile = videoFile(r"E:\Documents\Actual Documents\Projects\Python\in\[HTT]_Kimi_no_Na_wa._[Blu-Ray][Hi10][720p][48E78967].mkv")
        #print(type(vFile.sInfo['aTracks']))
        #print(vFile.sInfo['aTracks'])
        current_track = 'aTracks'
        if type(vFile.sInfo[current_track]) == int:
            #print("One audio track found: Track", vFile.sInfo['aTracks'])
            loopNext = vFile.sInfo[current_track] + 1
            loopEnd  = vFile.sInfo[current_track] + 2
            print("Track 1:", vFile.sInfo['%s_title' % vFile.sInfo[current_track]],\
                vFile.sInfo['%s_format' % vFile.sInfo[current_track]])
        else:
            #print("Multiple audio tracks found!")
            #for tracks in vFile.sInfo['aTracks']:
            #    print("Audio Track:", tracks)
            loopNext = len(vFile.sInfo[current_track]) + 1
            loopEnd  = len(vFile.sInfo[current_track]) + 2
            print("Select an Audio track:")
            for c, tracks in enumerate(vFile.sInfo[current_track]):
                print("Track %s:" % str(c+1), vFile.sInfo['%s_title' % tracks],\
                    vFile.sInfo['%s_format' % tracks])
        #
        x = input("press q to exit:")
    sys.exit()

if __name__ == '__main__':
    if not os.path.isfile(os.path.join(os.getcwd(),'convert.ini')):
        createConfig()
    readConfig()
    convertMenu()
    sys.exit()
