import vtk

class VtkVolumeModel:
  def __init__(self, name, image_data):
    if not isinstance(image_data, vtk.vtkImageData):
      raise TypeError("input has to be vtkImageData")

    self.name = name

    # Create transfer mapping scalar value to opacity.
    opacity_function = vtk.vtkPiecewiseFunction()
    opacity_function.AddPoint(0,   0.0)
    opacity_function.AddPoint(127, 0.0)
    opacity_function.AddPoint(128, 0.2)
    opacity_function.AddPoint(255, 0.2)
    
    # Create transfer mapping scalar value to color.
    color_function = vtk.vtkColorTransferFunction()
    color_function.SetColorSpaceToHSV()
    color_function.AddHSVPoint(0,   0.0, 0.0, 0.0)
    color_function.AddHSVPoint(127, 0.0, 0.0, 0.0)
    color_function.AddHSVPoint(128, 0.0, 0.0, 1.0)
    color_function.AddHSVPoint(255, 0.0, 0.0, 1.0)
    
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_function)
    volume_property.SetScalarOpacity(opacity_function)
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()
    
    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputData(image_data)
    
    self.volume = vtk.vtkVolume()
    self.volume.SetMapper(volume_mapper)
    self.volume.SetProperty(volume_property)


  @property
  def volume(self):
    return self.volume


  @property
  def prop_3d(self):
    return self.volume
