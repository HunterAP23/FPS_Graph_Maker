import math
import os
import sys
from argparse import RawTextHelpFormatter
from datetime import datetime as dt
from io import StringIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gooey import Gooey, GooeyParser
from matplotlib import animation


def anim_progress(cur_frame, total_frames):
    percent = "{0:.2f}".format(cur_frame * 100 / total_frames).zfill(5)
    print(
        "Saving frame {0} out of {1} : {2}%".format(
            str(cur_frame), str(total_frames), percent
        )
    )
    sys.stdout.flush()


def animate(plots, length, x, y, y2, interval, args):
    for plts in plots.keys():
        t = 0
        shown = 0

        def init():
            if "line" in plots[plts].keys():
                plots[plts]["line"].set_data([], [])
                return (plots[plts]["line"],)
            else:
                plots[plts]["line1"].set_data([], [])
                plots[plts]["line2"].set_data([], [])
                return (
                    plots[plts]["line1"],
                    plots[plts]["line2"],
                )

        def anim(i):
            # nonlocal t, shown
            # t += interval
            # if shown < len(x.array) and t >= x.array[shown]:
            #     shown += 1
            # if "line" in plots[plts].keys():
            #     plots[plts]["line"].set_data(x.array[:shown], y.array[:shown])
            # else:
            #     plots[plts]["line1"].set_data(x.array[:shown], y.array[:shown])
            #     plots[plts]["line2"].set_data(x.array[:shown], y2.array[:shown])
            # plots[plts]["ax"].set_xlim(
            #     x.array[i] - x.array[60], x.array[i] + x.array[60]
            # )
            # if "line" in plots[plts].keys():
            #     return (plots[plts]["line"],)
            # else:
            #     return (
            #         plots[plts]["line1"],
            #         plots[plts]["line2"],
            #     )
            if "line" in plots[plts].keys():
                plots[plts]["line"].set_data(x.array[:i], y.array[:i])
            else:
                plots[plts]["line1"].set_data(x.array[:i], y.array[:i])
                plots[plts]["line2"].set_data(x.array[:i], y2.array[:i])
            if i + 60 >= length:
                plots[plts]["ax"].set_xlim(
                    x.array[i-60], x.array[length-(length-i)]
                )
            else:
                plots[plts]["ax"].set_xlim(
                    # x.array[i] - x.array[60], x.array[i] + x.array[60]
                    x.array[i-60], x.array[i+60]
                )
            if "line" in plots[plts].keys():
                return (plots[plts]["line"],)
            else:
                return (
                    plots[plts]["line1"],
                    plots[plts]["line2"],
                )

        anim_func = animation.FuncAnimation(
            plots[plts]["figure"],
            anim,
            init_func=init,
            frames=length,
            interval=interval,
            blit=True,
            save_count=50,
        )

        if (
            (plts == "FPS" and args.export_fps)
            or (plts == "Frametime" and args.export_frametime)
            or (plts == "Combined" and args.export_combined)
        ):
            print("Saving {0} Graph to {1}".format(plots[plts], plots[plts]["filename"]))
            anim_func.save(
                plots[plts]["filename"],
                fps=60,
                dpi=args.dpi,
                savefig_kwargs={"transparent": True, "facecolor": "None"},
                progress_callback=anim_progress,
            )
            print("\nDone.\n")


def main(args):
    # my_CSV = None
    # # Does your CSV file exist?
    # if os.path.isfile(args.CSV_Report):
    #     print(str(args.CSV_Report) + " exists.")
    #     my_CSV = args.CSV_Report
    # else:
    #     print("That CSV file doesn't exist. Are you sure it's there?")
    #     exit(1)
    my_CSV = args.CSV_Report

    my_file = open(my_CSV, "r")
    data = my_file.read()

    # We'll attempt to use a semi-colon as a separator, and look for columns titled TIMESTAMP and FRAMERATE
    try:
        df = pd.read_csv(
            StringIO(data),
            sep=";",
            usecols=lambda x: x.upper() in ["TIMESTAMP", "FRAMERATE"],
            index_col=0,
        )
    except Exception:
        raise ValueError("No valid column header values found.")

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
        # if i == 0:
        #     # index_fixed[0] = float(i_dt.second + (i_dt.microsecond / 1000000))
        #     index_fixed[0] = i_dt
        # else:
        #     index_fixed[i] = (
        #         # float(i_dt.second + (i_dt.microsecond / 1000000)) - index_fixed[0]
        #         i_dt - index_fixed[0]
        #     )
        index_fixed[i] = i_dt
    # index_fixed[0] = 0.0
    df.index = index_fixed
    try:
        df = df.resample("16.6667L").interpolate(method="cubic")
        index_scaled = []
        for i in range(len(df.index)):
            to_dt = df.index[i].to_pydatetime()
            index_scaled.append(float(to_dt.second + (to_dt.microsecond / 1000000)))
        df.index = index_scaled
    except Exception:
        pass

    # the index is really the values actually the FPS_timestamp column.
    # x -> FPS timestamps
    # y -> FPS value at that timestamp
    # x = np.asarray(df.index)
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

    plotters = dict()
    if args.export_fps:
        plotters["FPS"] = {"figure": plt.figure(1)}
    if args.export_frametime:
        plotters["Frametime"] = {"figure": plt.figure(2)}
    if args.export_combined:
        plotters["Combined"] = {"figure": plt.figure(3)}

    for key, plts in plotters.items():
        plts["figure"].patch.set_alpha(0.0)
        # The inch size actually gets tranlated into the resolution
        # So 19.2 x 10.8 -> 1920x1080
        if args.resolution:
            if args.resolution == "720p":
                plts["figure"].set_size_inches(12.8, 7.2)
            elif args.resolution == "1080p":
                plts["figure"].set_size_inches(19.2, 10.8)
            elif args.resolution == "1440p":
                plts["figure"].set_size_inches(25.6, 14.4)
            elif args.resolution == "4k":
                plts["figure"].set_size_inches(38.4, 21.6)
        else:
            plts["figure"].set_size_inches(19.2, 10.8)

        if args.dpi:
            plts["figure"].dpi = args.dpi
        else:
            plts["figure"].dpi = 100

        plts["ax"] = plts["figure"].subplots()

    # Some FPS values can be 0
    # Frame times are calculated as 1000 / FPS value
    # That means we'd get a division-by-zero error
    # To get around this, we ignore any division-by zero errors
    # The next problem is that the program will put in "inf" and "-inf" as the
    # values, so we have to replace them with 0 so the graph doesn't freak out
    print("Removing inf frame-time values from doing division-by-zero.")
    with np.errstate(divide="ignore", invalid="ignore"):
        y2 = pd.Series(1000 / df["framerate"])
    y2[y2 == np.Inf] = np.nan
    y2[y2 == np.NINF] = np.nan

    y = y.interpolate(method="cubic")
    y2 = y2.interpolate(method="cubic")

    length = len(x)  # Total count of frames
    fps_min = y.min()  # Lowest recorded FPS value
    fps_max = y.max()  # Highest recorded FPS value
    fps_mean = y.mean()  # Average FPS
    fps_median = y.median()  # Median FPS
    if "FPS" in plotters.keys():
        plotters["FPS"]["Minimum"] = fps_min
        plotters["FPS"]["Maximum"] = fps_max
        plotters["FPS"]["Mean"] = fps_mean
        plotters["FPS"]["Median"] = fps_median

    frametime_min = y2.min()  # Lowest recorded frametime
    frametime_max = y2.max()  # Highest recorded frametime
    frametime_mean = y2.mean()  # Average frametime
    frametime_median = y2.median()  # Median frametime
    if "Frametime" in plotters.keys():
        plotters["Frametime"]["Minimum"] = frametime_min
        plotters["Frametime"]["Maximum"] = frametime_max
        plotters["Frametime"]["Mean"] = frametime_mean
        plotters["Frametime"]["Median"] = frametime_median

    print("# of Frames: {0}".format(length))
    print("Minimum FPS: {0}".format(fps_min))
    print("Maximum FPS: {0}".format(fps_max))
    print("Mean FPS: {0}".format(fps_mean))
    print("Median FPS: {0}".format(fps_median))
    print("Minimum Frametime: {0}ms".format(frametime_min))
    print("Maximum Frametime: {0}ms".format(frametime_max))
    print("Mean Frametime: {0}ms".format(frametime_mean))
    print("Median Frametime: {0}ms".format(frametime_median))

    # This actually plays the animations for each chart we want
    # The program doesn't display the graphs live,
    # the animations are generated in the background.
    fps_interval = float(100 / 6)

    # y_index = pd.Series(y.index)
    # y_val_new = []
    # y_idx_new = []
    # for y_val, y_idx, diff in zip(y, y_index, y_index.diff()):
    #     y_idx_new.append(y_idx)
    #     y_val_new.append(y_val)
    #     for i in range(round(mul)):
    #         for i in range(499):
    #             y_idx_new.append(np.nan)
    #             y_val_new.append(np.nan)

    # y = pd.Series(
    #     data=pd.Series(y_val_new).interpolate(method="cubic"),
    #     index=pd.Series(y_idx_new).interpolate(method="cubic")
    # )
    # x = pd.Series(y.index)
    # length = len(x)


    # Set the range for the Y-axis between 0 and item's max * 1.1
    if "FPS" in plotters.keys():
        plotters["FPS"]["ax"].set_ylim(0, fps_max * 1.1)
    if "Frametime" in plotters.keys():
        plotters["Frametime"]["ax"].set_ylim(0, frametime_max * 1.1)
    if "Combined" in plotters.keys():
        plotters["Combined"]["ax"].set_ylim(0, fps_max * 1.1)

    for key, plts in plotters.items():
        # Set the range for the initial X-axis
        plts["ax"].set_xlim(x.array[0], x.array[60])
        # Remove the X-axis ticks
        plts["ax"].set_xticklabels([])

    # Now we save each individual graph as it's own file.
    # We choose which files are saved based on the user's input in the
    # beginning of the program.

    rem = os.path.basename(my_CSV)
    my_path, my_file = os.path.abspath(my_CSV).split(rem)
    if my_path == "":
        my_path, my_file = os.getcwd().split("fps_2_chart.py")

    # if args.output:
    #     output_new = ".".join(args.output.split(".")[:-1])
    #     if args.export_fps:
    #         plotters["FPS"]["filename"] = "{0}_fps.mov".format(output_new)
    #     if args.export_frametime:
    #         plotters["Frametime"]["filename"] = "{0}_frametime.mov".format(output_new)
    #     if args.export_combined:
    #         plotters["Combined"]["filename"] = "{0}_combined.mov".format(output_new)
    # else:
    #     if args.export_fps:
    #         plotters["FPS"]["filename"] = "{0}anim_fps.mov".format(my_path)
    #     if args.export_frametime:
    #         plotters["Frametime"]["filename"] = "{0}anim_frametime.mov".format(my_path)
    #     if args.export_combined:
    #         plotters["Combined"]["filename"] = "{0}anim_combined.mov".format(my_path)
    output_new = ".".join(args.output.split(".")[:-1])
    if args.export_fps:
        plotters["FPS"]["filename"] = "{0}_fps.mov".format(output_new)
    if args.export_frametime:
        plotters["Frametime"]["filename"] = "{0}_frametime.mov".format(output_new)
    if args.export_combined:
        plotters["Combined"]["filename"] = "{0}_combined.mov".format(output_new)

    line_fps = mpl.lines.Line2D(x, y, color="b")
    line_frametime = mpl.lines.Line2D(x, y2, color="r")

    if args.export_fps:
        plotters["FPS"]["line"] = plotters["FPS"]["ax"].add_line(line_fps)
    if args.export_frametime:
        plotters["Frametime"]["line"] = plotters["Frametime"]["ax"].add_line(
            line_frametime
        )
    if args.export_combined:
        if args.export_fps:
            plotters["Combined"]["line1"] = plotters["FPS"]["line"]
        else:
            plotters["Combined"]["line1"] = plotters["Combined"]["ax"].add_line(
                line_fps
            )
        if args.export_frametime:
            plotters["Combined"]["line2"] = plotters["Frametime"]["line"]
        else:
            plotters["Combined"]["line2"] = plotters["Combined"]["ax"].add_line(
                line_frametime
            )

    animate(plotters, length, x, y, y2, fps_interval, args)


@Gooey(
    program_name="Framerate Graph Generator",
    default_size=(1280, 720),
    advanced=True,
    navigation="TABBED",
    clear_before_run=True,
)
def parse_arguments():
    """Parse input arguments."""

    main_help = "Plot CSV report to to a live video graph."
    parser = GooeyParser(description=main_help, formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "CSV_Report",
        widget="FileChooser",
        gooey_options={
            "default_dir": str(Path(__file__).parent),
            "message": "Input file name",
            "initial_value": "CSV Report",
            "wildcard": "Comma separated file (*.csv)|*.csv|" "All files (*.*)|*.*",
        },
        help="CSV report file.",
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
            "default_file": "graph",
            "initial_value": "graph",
        },
        help=output_help,
    )

    export_fps_help = (
        "Check the box if you want to generate and export the FPS graph.\n"
    )
    parser.add_argument(
        "--fps",
        dest="export_fps",
        action="store_true",
        help=export_fps_help,
    )

    export_frametime_help = (
        "Check the box if you want to generate and export the Frametime graph.\n"
    )
    parser.add_argument(
        "--frametime",
        dest="export_frametime",
        action="store_true",
        help=export_frametime_help,
    )

    export_combined_help = "Check the box if you want to generate and export the combined FPS + Frametime graph.\n"
    parser.add_argument(
        "--combined",
        dest="export_combined",
        action="store_true",
        help=export_combined_help,
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

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
