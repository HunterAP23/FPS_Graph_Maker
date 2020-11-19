# GameBench_Graph_Maker
Creates animated graphs from GameBench CSV files.

# Installation & Requirements
Requires Python 3.
Install the dependencies using the install_dependencies.bat for Windows,
or alternatively run the following command:
```
pip install -r requirements.txt
```
or:
```
python -m pip install -r requirements.txt
```

If you use the `pipenv` module, you can create a virtual environment with the
following command:
```
pipenv update
```
or:
```
python -m pipenv update
```

# Usage
You can use the help command to get a list of available options with the
following command:
```
python fps_2_chart.py -h
```

Here is what that output looks like:
```
usage: fps_2_chart.py [-h] [-o OUTPUT] [-i {linear,cubic}] [-t {default,fps,frametime,both}] [-r {720p,1080p,1440p,4k}] [-d DPI] [-w]
                      GameBench_Report

Plot GameBench report to to a live video graph.

positional arguments:
  GameBench_Report      GameBench CSV report file.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename (Default: "graph").
                        Depending on what you generate, the output files will have "_fps" or "_frametime" or "_both" appended to them
                        (IE: "graph" would generate "graph_fps.mov").
  -i {linear,cubic}, --interp {linear,cubic}
                        Choose the interpolation method for the FPS/FrametTime values.
                        * "linear" uses linear interpolation - a straight line will be generated between each point.
                        * "cubic" uses cubic interpolation. This tries to create smooth curves between points.
  -t {default,fps,frametime,both}, --type {default,fps,frametime,both}
                        Choose the what output video graph files to generate.
                        * "default" will generate all three graphs - FPS, Frame Time, and FPS + Frame Time combined.
                        * "fps" will only generate the FPS video graph.
                        * "frametime" will only generate the Frame Time video graph.
                        * "both" will only generate the combined FPS + Frame Time video graph.
  -r {720p,1080p,1440p,4k}, --resolution {720p,1080p,1440p,4k}
                        Choose the resolution for the graph video (Default is 1080p).
                        Note that higher values will mean drastically larger files and take substantially longer to encode.
  -d DPI, --dpi DPI     Choose the DPI value for the graph image and video (Default is 100).
                        The DPI value must be greater than or equal to 2.
                        Note that higher values will mean drastically larger files and take substantially longer to encode.
  -w, --overwrite       Use this flag to overwrite any existing files that have the same output name as the one set by the "-o" argument.
```
