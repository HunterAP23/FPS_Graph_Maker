# GameBench_Graph_Maker
Creates animated graphs from GameBench CSV files.

# Installation & Requirements
Requires Python 3.
Install the dependencies using the install_dependencies.bat for Windows,
or alternatively run the following command:
```py
pip install -r requirements.txt
```

# Usage
Run from the command line.

You can either include the name of the CSV file as an initial parameter,
otherwise the program will ask you to enter it manually.

If you include the CSV file as a parameter, you can also enter a number
from 0 - 3 to specify what graphs you want generated:
  0 -> FPS
  1 -> Frametime
  2 -> Combined
  3 -> All three graphs
  If no number is given, assume 3

After the initial creation of the graph(s), the program will then use FFmpeg
to re-encode the video into a QuickTime PNG stream with the background being
transparent.
