from .qvtkwidget import QVTKWidget
import vtk
import modelview
from .pick import ModelPicker
import datacontainer as dc
import gui.busy

class VtkWidget(modelview.Observer):
  def __init__(self, data_container, parent_qt_frame, busyness_indicator = None):
    modelview.Observer.__init__(self)

    self.data_container = data_container
    # Make sure that the data container has the right type
    if not isinstance(self.data_container, dc.DataContainer):
      raise TypeError("the data container has the wrong type")
    # Register itself as an observer to the data_container
    self.data_container.add_observer(self)

    self.busyness_indicator = busyness_indicator
    # Make sure 'busyness_indicator' has the right type
    if self.busyness_indicator and not isinstance(self.busyness_indicator, gui.busy.BusynessIndicator):
      print("Warning: input parameter 'busyness_indicator' has the wrong type")
      self.busyness_indicator = None

    # The render window interactor
    self.__vtk_widget = QVTKWidget(parent_qt_frame)
    self.__vtk_widget.Renderer.SetBackground(0.4, 0.41, 0.42)

    # This guy is very important: it handles all the model selection in the 3D view
    self.__model_picker = ModelPicker(self.data_container, self.interactor)

    # We want to see xyz axes in the lower left corner of the window
    lower_left_axes_actor = vtk.vtkAxesActor()
    lower_left_axes_actor.SetXAxisLabelText("X")
    lower_left_axes_actor.SetYAxisLabelText("Y")
    lower_left_axes_actor.SetZAxisLabelText("Z")
    lower_left_axes_actor.SetTotalLength(1.5, 1.5, 1.5)
    self.lower_left_axes_widget = vtk.vtkOrientationMarkerWidget()
    self.lower_left_axes_widget.SetOrientationMarker(lower_left_axes_actor)
    self.lower_left_axes_widget.KeyPressActivationOff()
    self.lower_left_axes_widget.SetInteractor(self.interactor)
    self.lower_left_axes_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
    self.lower_left_axes_widget.SetEnabled(1)
    self.lower_left_axes_widget.InteractiveOff()

    # The slicer for the volume data
    self.volume_widget = vtk.vtkImagePlaneWidget()
    self.volume_widget.SetInteractor(self.interactor)
    self.volume_widget.SetResliceInterpolateToCubic()


  def observable_changed(self, change, data):
    # Decide what to do depending on what changed
    if change == dc.DataContainer.change_is_new_data:
      self.__add_data_items(data)
    elif change == dc.DataContainer.change_is_data_visibility:
      self.update_clipping_range_and_render()
    elif change == dc.DataContainer.change_is_new_selection:
      self.__highlight_models(data)
    elif change == dc.DataContainer.change_is_color or change == dc.DataContainer.change_is_transparency:
      self.render()


  def reset_view(self):
    """Modifies the camera such that all (visible) data items are in the viewing frustum."""
    self.renderer.ResetCamera()
    self.renderer.ResetCameraClippingRange()
    self.interactor.Render()


  def update_clipping_range_and_render(self):
    """Resets the clipping range of the camera and renders the scene"""
    self.renderer.ResetCameraClippingRange()
    self.interactor.Render()


  def render(self):
    """Renders the scene"""
    self.interactor.Render()
    print("used depth peeling: " + str(self.renderer.GetLastRenderingUsedDepthPeeling()))

  @property
  def widget(self):
    return self.__vtk_widget


  @property
  def render_window(self):
    return self.widget.RenderWindow


  @property
  def interactor(self):
    return self.widget.Interactor


  @property
  def renderer(self):
    return self.widget.Renderer


  #def __add_volume(self, name, image_data):
    # VTK can render only one volume at each point in space, that's why we keep only one volume for now
    # Remove all volumes from the renderer
    #for vol in self.volume_models.values():
    #  self.renderer.RemoveViewProp(vol.volume)
    #self.volume_models.clear()
    #try:
    #  volume_model = vis.vtkvol.VtkVolumeModel(image_data)
    #  self.volume_models[name] = volume_model
    #  self.renderer.AddVolume(volume_model.volume)
    #except Exception as e:
    #  print("Error: couldn't add a new volume for " + name + ": " + e.message)
    
    #self.volume_models[name] = vis.vtkvol.VtkVolumeModel(image_data)
    #self.volume_widget.SetInputData(image_data)
    #self.volume_widget.SetPlaneOrientationToZAxes()
    #self.volume_widget.On()
    #return True


#  def __add_poly(self, name, poly_data):
#    try:
#      poly_model = vis.vtkpoly.VtkPolyModel(poly_data)
#      self.poly_models[name] = poly_model
#      self.renderer.AddActor(poly_model.actor)
#    except Exception as e:
#      print("Error: couldn't add the polygonal model " + name + ": " + e.message)
#      return False
#    else:
#      return True


  def __add_data_items(self, data_items):
    # Tell the world we are busy
    if self.busyness_indicator:
      self.busyness_indicator.set_status_is_busy("adding models to 3D renderer ...")
      
    # Add all the data to the renderer
    for data_item in data_items:
      self.renderer.AddViewProp(data_item.prop_3d)
    # Make sure that we see all the new data
    if len(data_items) > 0:
      self.reset_view()
    # We are done
    if self.busyness_indicator:
      self.busyness_indicator.set_status_is_done()      


  def __highlight_models(self, models):
    # First un-highlight all models
    for model in self.data_container.get_models():
      model.highlight_off()
    # Now highligh the ones we want to highlight
    for model in models:
      model.highlight_on()
    # Update the view
    self.render()
