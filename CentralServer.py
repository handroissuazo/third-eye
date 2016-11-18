from ftplib import FTP
from fnmatch import fnmatch
from time import time
from threading import Thread

# GLOBAL terminal call to generate photos from video (just need to change the name of the video 3dRenderme.mp4 to whatever)
makePhotosCmd = "ffmpeg -i 3dRenderMe.mp4 -vf fps=2/1 -s 1280/720 img%03d.jpg"
runSparseCmd = "./VisualSFM sfm ~/Downloads/superPhotos ~/Downloads/superPhotos/Money/cmdLineTest.nvm"
runDenseAndRenderCmd = "./VisualSFM sfm+loadnvm+cmvs ~/Downloads/superPhotos/Money/cmdLineTest.nvm ~/Downloads/superPhotos/Money/cmdLineFinal.nvm"

# GLOBAL ftp object initialization
# Login to FTP server.
ftp=FTP("192.168.1.3")
ftp.login()
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
                ftp.retrbinary(getFTPCommand, open(videoFileName, 'wb').write)
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
            p = Thread(render_video, args=(fileName,))
            p.start()


def render_video( fileName ):
    # TODO: ACTUALLY RENDER THE 3D MAP FROM THE VIDEO....
    print( "Render" + fileName )


# MAIN
if __name__ == '__main__':
    videoFiles = []
    renderVideoList = []

    get_video_file_info_from_server( '.', videoFiles )

    while 0 < len(videoFiles):
        render_videos( renderVideoList )
        get_video_file_info_from_server('.', videoFiles)
        get_videos_from_server(videoFiles, renderVideoList)

