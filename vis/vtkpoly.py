import vtk

class VtkPolyModel:
  def __init__(self, file_name, name, poly_data):
    if not isinstance(poly_data, vtk.vtkPolyData):
      raise TypeError("input has to be vtkPolyData")

    self.__file_name = file_name
    self.__name = name
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)
    self.__actor = vtk.vtkActor()
    self.__actor.SetMapper(mapper)
    self.__actor.GetProperty().SetAmbient(0.05)


  def set_transparency(self, value):
    """Sets the transparency of the model (0: non-transparent, i.e, not see-through,
    1: full transparent, i.e., invisible)."""
    self.__actor.GetProperty().SetOpacity(1.0 - value)


  def get_transparency(self):
    """Returns the transparency of the model (0: non-transparent, i.e, not see-through,
    1: full transparent, i.e., invisible)."""
    return 1.0 - self.__actor.GetProperty().GetOpacity()


  def get_diffuse_color(self):
    return self.__actor.GetProperty().GetDiffuseColor()


  def set_diffuse_color(self, r, g, b):
    return self.__actor.GetProperty().SetDiffuseColor(r, g, b)


  def highlight_on(self):
    d = self.get_diffuse_color()
    self.__actor.GetProperty().SetAmbientColor(d[0], d[1], d[2])
    self.__actor.GetProperty().SetAmbient(0.5)


  def highlight_off(self):
    self.__actor.GetProperty().SetAmbient(0.05)


  def toggle_highlight(self):
    self.__actor.GetProperty().SetAmbient(1 - self.__actor.GetProperty().GetAmbient())


  def visibility_on(self):
    self.__actor.VisibilityOn()


  def visibility_off(self):
    self.__actor.VisibilityOff()


  def is_visible(self):
    return self.__actor.GetVisibility() == 1


  def toggle_visibility(self):
    if self.is_visible():
      self.visibility_off()
    else:
      self.visibility_on()


  @property
  def file_name(self):
    return self.__file_name


  @property
  def name(self):
    return self.__name


  @property
  def actor(self):
    return self.__actor


  @property
  def prop_3d(self):
    return self.__actor
