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

dir_path = os.path.dirname(os.path.realpath(__file__))


def set_globals_based_on_os():
    global makePhotosCmd
    global runSparseCmd
    global runDenseCmd
    global runRenderCmd

    # if OS is windows
    if os.name == 'nt':
        # Ex: "ffmpeg-3.3.2-win64-static\bin\ffmpeg -i 3dRenderMe.mp4 -vf fps=2/1 -s 1280/720 img%03d.jpg"
        makePhotosCmd = dir_path + "\\ffmpeg-3.3.2-win64-static\\bin\\ffmpeg.exe -i {videoFileName} -vf fps=2/1 -s 1280/720 {picturePath}\\img%03d.jpg"

        # Ex: "./VisualSFM sfm ~/Downloads/superPhotos ~/Downloads/superPhotos/Money/cmdLineTest.nvm"
        runSparseCmd = dir_path + "\\vsfm_windows_64bit\\VisualSFM.exe sfm {directoryOfPhotos} {newSparseReconstructionFile}"

        # Ex: "./VisualSFM sfm+loadnvm+cmvs ~/Downloads/superPhotos/Money/cmdLineTest.nvm ~/Downloads/superPhotos/Money/cmdLineFinal.nvm"
        runDenseCmd = dir_path + "\\vsfm_windows_64bit\\VisualSFM.exe sfm+loadnvm+cmvs {sparseReconstructionFile} {newDenseReconstructionFile}"

        runRenderCmd = dir_path + "\\vsfm_windows_64bit\\VisualSFM.exe sfm+resume+pmvs {sparseReconstructionFile} {denseReconstructionFile}"


def get_videos_from_home_directory(videoDirectory, renderVideoList):
    if not os.path.isdir(dir_path + "\\" + videoDirectory):
        os.makedirs(dir_path + "\\" + videoDirectory)

    for file in os.listdir(dir_path + "\\" + videoDirectory):
        if file.endswith('.mkv') or file.endswith('.MOV') or file.endswith('.mp4'):
            renderVideoList.append(file)


def render_videos(renderVideoArr):
    while 0 < len(renderVideoArr):
        for fileName in renderVideoArr:
            renderVideoArr.remove(
                fileName)  # Remove immediately so other threads do not attempt to render on same file.
            render_video(fileName)
            


def render_video(fileName):
    print("Rendering " + fileName)
    # Note file path is just the file name without the file type
    cwd = os.getcwd()  # Get current working directory
    fileDir = cwd + "\\videos" + "\\" + fileName[:-4]
    filePath = cwd + "\\videos\\" + fileName

    #Store images and other files here
    if not os.path.isdir(fileDir):
        os.makedirs(fileDir)

    # Create Images from video
    createImagesCommand = makePhotosCmd.format(videoFileName=filePath, picturePath=fileDir)
    imagesCommandList = createImagesCommand.split()
    subprocess.run(imagesCommandList)

    # Run sparse reconstruction
    newSparseFile = fileDir + "\\" + fileName[:-4] + "_sparse.nvm"
    sparseReconCommand = runSparseCmd.format(directoryOfPhotos=fileDir, newSparseReconstructionFile=newSparseFile)
    sparseCommandList = sparseReconCommand.split()
    subprocess.call(sparseCommandList)

    # Run dense reconstruction
    newDenseFile = fileDir + "\\" + fileName[:-4] + "_dense.nvm"
    denseReconCommand = runDenseCmd.format(sparseReconstructionFile=newSparseFile,
                                           newDenseReconstructionFile=newDenseFile)
    denseCommandList = denseReconCommand.split()
    subprocess.call(denseCommandList)

    # Run ply render generation
    renderCommand = runRenderCmd.format(sparseReconstructionFile=newSparseFile, denseReconstructionFile=newDenseFile)
    renderCommandList = renderCommand.split()
    subprocess.call(renderCommandList)


# MAIN
if __name__ == '__main__':
    renderVideoList = []
    set_globals_based_on_os()
    get_videos_from_home_directory("videos", renderVideoList)
    render_videos(renderVideoList)
