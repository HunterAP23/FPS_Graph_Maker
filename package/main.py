import math
import os
import sys
from argparse import RawTextHelpFormatter
from datetime import datetime as dt
from datetime import timedelta as td
from io import StringIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gooey import Gooey, GooeyParser
from matplotlib import animation

if __name__ == "__main__":
    from FPS_Graph_Maker import parse_arguments, main 
    args = parse_arguments()
    main(args)