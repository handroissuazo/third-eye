from ftplib import FTP
from fnmatch import fnmatch
from time import time
from threading import Thread
import os
import subprocess

# GLOBAL terminal call to generate photos from video (just need to change the name of the video 3dRenderme.mp4 to whatever)
# Ex: "ffmpeg -i 3dRenderMe.mp4 -vf fps=2/1 -s 1280/720 img%03d.jpg"
makePhotosCmd = "ffmpeg -i {videoFileName} -vf fps=2/1 -s 1280/720 {picturePath}/img%03d.jpg"

# Ex: "./VisualSFM sfm ~/Downloads/superPhotos ~/Downloads/superPhotos/Money/cmdLineTest.nvm"
runSparseCmd = "/home/alejandro/vsfm/vsfm/bin/VisualSFM sfm {directoryOfPhotos} {newSparseReconstructionFile}"

# Ex: "./VisualSFM sfm+loadnvm+cmvs ~/Downloads/superPhotos/Money/cmdLineTest.nvm ~/Downloads/superPhotos/Money/cmdLineFinal.nvm"
runDenseCmd = "/home/alejandro/vsfm/vsfm/bin/VisualSFM sfm+loadnvm+cmvs {sparseReconstructionFile} {newDenseReconstructionFile}"

runRenderCmd = "/home/alejandro/vsfm/vsfm/bin/VisualSFM sfm+resume+pmvs {sparseReconstructionFile} {denseReconstructionFile}"

# GLOBAL ftp object initialization
# Login to FTP server.
ftp=FTP("192.168.1.3")
ftp.login('default')
ftp.cwd('DCIM')               # change into \DCIM directory
ftp.cwd('100MEDIA')               # change into \100MEDIA directory

# Generate file information dictionary in the format
# [{
#   fileName: name, <- Name of the video file.
#   size: ####,     <- Value of last saved size of video file.
#   timeRead: ####  <- Value used to know whether or not the video is currently being created.
# }, ... ]
def get_video_file_info_from_server(directory, videoFilesArr):
    for filename in ftp.nlst(directory):
        if fnmatch(filename, '*.MOV'):
            bAddToVideoFiles = True

            # Make sure we haven't already saved the file.
            for videoFile in videoFilesArr:
                if videoFile["fileName"] == filename:
                    bAddToVideoFiles = False
                    break

            # Add the file to our array
            if bAddToVideoFiles:
                videoFileObj =  {
                                  "fileName": filename, # Save file name
                                  "size": ftp.size(filename), # Get file size
                                  "timeRead": time() # Get current time
                                }
                videoFilesArr.append(videoFileObj)


def get_videos_from_server( videoFilesArr, renderVideoList ):
    for video in videoFilesArr:
        currentTime = time() # Get current time in seconds.
        if video["timeRead"] + 5 < currentTime:
            videoFileName = video["fileName"]
            currentVideoSizeOnFTPServer = ftp.size( videoFileName )

            if currentVideoSizeOnFTPServer == video["size"]:
                # Download file
                getFTPCommand = "RETR " + videoFileName

                # Create Directory with fileName without file type.
                os.mkdir(videoFileName[:-4])

                # Download video into new directory
                videoFilePath = videoFileName[:-4] + "/" + videoFileName
                ftp.retrbinary(getFTPCommand, open(videoFilePath, 'wb').write)
                print("Downloaded " + videoFileName)

                # Delete video from server and remove entry from video file list
                ftp.delete( videoFileName )
                videoFilesArr.remove( video )

                # Save the video name to to later use in the 3d rendering process! :D
                renderVideoList.append( videoFileName )
            else:
                # Update the
                video["size"] = currentVideoSizeOnFTPServer
                video["timeRead"] = currentTime


def render_videos(renderVideoArr):
    while 0 < len(renderVideoArr):
        for fileName in renderVideoArr:
            renderVideoArr.remove( fileName ) # Remove immediately so other threads do not attempt to render on same file.
            p = Thread(target=render_video, args=(fileName,))
            p.start()


def render_video( fileName ):
    print( "Rendering " + fileName )
    # Note file path is just the file name without the file type
    cwd = os.getcwd()  # Get current working directory
    fileDir = cwd + "/" + fileName[:-4]
    filePath = cwd + "/" + fileName[:-4] + "/" + fileName

    # Create Images from video
    createImagesCommand = makePhotosCmd.format(videoFileName=filePath, picturePath=fileDir)
    imagesCommandList = createImagesCommand.split()
    subprocess.run(imagesCommandList)

    # Run sparse reconstruction
    newSparseFile = fileDir + "/" + fileName[:-4] + "_sparse.nvm"
    sparseReconCommand = runSparseCmd.format(directoryOfPhotos=fileDir, newSparseReconstructionFile=newSparseFile)
    sparseCommandList = sparseReconCommand.split()
    subprocess.run(sparseCommandList)

    # Run dense reconstruction
    newDenseFile = fileDir + "/" + fileName[:-4] + "_dense.nvm"
    denseReconCommand = runDenseCmd.format(sparseReconstructionFile=newSparseFile, newDenseReconstructionFile=newDenseFile)
    denseCommandList = denseReconCommand.split()
    subprocess.run(denseCommandList)

    #Run ply render generation
    renderCommand = runRenderCmd.format(sparseReconstructionFile=newSparseFile, denseReconstructionFile=newDenseFile)
    renderCommandList = renderCommand.split()
    subprocess.run(renderCommandList)

# MAIN
if __name__ == '__main__':
    videoFiles = []
    renderVideoList = []
    get_video_file_info_from_server('.', videoFiles)

    while 0 < len(videoFiles):
        get_videos_from_server(videoFiles, renderVideoList)
        render_videos(renderVideoList)
        get_video_file_info_from_server('.', videoFiles)

