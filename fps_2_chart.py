from io import StringIO
from matplotlib import animation
import matplotlib.pyplot as plt
from numpy import inf
import argparse as argp
import pandas as pd
import numpy as np
import shlex
import math
import statistics
import sys
import os


def anim_progress(cur_frame, total_frames):
    percent = "{0:.2f}".format(cur_frame * 100 / total_frames).zfill(5)
    sys.stdout.write("\rSaving frame " + str(cur_frame) + " out of " + str(total_frames) + " : " + percent + "%")
    sys.stdout.flush()


def should_generate_graph(cur_file):
    if os.path.isfile(cur_file):
        overwrite = input(str(cur_file) + " already exists, do you want to generate the graph again? (0 -> No, 1 -> Yes): ")
        if int(overwrite) == 0:
            return False
        else:
            return True
    else:
        print(str(cur_file) + " does not exist, generating.")
        return True


def add_steppings(array):
    # return array.fillna(method="pad").repeat(60)

    array_list = []
    for item in array:
        tmp_list = []
        array_list.append(item)
        for i in range(59):
            array_list.append(np.nan)
    new_array = pd.Series(array_list).interpolate(method="akima").fillna(method="pad")
    return new_array


def main(args):
    my_CSV = None
    files_to_save = None
    # If you gave the file as an initial parameter, use it
    if len(sys.argv) > 1:
        # Does your CSV file exist?
        if os.path.isfile(sys.argv[1]):
            print(str(sys.argv[1]) + " exists.")
            my_CSV = sys.argv[1]
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
                tmp_val = int(sys.argv[2])
                if tmp_val == 0:
                    files_to_save = 0
                elif tmp_val == 1:
                    files_to_save = 1
                elif tmp_val == 2:
                    files_to_save = 2
                elif tmp_val == 3:
                    files_to_save = 3
                else:
                    files_to_save = 3
            except ValueError:
                print("Non-integer value given for 2nd argument.")
                exit(2)
        else:
            files_to_save = 3
    else:  # No initial param -> ask for CSV file
        tmp_CSV = input("Give the explicit path to your CSV file: ")
        # Does your CSV file exist?
        if os.path.isfile(tmp_CSV):  # Does your CSV file exist?
            print(str(tmp_CSV) + " exists.")
            my_CSV = tmp_CSV
        else:
            print("That CSV file doesn't exist. Are you sure it's there?")
            exit(1)

        try:
            print("Enter one of the following options for what to print: ")
            print("0. Create FPS Graph")
            print("1. Create Frametime Graph")
            print("2. Create Combined FPS + Frametime Graph")
            print("3. Create all three graphs")
            user_input = input("Chose an option: ")
            tmp_val = int(user_input)
            if tmp_val == 0:
                files_to_save = 0
            elif tmp_val == 1:
                files_to_save = 1
            elif tmp_val == 2:
                files_to_save = 2
            elif tmp_val == 3:
                files_to_save = 3
            else:
                files_to_save = 3
        except ValueError:
            print("Non-integer value given for 2nd argument.")
            exit(2)

    print("User Choice: " + str(files_to_save))
    # read the CSV file
    my_file = open(my_CSV, "r")
    data = my_file.read()

    # this grabs only the two columns we need: FPS_timestamp and FPS_value
    df = pd.read_csv(
        StringIO(data),
        usecols=lambda x: x.upper() in [
            "FPS_TIMESTAMP",
            "FPS_VALUE"
        ],
        index_col=0
    )

    # replace original list of FPS values with one that doesn't
    # have any NaN values.
    # print("Removing NaN values.")
    # df = df[pd.notnull(df["FPS_value"])]

    # the index is really the values actually the FPS_timestamp column.
    # x -> FPS timestamp
    # y -> FPS value at that timestamp
    # x = np.asarray(df.index)
    x = pd.Series(df.index)
    y = pd.Series(df["FPS_value"])

    # set the all the plot params
    plt.rcParams.update({
        "figure.facecolor":  (0.0, 0.0, 0.0, 0.0),
        "figure.edgecolor":  "black",
        "axes.facecolor":    (0.0, 0.0, 0.0, 0.0),
        "savefig.facecolor": (0.0, 0.0, 0.0, 0.0),
        "legend.facecolor": (0.0, 0.0, 0.0, 0.0),
        "legend.edgecolor": "black",
        "legend.frameon": False,
        "savefig.transparent": True,
        "animation.codec": "qtrle",
        "font.size": 26,
        })
    fig, ax = plt.subplots()
    fig.patch.set_alpha(0.)
    # The inch size actually gets tranlated into the resolution
    # So 19.2 x 10.8 -> 1920x1080
    # Right now it's set to 4k, but it's easily changeable
    fig.set_size_inches(38.4, 21.6)
    fig.dpi = 500

    # Some FPS values can be 0
    # Frame times are calculated as 1000 / FPS value
    # That means we'd get a division-by-zero error
    # To get around this, we ignore any division-by zero errors
    # The next problem is that the program will put in "inf" and "-inf" as the
    # values, so we have to replace them with 0 so the graph doesn't freak out
    print("Removing inf frame-time values from doing division-by-zero.")
    with np.errstate(divide="ignore", invalid="ignore"):
        # y2 = np.asarray(1000 / df["FPS_value"])
        y2 = pd.Series(1000 / df["FPS_value"])
    y2[y2 == inf] = 0
    y2[y2 == -inf] = 0

    # Since we only get FPS values roughly every second, rather than multiple
    # times a second, we'll be repeating values to smooth out the graph for 60
    # FPS playback.
    # For the X axis, we'll have this program make 60 steps for get from one
    # x value to the next.
    # We can do the same for the Y values, but for now it'll just stay at the
    # same values.
    print("Making equal spacing between X axis values (to simulate 60fps)")
    # x = add_steppings(x)
    # y = add_steppings(y)
    # y2 = add_steppings(y2)
    x = add_steppings(x)
    y = add_steppings(y)
    y2 = add_steppings(y2)

    # print("Repeating values to fit 60 FPS video format.")
    # y = np.repeat(y, 60)
    # y2 = np.repeat(y2, 60)

    length = len(x)  # Total count of frames
    FPS_min = y.min()  # Lowest recorded FPS value
    FPS_max = y.max()  # Highest recorded FPS value
    FPS_mean = y.mean() # Average FPS
    FPS_median = y.median() # Median FPS
    time_min = y2.min()  # Lowest recorded frametime
    time_max = y2.max()  # Highest recorded frametime


    print("# of Frames: " + str(length))
    print("Minimum FPS: " + str(FPS_min))
    print("Maximum FPS: " + str(FPS_max))
    print("Mean FPS: " + str(FPS_mean))
    print("Median FPS: " + str(FPS_median))
    print("Minimum Frametime: " + str(time_min) + "ms")
    print("Maximum Frametime: " + str(time_max) + "ms")

    # Set the range for the Y-axis between 0 and 70
    ax.set_ylim(0, 70)
    # Set the range for the initial X-axis
    ax.set_xlim(x.array[0] - x.array[60], x.array[60])
    # Remove the X-axis ticks
    ax.set_xticklabels([])

    # line is just for the FPS graph
    line, = ax.plot(x, y, "b")
    # line2 is just for the frametime graph
    line2, = ax.plot(x, y2, "r")

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
        line.set_data(x.array[:i], y.array[:i])
        ax.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return line,

    def animate_frametime(i):
        line2.set_data(x.array[:i], y2.array[:i])
        ax.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return line2,

    def animate_combined(i):
        line.set_data(x.array[:i], y.array[:i])
        line2.set_data(x.array[:i], y2.array[:i])
        ax.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return line, line2,

    # This actually plays the animations for each chart we want
    # The program doesn't display the graphs live,
    # the animations happen in the background
    anim_fps = animation.FuncAnimation(
        fig, animate_fps, init_func=init_fps, frames=length, interval=float(100 / 6), blit=True, save_count=50)

    anim_frametime = animation.FuncAnimation(
        fig, animate_frametime, init_func=init_frametime, frames=length, interval=float(100 / 6), blit=True, save_count=50)

    anim_combined = animation.FuncAnimation(
        fig, animate_combined, init_func=init_combined, frames=length, interval=float(100 / 6), blit=True, save_count=50)

    # Now we save each individual graph as it's own file.
    # We choose which files are saved based on the user's input in the
    # beginning of the program.

    rem = os.path.basename(my_CSV)
    my_path, my_file = os.path.abspath(my_CSV).split(rem)
    if my_path == "":
        my_path, my_file = os.getcwd().split("fps_2_chart.py")
    tmpList = []

    def save_fps(the_file):
        print("Saving FPS Graph to " + str(my_path) + "anim_fps.mov")
        anim_fps.save(str(my_path) + "anim_fps.mov", fps=FPS_median, dpi=50, savefig_kwargs={"transparent": True, "facecolor": "None"}, progress_callback=anim_progress)
        anim_progress(length, length)
        print("\nDone.\n")

    def save_frametime(the_file):
        print("Saving Frame Time Graph to " + str(my_path) + "anim_frametime.mov")
        anim_frametime.save(str(my_path) + "anim_frametime.mov", fps=FPS_median, dpi=100, savefig_kwargs={"transparent": True, "facecolor": "None"}, progress_callback=anim_progress)
        anim_progress(length, length)
        print("\nDone.\n")

    def save_combined(the_file):
        print("Saving Combined FPS + Frame Time Graph to " + str(my_path) + "anim_combined.mov")
        anim_combined.save(str(my_path) + "anim_combined.mov", fps=FPS_median, dpi=100, savefig_kwargs={"transparent": True, "facecolor": "None"}, progress_callback=anim_progress)
        anim_progress(length, length)
        print("\nDone.\n")

    file_fps = str(my_path) + "anim_fps.mov"
    file_frametime = str(my_path) + "anim_frametime.mov"
    file_combined = str(my_path) + "anim_combined.mov"
    if files_to_save == 0:
        if should_generate_graph(file_fps):
            save_fps(file_fps)
    elif files_to_save == 1:
        if should_generate_graph(file_frametime):
            save_frametime(file_frametime)
    elif files_to_save == 2:
        if should_generate_graph(file_combined):
            save_combined(file_combined)
    elif files_to_save == 3:
        print("Saving all three files to " + str(my_path))
        if should_generate_graph(str(my_path) + "anim_fps.mov"):
            save_fps(file_fps)
        if should_generate_graph(str(my_path) + "anim_frametime.mov"):
            save_frametime(file_frametime)
        if should_generate_graph(str(my_path) + "anim_combined.mov"):
            save_frametime(file_frametime)

def parse_arguments():
    main_help = "Plot GameBench report to to a live video graph.\n"
    parser = argp.ArgumentParser(description=main_help, formatter_class=argp.RawTextHelpFormatter)
    parser.add_argument("GameBench_Report", type=str, help="GameBench CSV report file.")

    o_help = "Output filename (Default: vmaf.png).\nAlso defines the name of the output graph (Default: vmaf.mov)."
    parser.add_argument("-o", "--output", dest="output", type=str, default="vmaf.png", help=o_help)

    l_help = "Choose what the lowest value of the graph will be.\n"
    l_help += "* \"default\" uses the lowest VMAF value minus 5  as the lowest point of the y-axis so the values aren't so stretched vertically.\n"
    l_help += "* \"min\" will use whatever the lowest VMAF value is as the lowest point of the y-axis. Makes the data look a bit stretched vertically.\n"
    l_help += "* \"zero\" will explicitly use 0 as the lowest point on the y-axis. Makes the data look a bit compressed vertically.\n"
    l_help += "* \"custom\" will use the value entered by the user in the \"-c\" / \"--custom\" option."
    parser.add_argument("-l", "--lower-boundary", dest="low", type=str, default="default", choices=["default", "min", "zero", "custom"], help=l_help)

    custom_help = "Enter custom minimum point for y-axis. Requires \"-l\" / \"--lower-boundary\" set to \"custom\" to work.\nThis option expects an integer value."
    parser.add_argument("-c", "--custom", dest="custom", type=int, help=custom_help)

    res_help = "Choose the resolution for the graph video (Default is 1080p).\n"
    res_help += "Note that higher values will mean drastically larger files and take substantially longer to encode."
    parser.add_argument("-r", "--resolution", dest="res", type=str, default="1080p", choices=["720p", "1080p", "1440p", "4k"], help=res_help)

    dpi_help = "Choose the DPI for the graph image and video (Default is 100).\n"
    dpi_help += "Note that higher values will mean drastically larger files and take substantially longer to encode.\n"
    dpi_help += "This setting applies only to the video file, not the image file."
    parser.add_argument("-d", "--dpi", dest="dpi", type=float, default="100", help=dpi_help)

    args = parser.parse_args()

    if args.low == "custom":
        try:
            if args.custom < 0 or args.custom > 100:
                parser.error("Value {0} for \"custom\" argument was not in the valid range of 0 to 100.".format(float(args.custom)))
                exit()
        except ValueError as ve:
            print(ve)
            exit()

    return(args)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
