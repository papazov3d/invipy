import abc

#==================================================================================================
# FileLoadCallback ================================================================================
#==================================================================================================
class FileLoadCallback:
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def init_loading(self, num_of_files_to_load):
    """This method is called when the loader has counted the number of files to be loaded."""
    pass
  
  @abc.abstractmethod
  def file_loaded(self, num_of_loaded_files):
    """This method is called when a new file was loaded. 'num_of_loaded_files' is the number of loaded files. For example,
    when the method is called with num_of_loaded_files = 2 this means that two files are already loaded."""
    pass
  
  @abc.abstractmethod
  def loading_done(self):
    """This method is called when the loading is finished."""
    pass
