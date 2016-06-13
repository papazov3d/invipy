Invipy is written in Python3 and uses PyQt5 and VTK.

# Install and Run

In the following, we describe how to install and run invipy on Windows and Linux.

## Windows

We use Windows 8, 64 bit.

* **Install PyQt5.** Open a command prompt (eventually as admin) and run `pip install PyQt5`.

* **Install VTK.** Follow [these](doc/install_vtk_win.md) instructions.

* **Set up environment variables.** We assume that VTK is installed in **C:\Program Files\VTK\7.0.0**.
  * Add **C:\Program Files\VTK\7.0.0\bin** to the **Path** environment variable.
  * Add **C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages\vtk;C:\Program Files\VTK\7.0.0\lib\python3.5\site-packages** to the **PYTHONPATH** environment variable (create one if it does not exist).

* **Run invipy.** Checkout this repository or download the code from here. Open a command prompt and go to the directory containing **main.py**. Run `python main.py`.

*** Linux ***

Adjust some environment variables (for cshell in Linux):
setenv LD_LIBRARY_PATH /local/usr/vtk7/lib
setenv PYTHONPATH /local/usr/vtk7/lib/python2.7/site-packages:/local/usr/vtk7/lib/python2.7/site-packages/vtk


*** Windows ***

Add to Path variable (this is where the VTK DLLs are located):
C:\Program Files\VTK\7.0.0-no-qt\bin

Add to PYTHONPATH variable:
C:\Program Files\VTK\7.0.0-no-qt\lib\python3.5\site-packages\vtk;C:\Program Files\VTK\7.0.0-no-qt\lib\python3.5\site-packages
