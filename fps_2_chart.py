from pandas.compat import StringIO
from matplotlib import animation
import matplotlib.pyplot as plt
from numpy import inf
import pandas as pd
import numpy as np
import shlex
import ffmpy
import sys
import os

if __name__ == '__main__':
    myCSV = None
    filesToSave = None
    # If you gave the file as an initial parameter, use it
    if len(sys.argv) > 1:
        # Does your CSV file exist?
        if os.path.isfile(sys.argv[1]):
            print(str(sys.argv[1]) + " exists.")
            myCSV = sys.argv[1]
        else:
            print("That CSV file doesn't exist. Are you sure it's there?")
            exit(1)

        # After the file, you should include a number from 0 to 3
        # regarding what graphs you want generated
        # 0 -> FPS
        # 1 -> Frametime
        # 2 -> Combined
        # 3 -> All three graphs
        # If no number is given, assume 3
        if len(sys.argv) > 2:
            try:
                tmpVal = int(sys.argv[2])
                if tmpVal == 0:
                    filesToSave = 0
                elif tmpVal == 1:
                    filesToSave = 1
                elif tmpVal == 2:
                    filesToSave = 2
                elif tmpVal == 3:
                    filesToSave = 3
                else:
                    filesToSave = 3
            except ValueError:
                print("Non-integer value given for 2nd argument.")
                exit(2)
        else:
            filesToSave = 3
    else:  # No initial param -> ask for CSV file
        tmpCSV = input("Give the explicit path to your CSV file: ")
        # Does your CSV file exist?
        if os.path.isfile(tmpCSV):  # Does your CSV file exist?
            print(str(tmpCSV) + " exists.")
            myCSV = tmpCSV
        else:
            print("That CSV file doesn't exist. Are you sure it's there?")
            exit(1)

        try:
            print("Enter one of the following options for what to print: ")
            print("0. Create FPS Graph")
            print("1. Create Frametime Graph")
            print("2. Create Combined FPS + Frametime Graph")
            print("3. Create all three graphs")
            userInput = input("Chose an option: ")
            tmpVal = int(userInput)
            if tmpVal == 0:
                filesToSave = 0
            elif tmpVal == 1:
                filesToSave = 1
            elif tmpVal == 2:
                filesToSave = 2
            elif tmpVal == 3:
                filesToSave = 3
            else:
                filesToSave = 3
        except ValueError:
            print("Non-integer value given for 2nd argument.")
            exit(2)

    print("User Choice: " + str(filesToSave))
    # read the CSV file
    myFile = open(myCSV, 'r')
    data = myFile.read()

    # this grabs only the two columns we need: FPS_timestamp and FPS_value
    df = pd.read_csv(
        StringIO(data),
        usecols=lambda x: x.upper() in [
            'FPS_TIMESTAMP',
            'FPS_VALUE'
        ],
        index_col=0
    )

    # replace original list of FPS values with one that doesn't
    # have any NaN values.
    print("Removing NaN values.")
    df = df[pd.notnull(df['FPS_value'])]

    # the index is really the values actually the FPS_timestamp column.
    # x -> FPS timestamp
    # y -> FPS value at that timestamp
    x = np.asarray(df.index)
    y = np.asarray(df['FPS_value'])

    # set the font size to 22
    plt.rcParams.update({'font.size': 22})
    fig, ax = plt.subplots()
    fig.patch.set_alpha(0.)
    # The inch size actually gets tranlated into the resolution
    # So 19.2 x 10.8 -> 1920x1080
    # Right now it's set to 4k, but it's easily changeable
    fig.set_size_inches(38.4, 21.6)
    fig.dpi = 100

    # Some FPS values can be 0
    # Frame times are calculated as 1000 / FPS value
    # That means wee'd get a division-by-zero error
    # To get aroudn this, we ignore any division-by zero errors
    # The next problem is that the program will put in "inf" and "-inf"
    # as the values, so we have to replace them with 0 so the graph doesn't look bad
    print("Removing inf frame-time values from doing division-by-zero.")
    with np.errstate(divide='ignore', invalid='ignore'):
        y2 = np.asarray(1000 / df['FPS_value'])
    y2[y2 == inf] = 0
    y2[y2 == -inf] = 0

    length = len(df['FPS_value'])  # Total count of frames
    minFPS = y.min()  # Lowest recorded FPS value
    maxFPS = y.max()  # Highest recorded FPS value
    minTime = y2.min()  # Lowest recorded frametime
    maxTime = y2.max()  # Highest recorded frametime

    print("# of Frames: " + str(length))
    print("min FPS: " + str(minFPS))
    print("max FPS: " + str(maxFPS))
    print("min Frametime: " + str(minTime) + "ms")
    print("max Frametime: " + str(maxTime) + "ms")

    # Set the range for the Y-axis between 0 and 70
    ax.set_ylim(0, 70)
    # Set the range for the initial X-axis
    ax.set_xlim(x[0] - x[60], x[60])
    # Remove the X-axis ticks
    ax.set_xticklabels([])
    # line is just for the FPS graph
    line, = ax.plot(x, y)
    # line2 is just for the frametime graph
    line2, = ax.plot(x, y2)

    # Misc functions needed for the graphs
    # Ones with _fps are just for the FPS graph
    # Others with _frametime are just for the frametime
    # The ones with _combined are for both FPS + frametime in one chart
    def init_fps():
        line.set_data([], [])
        return line,

    def init_frametime():
        line2.set_data([], [])
        return line2,

    def init_combined():
        line.set_data([], [])
        line2.set_data([], [])
        return line, line2,

    def animate_fps(i):
        line.set_data(x[:i], y[:i])
        ax.set_xlim(x[i] - x[60], x[i] + x[60])
        return line,

    def animate_frametime(i):
        line2.set_data(x[:i], y2[:i])
        ax.set_xlim(x[i] - x[60], x[i] + x[60])
        return line2,

    def animate_combined(i):
        line.set_data(x[:i], y[:i])
        line2.set_data(x[:i], y2[:i])
        ax.set_xlim(x[i] - x[60], x[i] + x[60])
        return line, line2,

    # This actually plays the animations for each chart we want
    # The program doesn't display the graphs live,
    # the animations happen in the background
    anim_fps = animation.FuncAnimation(
        fig, animate_fps, init_func=init_fps, frames=length, interval=100/6, blit=True, save_count=50)

    anim_frametime = animation.FuncAnimation(
        fig, animate_frametime, init_func=init_frametime, frames=length, interval=100/6, blit=True, save_count=50)

    anim_combined = animation.FuncAnimation(
        fig, animate_combined, init_func=init_combined, frames=length, interval=100/6, blit=True, save_count=50)

    # Now we save each individual graph as it's own file.
    # We choose which files are saved based on the user's input in the
    # beginning of the program.

    if filesToSave == 0:
        print("Saving FPS Graph.")
        anim_fps.save('anim_fps.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")
    elif filesToSave == 1:
        print("Saving Frame Time Graph.")
        anim_frametime.save('anim_frametime.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")
    elif filesToSave == 2:
        print("Saving Combined FPS + Frame Time Graph.")
        anim_combined.save('anim_combined.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")
    elif filesToSave == 3:
        print("Saving all three files.")

        print("Saving FPS Graph.")
        anim_fps.save('anim_fps.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")

        print("Saving Frame Time Graph.")
        anim_frametime.save('anim_frametime.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")

        print("Saving Combined FPS + Frame Time Graph.")
        anim_combined.save('anim_combined.mp4', fps=60, dpi=100, extra_args=['-c:v', 'libx264'])
        print("Done.\n")

    # Then we use ffmpeg through the ffmpy module to re-encode
    # the videos with transparency in MOV format
    print("Re-encoding the videos graph videos with transparency.")
    tmpList = ['anim_fps.mp4', 'anim_frametime.mp4', 'anim_combined.mp4']
    for file in tmpList:
        print("Re-encoding " + str(file))
        exportName = file.replace(".mp4", "_PNG.mov")
        encoderCommands = []
        tmpCommands = "-hide_banner -i " + repr(file) + " -crf 18 -c:v png -vf chromakey=white"
        tmpStuff = shlex.split(tmpCommands)
        for i in range(0, len(tmpStuff), 1):
            encoderCommands.append(tmpStuff[i])

        myPass = ffmpy.FFmpeg(
            outputs={str(exportName): encoderCommands}
        )
        myPass.run()
