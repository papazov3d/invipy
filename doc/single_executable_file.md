# Bundle everything to a single executble file

This is a short version of this tutorial: https://mborgerson.com/creating-an-executable-from-a-python-script

* Open a command line tool and type in `pip install pyinstaller` (put `sudo` in front if you need to).
* Build the executable: `pyinstaller --onefile --windowed invipy.py`. This creates a **dist** folder which contais the executable (it also generates a couple of other folders).

Usually, I call `pyinstaller` from a folder different than the one which contains the python source in order not to get all the stuff in the source code folder.
