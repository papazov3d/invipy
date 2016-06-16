from PyQt5 import QtCore, QtWidgets
import os
import sys
import vtk
import datacontainer as dc
import gui.vtkwidget
import gui.datapanel
import gui.propspanel
import gui.busy
import inout.iocallback


#==================================================================================================
# ProgressBarBusynessIndicator ====================================================================
#==================================================================================================
class ProgressBarBusynessIndicator(gui.busy.BusynessIndicator):
  def __init__(self, parent_window, qt_main_app):
    self.__parent_window = parent_window
    self.__qt_main_app = qt_main_app
    # The label which tells the user about the current task
    self.__label = QtWidgets.QLabel("")
    # The layout
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.__label)
    layout.setAlignment(self.__label, QtCore.Qt.AlignCenter)
    # The window to be shown
    self.__dialog = QtWidgets.QFrame(self.__parent_window, QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)
    self.__dialog.setLayout(layout)


  def set_status_is_busy(self, task_description):
    """Inherited"""
    self.__label.setText(task_description)

    # Compute the shape of this window:
    # First, get the shape of the parent
    parent_rect = self.__parent_window.geometry()
    # Compute the width and height of this window
    width_frac = 0.5
    width = width_frac*parent_rect.width()
    height = 60
    # Compute the left and top coordinates of this window
    left = parent_rect.left() + 0.5*(1.0 - width_frac)*parent_rect.width()
    top = parent_rect.top() + 0.5*parent_rect.height() - 0.5*height

    self.__qt_main_app.processEvents()
    self.__dialog.setGeometry(left, top, width, height)
    self.__dialog.show()
    self.__qt_main_app.processEvents()


  def set_status_is_done(self):
    """Inherited"""
    self.__dialog.close()


#==================================================================================================
# FileLoadProgressBar =============================================================================
#==================================================================================================
class FileLoadProgressBar(inout.iocallback.FileLoadCallback):
  def __init__(self, parent_window, qt_main_app):
    self.__parent_window = parent_window
    self.__qt_main_app = qt_main_app
    
    # The guy who indicates the progress
    self.__progress_bar = QtWidgets.QProgressBar()
    # The layout
    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(QtWidgets.QLabel("loading files:"))
    layout.addWidget(self.__progress_bar)
    # Thw window to be shown
    self.__dialog = QtWidgets.QFrame(self.__parent_window, QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)
    self.__dialog.setLayout(layout)


  def init_loading(self, num_of_files_to_load):
    """Inherited from parent class."""
    self.__progress_bar.setRange(0, num_of_files_to_load)

    # Compute the shape of this window:
    # First, get the shape of the parent window
    parent_rect = self.__parent_window.geometry()
    # Compute the width and height of this window
    width_frac = 0.6
    width = width_frac*parent_rect.width()
    height = 60
    # Compute the left and top coordinates of this window
    left = parent_rect.left() + 0.5*(1.0 - width_frac)*parent_rect.width()
    top = parent_rect.top() + 0.5*parent_rect.height() - 0.5*height

    self.__qt_main_app.processEvents()
    self.__dialog.setGeometry(left, top, width, height)
    self.__dialog.show()
    self.__qt_main_app.processEvents()


  def file_loaded(self, num_of_loaded_files):
    """Inherited from parent class."""
    self.__progress_bar.setValue(num_of_loaded_files)
    self.__dialog.repaint()


  def loading_done(self):
    """Inherited from parent class."""
    self.__dialog.close()


#==================================================================================================
# MainWindow ======================================================================================
#==================================================================================================
class MainWindow(QtWidgets.QMainWindow):
  def __init__(self, data_container, qt_main_app):
    QtWidgets.QMainWindow.__init__(self)

    # Save the input arguments
    self.__data_container = data_container
    self.__qt_main_app = qt_main_app

    # Setup the position and size of the main window
    desktop_widget = QtWidgets.QDesktopWidget()
    rect = desktop_widget.availableGeometry(desktop_widget.primaryScreen())
    #self.setFixedSize(1400, 900)
    self.move(rect.x(), rect.y())

    self.__file_load_progress_bar = FileLoadProgressBar(self, self.__qt_main_app)
    self.__busyness_indicator = ProgressBarBusynessIndicator(self, self.__qt_main_app)

    # Create the GUI elements
    self.__add_menus()
    self.__setup_main_frame()

    # Start the main loop
    self.vtk_widget.interactor.Initialize()
    self.showMaximized()


  def __add_menus(self):
    # Load file(s)    
    load_files_action = QtWidgets.QAction('Load file(s)', self)
    load_files_action.setShortcut('Ctrl+L')
    load_files_action.triggered.connect(self.__on_load_files)
    # Load folder
    load_folder_action = QtWidgets.QAction('Load folder', self)
    load_folder_action.setShortcut('Ctrl+I')
    load_folder_action.triggered.connect(self.__on_load_folder)
    # Open test file
    #open_test_file_action = QtWidgets.QAction('Open test file', self)
    #open_test_file_action.setShortcut('Ctrl+O')
    #open_test_file_action.triggered.connect(self.__on_open_test_file)
    # Quit
    quit_action = QtWidgets.QAction('Quit', self)
    quit_action.setShortcut('Ctrl+Q')
    quit_action.triggered.connect(QtWidgets.qApp.quit)

    file_menu = self.menuBar().addMenu(r"&FILE")
    file_menu.addAction(load_files_action)
    file_menu.addAction(load_folder_action)
    #file_menu.addAction(open_test_file_action)
    file_menu.addSeparator()
    file_menu.addAction(quit_action)


  def __setup_main_frame(self):
    # Create the 3D rendering viewport
    vtk_frame = QtWidgets.QFrame()
    self.vtk_widget = gui.vtkwidget.VtkWidget(self.__data_container, vtk_frame, self.__busyness_indicator)
    vtk_frame_layout = QtWidgets.QVBoxLayout()
    vtk_frame_layout.addWidget(self.vtk_widget.widget)
    vtk_frame.setLayout(vtk_frame_layout)
    self.setCentralWidget(vtk_frame)

    # Add the dock which shows the list of the loaded data (on the left in the main window)
    self.data_panel = gui.datapanel.DataPanel(self.__data_container)
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.data_panel.dock_widget)

    # Add the dock which shows the properties of the selected object (on the right in the main window)
    self.props_panel = gui.propspanel.PropsPanel(self.__data_container)
    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.props_panel.dock_widget)


  def __on_open_test_file(self):
    file_name = list()
    file_name.append(r"C:\Users\papazov\Google Drive\research\data\my_data\annulus_1.obj")
    # Let the data_container load the files. The data_container will notify its observers that new data was loaded.
    self.__data_container.load_files(file_name, self.__file_load_progress_bar)


  def __on_load_files(self):
    default_folder = r"C:\Users\papazov\Google Drive\research\data\models" # Windows
    #default_folder = r"/local/data/zbrain/masks/remeshed/15_Percent_Size"

    # Let the user select the files (file_names[0] will be the list with the file names)
    file_names = QtWidgets.QFileDialog.getOpenFileNames(self, "Load file(s)", default_folder, r"All Files (*.*)")

    # Let the data_container load the files. The data_container will notify its observers that new data was loaded.
    self.__data_container.load_files(file_names[0], self.__file_load_progress_bar)


  def __on_load_folder(self):
    default_folder = r"C:\Users\papazov\Google Drive\research\data\models" # Windows
    #default_folder = r"/local/data/zbrain/masks/remeshed/15_Percent_Size"
  
    folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Load all files from a folder", default_folder)
    # Make sure we got an existing directory
    if not os.path.isdir(folder_name):
      return

    full_file_names = list()

    # Get the *full* file names
    for file_name in os.listdir(folder_name):
      full_file_names.append(folder_name + "/" + file_name) # works on Windows too

    # Let the data_container load the files. The data_container will notify its observers that new data was loaded.
    self.__data_container.load_files(full_file_names, self.__file_load_progress_bar)


#==================================================================================================
# The main function ===============================================================================
#==================================================================================================
if __name__ == "__main__":
  data_container = dc.DataContainer()
  app = QtWidgets.QApplication(sys.argv)
  window = MainWindow(data_container, app)
  sys.exit(app.exec_())
