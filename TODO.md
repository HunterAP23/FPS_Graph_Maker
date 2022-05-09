# FPS_Graph_Maker
### Workflow
1. Develop application to utilize the `gooey` library for GUI
2. Manage application dependencies with `poetry`
3. Lint code with `black` and `isort` libraries
4. Format and check for errors in code with `flake8`
5. Check if minimum support Python version changed with `vermin`
6. Compile code with `cython`
7. Build application into singular executable with embedded Python runtime with `pyinstaller`
8. Use `pre-commit` CI to run through steps 3 to 7 before a commit is sent out
9. Use GitHub Actions to run through steps 3 to 7 for each os (Windows, Linux, and MacOS)
10. Use GitHub Actions to create a new release if a push or pull request is made onto the main branch.


### In Progress

- [ ] Update GitHub Actions  
  - [ ] Add `venv` installation step  
    - [ ] Create virtual environment with `python -m venv --upgrade-deps .venv`
  - [ ] Add Cython compilation step  
    - [ ] Check if file `src/setup.py` exists - if yes then compile, else skip this job  
    - [ ] Compile with `python src/setup.py build_ext --inplace`  
  - [ ] Update pyinstaller steps to include compiled code  
    - [ ] Check for and include compiled code  
      - [ ] `*.pyd` for Windows  
      - [ ] `*.so` for Linux and MacOS  
    - [ ] Check for and include related libraries (such as `Gooey` and `wxPython`)  
  - [ ] Add support for Pypy builds  
    - [ ] Add Cython compile steps  
    - [ ] Add Pyinstaller build steps  
    - [ ] Add release steps  
  - [ ] Add support for Anaconda builds  
    - [ ] Add Cython compile steps  
    - [ ] Add Pyinstaller build steps  
    - [ ] Add release steps  
- [ ] Migrate off of `pipenv` and onto `poetry`

### Done ✓
- [x] Add Cython Compilation  
  - Build app with `python .\src\setup.py build_ext --inplace`  
  - Cython version of app is run by moving the compiled `FPS_Graph_Maker.cp39-win_amd64` file (be it `.so` or `.pyd`) into the `src` folder, then running `python src/main.py`  
  - The `fps_2_chart.pyx` file can still be run natively without cython with `python src/fps_2_chart.py`