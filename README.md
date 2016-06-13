Invipy is written in Python3 and uses PyQt5 and VTK.

# Install and Run

In the following, we describe how to install and run invipy on Windows and Linux.

## Windows

We use 64bit Windows 8.

* **Install PyQt5.** Open a command prompt (eventually as admin) and run `pip install PyQt5`.

* **Install VTK.** Follow [these](doc/install_vtk_win.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **C:\Program Files\VTK\7.0.0**.
  * Add **C:\Program Files\VTK\7.0.0\bin** to the **Path** environment variable.
  * Add **C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages\vtk;C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages** to the **PYTHONPATH** environment variable (create one if it does not exist).

* **Run invipy.** Check out this repository or download the code from here. Open a command prompt and go to the directory containing **main.py**. Run `python main.py`.


## Linux

We use 64bit Ubuntu 14.

* **Install PyQt5.** Open a command prompt and run `sudo pip install PyQt5` (no `sudo` if you are using **virtualenv**).

* **Install VTK.** Follow [these](doc/install_vtk_linux.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **/local/usr/vtk7**.
  * Add **/local/usr/vtk7/lib** to the **LD_LIBRARY_PATH** environment variable.
  * Add **/local/usr/vtk7/lib/python3.5/site-packages:/local/usr/vtk7/lib/python3.5/site-packages/vtk** to the **PYTHONPATH** environment variable.

* **Run invipy.** Checkout this repository or download the code from here. Open a command prompt and go to the directory containing **main.py**. Run `python main.py`.
