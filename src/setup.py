from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [Extension("FPS_Graph_Maker", ["src/fps_2_chart.py"])]

setup(
    ext_modules=cythonize(
        extensions,
        build_dir="build",
        language_level=3,
    ),
    options={"build": {"build_lib": "package"}},
)
