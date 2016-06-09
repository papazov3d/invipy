import abc

class BusynessIndicator:
  __metaclass__ = abc.ABCMeta
  
  @abc.abstractmethod
  def set_status_is_busy(self, task_description):
    """Call to indicate that the process is doing something. 'task_description' should be a
    short string which describes what the process is doing"""
    pass

  @abc.abstractmethod
  def set_status_is_done(self):
    """Call to indicate that the process is done."""
    pass
