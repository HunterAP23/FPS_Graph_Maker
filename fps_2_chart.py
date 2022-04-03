import os
import sys
from argparse import RawTextHelpFormatter
from datetime import datetime as dt
from io import StringIO
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from gooey import Gooey, GooeyParser
from matplotlib import animation


def anim_progress(cur_frame, total_frames):
    percent = "{0:.2f}".format(cur_frame * 100 / total_frames).zfill(5)
    print("Saving frame {0} out of {1} : {2}%".format(str(cur_frame), str(total_frames), percent))
    # sys.stdout.write(
    #     "\rSaving frame {0} out of {1} : {2}%".format(
    #         str(cur_frame), str(total_frames), percent
    #     )
    # )
    sys.stdout.flush()


def should_generate_graph(cur_file, overwrite):
    if overwrite:
        print(
            "User specified the overwrite argument, replacing old graphs with new ones."
        )
        return True
    elif os.path.isfile(cur_file):
        # overwrite = input(
        #     str(cur_file)
        #     + " already exists, do you want to generate the graph again? (0 -> No, 1 -> Yes): "
        # )
        # if int(overwrite) == 0:
        #     return False
        # else:
        #     return True
        return True
    else:
        print(str(cur_file) + " does not exist, generating.")
        return True


# def add_steppings(array, interp):
#     # return array.fillna(method="pad").repeat(60)

#     array_list = []
#     for item in array:
#         array_list.append(item)
#         for i in range(59):
#             array_list.append(np.nan)
#     if interp:
#         if interp == "linear":
#             return (
#                 pd.Series(array_list).interpolate(method="linear").fillna(method="pad")
#             )
#         elif interp == "cubic":
#             return (
#                 pd.Series(array_list).interpolate(method="cubic").fillna(method="pad")
#             )
#     else:
#         return pd.Series(array_list).interpolate(method="linear").fillna(method="pad")


def main(args):
    my_CSV = None
    # Does your CSV file exist?
    if os.path.isfile(args.GameBench_Report):
        print(str(args.GameBench_Report) + " exists.")
        my_CSV = args.GameBench_Report
    else:
        print("That CSV file doesn't exist. Are you sure it's there?")
        exit(1)

    my_file = open(my_CSV, "r")
    data = my_file.read()

    # Try to grab the different data from the CSV file
    # For a default GameBench report, this expects the separator to be a comma
    # and it will look for columsn titled FPS_TIMESTAMP and FPS_VALUE
    # if that fails, it will attempt to use a semi-colon as a separator, and
    # look for columns titled TIMESTAMP and FRAMERATE
    df = None
    df_type = None
    try:
        df = pd.read_csv(
            StringIO(data),
            usecols=lambda x: x.upper() in ["FPS_TIMESTAMP", "FPS_VALUE"],
            index_col=0,
        )
        df_type = "GameBench"
    except Exception:
        try:
            df = pd.read_csv(
                StringIO(data),
                sep=";",
                usecols=lambda x: x.upper() in ["TIMESTAMP", "FRAMERATE"],
                index_col=0,
            )
            df_type = "Other"
        except Exception:
            raise ValueError("No valid column header values found.")

    if df_type == "GameBench":
        df.rename(columns={"FPS_value": "framerate"}, inplace=True)
        df.index.names = ["timestamp"]
    index_fixed = []
    for i in df.index:
        index_fixed.append(i.replace("_", " ").replace("-", " ").replace(":", " "))
    for i in range(len(index_fixed)):
        i_split = index_fixed[i].split(" ")
        i_dt = dt(
            year=int(i_split[0]),
            month=int(i_split[1]),
            day=int(i_split[2]),
            hour=int(i_split[3]),
            minute=int(i_split[4]),
            second=int(i_split[5]),
            microsecond=int(i_split[6]) * 1000,
        )
        if i == 0:
            index_fixed[0] = float(i_dt.second + (i_dt.microsecond / 1000000))
        else:
            index_fixed[i] = (
                float(i_dt.second + (i_dt.microsecond / 1000000)) - index_fixed[0]
            )
    index_fixed[0] = 0.0
    df.index = index_fixed

    # replace original list of FPS values with one that doesn't
    # have any NaN values.
    # print("Removing NaN values.")
    # df = df[pd.notnull(df["FPS_value"])]

    # the index is really the values actually the FPS_timestamp column.
    # x -> FPS timestamp
    # y -> FPS value at that timestamp
    # x = np.asarray(df.index)
    x = None
    y = None
    if df_type == "GameBench":
        x = pd.Series(df.index)
        y = pd.Series(df["framerate"])
    else:
        x = pd.Series(df.index)
        y = pd.Series(df["framerate"])

    # set the all the plot params
    plt.rcParams.update(
        {
            "figure.facecolor": (0.0, 0.0, 0.0, 0.0),
            "figure.edgecolor": "black",
            "axes.facecolor": (0.0, 0.0, 0.0, 0.0),
            "savefig.facecolor": (0.0, 0.0, 0.0, 0.0),
            "legend.facecolor": (0.0, 0.0, 0.0, 0.0),
            "legend.edgecolor": "black",
            "legend.frameon": False,
            "savefig.transparent": True,
            "animation.codec": "qtrle",
            "font.size": 26,
        }
    )
    # fig, ax = plt.subplots()
    fig_fps = plt.figure(1)
    fig_frametime = plt.figure(2)
    fig_combined = plt.figure(3)

    fig_fps.patch.set_alpha(0.0)
    fig_frametime.patch.set_alpha(0.0)
    fig_combined.patch.set_alpha(0.0)
    # The inch size actually gets tranlated into the resolution
    # So 19.2 x 10.8 -> 1920x1080
    if args.resolution:
        if args.resolution == "720p":
            fig_fps.set_size_inches(12.8, 7.2)
            fig_frametime.set_size_inches(12.8, 7.2)
            fig_combined.set_size_inches(12.8, 7.2)
        elif args.resolution == "1080p":
            fig_fps.set_size_inches(19.2, 10.8)
            fig_frametime.set_size_inches(12.8, 7.2)
            fig_combined.set_size_inches(12.8, 7.2)
        elif args.resolution == "1440p":
            fig_fps.set_size_inches(25.6, 14.4)
            fig_frametime.set_size_inches(12.8, 7.2)
            fig_combined.set_size_inches(12.8, 7.2)
        elif args.resolution == "4k":
            fig_fps.set_size_inches(38.4, 21.6)
            fig_frametime.set_size_inches(12.8, 7.2)
            fig_combined.set_size_inches(12.8, 7.2)
    else:
        fig_fps.set_size_inches(19.2, 10.8)
        fig_frametime.set_size_inches(12.8, 7.2)
        fig_combined.set_size_inches(12.8, 7.2)

    if args.dpi:
        fig_fps.dpi = args.dpi
        fig_frametime.dpi = args.dpi
        fig_combined.dpi = args.dpi
    else:
        fig_fps.dpi = 100
        fig_frametime.dpi = 100
        fig_combined.dpi = 100

    # Some FPS values can be 0
    # Frame times are calculated as 1000 / FPS value
    # That means we'd get a division-by-zero error
    # To get around this, we ignore any division-by zero errors
    # The next problem is that the program will put in "inf" and "-inf" as the
    # values, so we have to replace them with 0 so the graph doesn't freak out
    print("Removing inf frame-time values from doing division-by-zero.")
    with np.errstate(divide="ignore", invalid="ignore"):
        # y2 = np.asarray(1000 / df["FPS_value"])
        y2 = pd.Series(1000 / df["framerate"])
    y2[y2 == np.Inf] = 0
    y2[y2 == np.NINF] = 0

    # print("X:")
    # print(x.to_string())
    # print("\nY:")
    # y.to_csv("y_test.csv")
    # print("\nY2:")
    # print(y2.to_string())
    # exit()

    # Since we only get FPS values roughly every second, rather than multiple
    # times a second, we'll be repeating values to smooth out the graph for 60
    # FPS playback.
    # For the X axis, we'll have this program make 60 steps for get from one
    # x value to the next.
    # We can do the same for the Y values, but for now it'll just stay at the
    # same values.
    # print("Making equal spacing between X axis values.")
    FPS_min = y.min()  # Lowest recorded FPS value
    FPS_max = y.max()  # Highest recorded FPS value
    FPS_mean = y.mean()  # Average FPS
    FPS_median = y.median()  # Median FPS
    time_min = y2.min()  # Lowest recorded frametime
    time_max = y2.max()  # Highest recorded frametime

    # x = add_steppings(x, args.interpolation)
    # y = add_steppings(y, args.interpolation)
    # y2 = add_steppings(y2, args.interpolation)

    # print("Repeating values to fit 60 FPS video format.")
    # y = np.repeat(y, 60)
    # y2 = np.repeat(y2, 60)

    length = len(x)  # Total count of frames
    # FPS_min = y.min()  # Lowest recorded FPS value
    # FPS_max = y.max()  # Highest recorded FPS value
    # FPS_mean = y.mean()  # Average FPS
    # FPS_median = y.median()  # Median FPS
    # time_min = y2.min()  # Lowest recorded frametime
    # time_max = y2.max()  # Highest recorded frametime

    print("# of Frames: {0}".format(length))
    print("Minimum FPS: {0}".format(FPS_min))
    print("Maximum FPS: {0}".format(FPS_max))
    print("Mean FPS: {0}".format(FPS_mean))
    print("Median FPS: {0}".format(FPS_median))
    print("Minimum Frametime: {0}ms".format(time_min))
    print("Maximum Frametime: {0}ms".format(time_max))

    ax_fps = fig_fps.subplots()
    ax_frametime = fig_frametime.subplots()
    ax_combined = fig_combined.subplots()

    # Set the range for the Y-axis between 0 and FPS_max * 1.1
    ax_fps.set_ylim(0, FPS_max * 1.1)
    ax_frametime.set_ylim(0, time_max * 1.1)
    ax_combined.set_ylim(0, FPS_max * 1.1)
    # Set the range for the initial X-axis
    # ax_fps.set_xlim(x.array[0] - x.array[60], x.array[60])
    # ax_frametime.set_xlim(x.array[0] - x.array[60], x.array[60])
    # ax_combined.set_xlim(x.array[0] - x.array[60], x.array[60])
    # ax_fps.set_xlim(x.array[0], x.array[60])
    ax_frametime.set_xlim(x.array[0], x.array[60])
    ax_combined.set_xlim(x.array[0], x.array[60])

    # Remove the X-axis ticks
    ax_fps.set_xticklabels([])
    ax_frametime.set_xticklabels([])
    ax_combined.set_xticklabels([])

    (line_fps,) = ax_fps.plot(x, y, "b")
    (line_frametime,) = ax_frametime.plot(x, y2, "r")
    (line_combined1,) = ax_combined.plot(x, y, "b")
    (line_combined2,) = ax_combined.plot(x, y2, "r")

    # Misc functions needed for the graphs
    # Ones with _fps are just for the FPS graph
    # Others with _frametime are just for the frametime
    # The ones with _combined are for both FPS + frametime in one chart
    def init_fps():
        line_fps.set_data([], [])
        return (line_fps,)

    def init_frametime():
        line_frametime.set_data([], [])
        return (line_frametime,)

    def init_combined():
        line_combined1.set_data([], [])
        line_combined2.set_data([], [])
        return (
            line_combined1,
            line_combined2,
        )

    # This actually plays the animations for each chart we want
    # The program doesn't display the graphs live,
    # the animations are generated in the background.
    fps_interval = float(100 / 6)
    fps_t = 0
    fps_shown = 0

    def animate_fps(i):
        nonlocal fps_t, fps_shown
        fps_t += fps_interval
        if fps_shown < len(x.array) and fps_t >= x.array[fps_shown]:
            fps_shown += 1
        line_fps.set_data(x.array[:fps_shown], y.array[:fps_shown])
        ax_fps.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return (line_fps,)

    frametime_t = 0
    frametime_shown = 0

    def animate_frametime(i):
        nonlocal frametime_t, frametime_shown
        frametime_t += fps_interval
        if frametime_shown < len(x.array) and frametime_t >= x.array[frametime_shown]:
            frametime_shown += 1
        line_frametime.set_data(x.array[:frametime_shown], y2.array[:frametime_shown])
        ax_frametime.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return (line_frametime,)

    combined_t = 0
    combined_shown = 0

    def animate_combined(i):
        nonlocal combined_t, combined_shown
        combined_t += fps_interval
        if combined_shown < len(x.array) and combined_t >= x.array[combined_shown]:
            combined_shown += 1
        line_combined1.set_data(x.array[:combined_shown], y.array[:combined_shown])
        line_combined2.set_data(x.array[:combined_shown], y2.array[:combined_shown])
        ax_combined.set_xlim(x.array[i] - x.array[60], x.array[i] + x.array[60])
        return (
            line_combined1,
            line_combined2,
        )

    # anim_fps = animation.FuncAnimation(
    #     fig, animate_fps, init_func=init_fps, frames=length, interval=fps_interval, blit=True, save_count=50)
    anim_fps = animation.FuncAnimation(
        fig_fps,
        animate_fps,
        init_func=init_fps,
        frames=length,
        interval=fps_interval,
        blit=True,
        save_count=50,
    )

    anim_frametime = animation.FuncAnimation(
        fig_frametime,
        animate_frametime,
        init_func=init_frametime,
        frames=length,
        interval=fps_interval,
        blit=True,
        save_count=50,
    )

    anim_combined = animation.FuncAnimation(
        fig_combined,
        animate_combined,
        init_func=init_combined,
        frames=length,
        interval=fps_interval,
        blit=True,
        save_count=50,
    )

    # Now we save each individual graph as it's own file.
    # We choose which files are saved based on the user's input in the
    # beginning of the program.

    rem = os.path.basename(my_CSV)
    my_path, my_file = os.path.abspath(my_CSV).split(rem)
    if my_path == "":
        my_path, my_file = os.getcwd().split("fps_2_chart.py")

    def save_fps(the_file):
        print("Saving FPS Graph to {0}".format(the_file))
        anim_fps.save(
            the_file,
            fps=60,
            dpi=args.dpi,
            savefig_kwargs={"transparent": True, "facecolor": "None"},
            progress_callback=anim_progress,
        )
        anim_progress(length, length)
        print("\nDone.\n")

    def save_frametime(the_file):
        print("Saving Frame Time Graph to {0}".format(the_file))
        anim_frametime.save(
            the_file,
            fps=60,
            dpi=args.dpi,
            savefig_kwargs={"transparent": True, "facecolor": "None"},
            progress_callback=anim_progress,
        )
        anim_progress(length, length)
        print("\nDone.\n")

    def save_combined(the_file):
        print("Saving Combined FPS + Frame Time Graph to {0}".format(the_file))
        anim_combined.save(
            the_file,
            fps=60,
            dpi=args.dpi,
            savefig_kwargs={"transparent": True, "facecolor": "None"},
            progress_callback=anim_progress,
        )
        anim_progress(length, length)
        print("\nDone.\n")

    file_fps = ""
    file_frametime = ""
    file_combined = ""
    if args.output:
        output_new = ".".join(args.output.split(".")[:-1])
        file_fps = "{0}_fps.mov".format(output_new)
        file_frametime = "{0}_frametime.mov".format(output_new)
        file_combined = "{0}_combined.mov".format(output_new)
    else:
        file_fps = "{0}anim_fps.mov".format(my_path)
        file_frametime = "{0}anim_frametime.mov".format(my_path)
        file_combined = "{0}anim_combined.mov".format(my_path)

    if args.type == "fps":
        if should_generate_graph(file_fps, args.overwrite):
            save_fps(file_fps)
    elif args.type == "frametime":
        if should_generate_graph(file_frametime, args.overwrite):
            save_frametime(file_frametime)
    elif args.type == "both":
        if should_generate_graph(file_combined, args.overwrite):
            save_combined(file_combined)
    elif args.type == "all":
        print("Saving all three files to {0}".format(my_path))
        if should_generate_graph(file_fps, args.overwrite):
            save_fps(file_fps)
        if should_generate_graph(file_frametime, args.overwrite):
            save_frametime(file_frametime)
        if should_generate_graph(file_combined, args.overwrite):
            save_combined(file_combined)


@Gooey(
    program_name="Framerate Graph Generator",
    default_size=(1280, 720),
    advanced=True,
    navigation="TABBED",
)
def parse_arguments():
    """Parse input arguments."""

    main_help = "Plot GameBench report to to a live video graph."
    parser = GooeyParser(description=main_help, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "GameBench_Report",
        widget="FileChooser",
        gooey_options={
            "default_dir": str(Path(__file__).parent),
            "message": "Input file name",
            "initial_value": "GameBench Report",
            "wildcard": "Comma separated file (*.csv)|*.csv|" "All files (*.*)|*.*",
        },
        help="GameBench CSV report file.",
    )

    output_help = 'Output filename (Default: "graph").\n'
    output_help += 'Depending on what you generate, the output files will have "_fps" or "_frametime" or "_both" appended to them\n'
    output_help += '(IE: "graph" would generate "graph_fps.mov").'
    parser.add_argument(
        "-o",
        "--output",
        default="graph",
        widget="FileSaver",
        gooey_options={
            "default_dir": str(Path(__file__).parent),
            "message": "Output file name",
            "default_file": "graph.mov",
            "initial_value": "graph.mov",
        },
        help=output_help,
    )

    interpolation_help = (
        "Choose the interpolation method for the FPS/FrametTime values.\n"
    )
    interpolation_help += '* "linear" uses linear interpolation - a straight line will be generated between each point (Default).'
    interpolation_help += '* "cubic" uses cubic interpolation. This tries to create smooth curves between points.'
    parser.add_argument(
        "-i",
        "--interpolation",
        type=str,
        default="linear",
        choices=["linear", "cubic"],
        widget="Dropdown",
        gooey_options={
            "initial_value": "linear",
        },
        help=interpolation_help,
    )

    type_help = "Choose the what output video graph files to generate.\n"
    type_help += '* "all" will generate all three graphs - FPS, Frame Time, and FPS + Frame Time combined (Default).\n'
    type_help += '* "fps" will only generate the FPS video graph.\n'
    type_help += '* "frametime" will only generate the Frame Time video graph.\n'
    type_help += (
        '* "combined" will only generate the combined FPS + Frame Time video graph.\n'
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        default="all",
        choices=["all", "fps", "frametime", "combined"],
        widget="Dropdown",
        gooey_options={
            "initial_value": "all",
        },
        help=type_help,
    )

    res_help = "Choose the resolution for the graph video (Default is 1080p).\n"
    res_help += "Note that higher values will mean drastically larger files and take substantially longer to encode."
    parser.add_argument(
        "-r",
        "--resolution",
        type=str,
        default="1080p",
        choices=["720p", "1080p", "1440p", "4k"],
        widget="Dropdown",
        gooey_options={
            "initial_value": "1080p",
        },
        help=res_help,
    )

    dpi_help = "Choose the DPI value for the graph image and video (Default is 100).\n"
    dpi_help = "A value of 100 means will create a file with the exact resolution that you set, whereas 200 DPI will be 2x the resolution.\n"
    dpi_help += "Note that higher values will mean drastically larger files and take substantially longer to encode.\n"
    parser.add_argument(
        "-d",
        "--dpi",
        type=int,
        default=100,
        widget="Slider",
        gooey_options={
            "min": 2,
            "max": 200,
            "initial_value": 100,
        },
        help=dpi_help,
    )

    overwrite_help = 'Use this flag to overwrite any existing files that have the same output name as the one set by the "-o" argument.'
    parser.add_argument(
        "--overwrite",
        required=False,
        action="store_true",
        help=overwrite_help,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
