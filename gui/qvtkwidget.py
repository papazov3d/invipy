from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QEvent
from PyQt5 import QtOpenGL
import vtk

class QVTKWidget(QtOpenGL.QGLWidget):
    # Map between VTK and Qt cursors.
    _CURSOR_MAP = {
        0:  Qt.ArrowCursor,          # VTK_CURSOR_DEFAULT
        1:  Qt.ArrowCursor,          # VTK_CURSOR_ARROW
        2:  Qt.SizeBDiagCursor,      # VTK_CURSOR_SIZENE
        3:  Qt.SizeFDiagCursor,      # VTK_CURSOR_SIZENWSE
        4:  Qt.SizeBDiagCursor,      # VTK_CURSOR_SIZESW
        5:  Qt.SizeFDiagCursor,      # VTK_CURSOR_SIZESE
        6:  Qt.SizeVerCursor,        # VTK_CURSOR_SIZENS
        7:  Qt.SizeHorCursor,        # VTK_CURSOR_SIZEWE
        8:  Qt.SizeAllCursor,        # VTK_CURSOR_SIZEALL
        9:  Qt.PointingHandCursor,   # VTK_CURSOR_HAND
        10: Qt.CrossCursor,          # VTK_CURSOR_CROSSHAIR
    }

    def __init__(self, parent=None, wflags=Qt.WindowFlags()):
        # the current button
        self._ActiveButton = Qt.NoButton

        # private attributes
        self.__saveX = 0
        self.__saveY = 0
        self.__saveModifiers = Qt.NoModifier
        self.__saveButtons = Qt.NoButton

        # create qt-level widget
        glFormat = QtOpenGL.QGLFormat()
        glFormat.setAlpha(True)
        QtOpenGL.QGLWidget.__init__(self,glFormat,parent,None)

        # Create a wender window
        self._RenderWindow = vtk.vtkRenderWindow()
        self._RenderWindow.SetAlphaBitPlanes(1)
        self._RenderWindow.SetMultiSamples(0)

        # Create a renderer
        self._Renderer = vtk.vtkRenderer()
        self._Renderer.SetUseDepthPeeling(1)
        #self._Renderer.SetMaximumNumberOfPeels(100)
        #self._Renderer.SetOcclusionRatio(0.0)
        self._RenderWindow.AddRenderer(self._Renderer)

        WId = self.winId()

        # Python2
        if type(WId).__name__ == 'PyCObject':
            from ctypes import pythonapi, c_void_p, py_object

            pythonapi.PyCObject_AsVoidPtr.restype  = c_void_p
            pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]

            WId = pythonapi.PyCObject_AsVoidPtr(WId)

        # Python3
        elif type(WId).__name__ == 'PyCapsule':
            from ctypes import pythonapi, c_void_p, py_object, c_char_p

            pythonapi.PyCapsule_GetName.restype = c_char_p
            pythonapi.PyCapsule_GetName.argtypes = [py_object]

            name = pythonapi.PyCapsule_GetName(WId)

            pythonapi.PyCapsule_GetPointer.restype  = c_void_p
            pythonapi.PyCapsule_GetPointer.argtypes = [py_object, c_char_p]

            WId = pythonapi.PyCapsule_GetPointer(WId, name)

        self._RenderWindow.SetWindowInfo(str(int(WId)))

        self._Iren = vtk.vtkGenericRenderWindowInteractor()
        self._Iren.SetRenderWindow(self._RenderWindow)

        # do all the necessary qt setup
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_PaintOnScreen)
        self.setMouseTracking(True) # get all mouse events
        self.setFocusPolicy(Qt.WheelFocus)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self._Timer = QTimer(self)
        self._Timer.timeout.connect(self.TimerEvent)

        self._Iren.AddObserver('CreateTimerEvent', self.CreateTimer)
        self._Iren.AddObserver('DestroyTimerEvent', self.DestroyTimer)
        self._Iren.GetRenderWindow().AddObserver('CursorChangedEvent',
                                                 self.CursorChangedEvent)

        #Create a hidden child widget and connect its destroyed signal to its
        #parent ``Finalize`` slot. The hidden children will be destroyed before
        #its parent thus allowing cleanup of VTK elements.
        self._hidden = QWidget(self)
        self._hidden.hide()
        self._hidden.destroyed.connect(self.Finalize)


    @property
    def Renderer(self):
      return self._Renderer


    @property
    def RenderWindow(self):
      return self._RenderWindow


    @property
    def Interactor(self):
      return self._Iren
    

    def __getattr__(self, attr):
        """Makes the object behave like a vtkGenericRenderWindowInteractor"""
        if attr == '__vtk__':
            return lambda t=self._Iren: t
        elif hasattr(self._Iren, attr):
            return getattr(self._Iren, attr)
        else:
            raise AttributeError(self.__class__.__name__ +
                  " has no attribute named " + attr)

    def Finalize(self):
        '''
        Call internal cleanup method on VTK objects
        '''
        self._RenderWindow.Finalize()

    def CreateTimer(self, obj, evt):
        self._Timer.start(10)

    def DestroyTimer(self, obj, evt):
        self._Timer.stop()
        return 1

    def TimerEvent(self):
        self._Iren.TimerEvent()

    def CursorChangedEvent(self, obj, evt):
        """Called when the CursorChangedEvent fires on the render window."""
        # This indirection is needed since when the event fires, the current
        # cursor is not yet set so we defer this by which time the current
        # cursor should have been set.
        QTimer.singleShot(0, self.ShowCursor)

    def HideCursor(self):
        """Hides the cursor."""
        self.setCursor(Qt.BlankCursor)

    def ShowCursor(self):
        """Shows the cursor."""
        vtk_cursor = self._Iren.GetRenderWindow().GetCurrentCursor()
        qt_cursor = self._CURSOR_MAP.get(vtk_cursor, Qt.ArrowCursor)
        self.setCursor(qt_cursor)

    def closeEvent(self, evt):
        self.Finalize()

    def sizeHint(self):
        return QSize(400, 400)

    def paintEngine(self):
        return None

    def paintEvent(self, ev):
        self._Iren.Render()

    def resizeEvent(self, ev):
        w = self.width()
        h = self.height()
        vtk.vtkRenderWindow.SetSize(self._RenderWindow, w, h)
        self._Iren.SetSize(w, h)
        self._Iren.ConfigureEvent()
        self.update()

    def _GetCtrlShift(self, ev):
        ctrl = shift = False

        if hasattr(ev, 'modifiers'):
            if ev.modifiers() & Qt.ShiftModifier:
                shift = True
            if ev.modifiers() & Qt.ControlModifier:
                ctrl = True
        else:
            if self.__saveModifiers & Qt.ShiftModifier:
                shift = True
            if self.__saveModifiers & Qt.ControlModifier:
                ctrl = True

        return ctrl, shift

    def enterEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.EnterEvent()

    def leaveEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.LeaveEvent()

    def mousePressEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        repeat = 0
        if ev.type() == QEvent.MouseButtonDblClick:
            repeat = 1
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), repeat, None)

        self._ActiveButton = ev.button()

        if self._ActiveButton == Qt.LeftButton:
            self._Iren.LeftButtonPressEvent()
        elif self._ActiveButton == Qt.RightButton:
            self._Iren.RightButtonPressEvent()
        elif self._ActiveButton == Qt.MidButton:
            self._Iren.MiddleButtonPressEvent()

    def mouseReleaseEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), 0, None)

        if self._ActiveButton == Qt.LeftButton:
            self._Iren.LeftButtonReleaseEvent()
        elif self._ActiveButton == Qt.RightButton:
            self._Iren.RightButtonReleaseEvent()
        elif self._ActiveButton == Qt.MidButton:
            self._Iren.MiddleButtonReleaseEvent()

    def mouseMoveEvent(self, ev):
        self.__saveModifiers = ev.modifiers()
        self.__saveButtons = ev.buttons()
        self.__saveX = ev.x()
        self.__saveY = ev.y()

        ctrl, shift = self._GetCtrlShift(ev)
        self._Iren.SetEventInformationFlipY(ev.x(), ev.y(),
                                            ctrl, shift, chr(0), 0, None)
        self._Iren.MouseMoveEvent()

    def keyPressEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        if ev.key() < 256:
            key = str(ev.text())
        else:
            key = chr(0)

        keySym = _qt_key_to_key_sym(ev.key())
        if shift and len(keySym) == 1 and keySym.isalpha():
            keySym = keySym.upper()

        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, key, 0, keySym)
        self._Iren.KeyPressEvent()
        self._Iren.CharEvent()

    def keyReleaseEvent(self, ev):
        ctrl, shift = self._GetCtrlShift(ev)
        if ev.key() < 256:
            key = chr(ev.key())
        else:
            key = chr(0)

        self._Iren.SetEventInformationFlipY(self.__saveX, self.__saveY,
                                            ctrl, shift, key, 0, None)
        self._Iren.KeyReleaseEvent()

    def wheelEvent(self, event):
        if event.angleDelta().y() >= 0:
            self._Iren.MouseWheelForwardEvent()
        else:
            self._Iren.MouseWheelBackwardEvent()

    def GetRenderWindow(self):
        return self._RenderWindow

    def Render(self):
        self.update()


_keysyms = {
    Qt.Key_Backspace: 'BackSpace',
    Qt.Key_Tab: 'Tab',
    Qt.Key_Backtab: 'Tab',
    # Qt.Key_Clear : 'Clear',
    Qt.Key_Return: 'Return',
    Qt.Key_Enter: 'Return',
    Qt.Key_Shift: 'Shift_L',
    Qt.Key_Control: 'Control_L',
    Qt.Key_Alt: 'Alt_L',
    Qt.Key_Pause: 'Pause',
    Qt.Key_CapsLock: 'Caps_Lock',
    Qt.Key_Escape: 'Escape',
    Qt.Key_Space: 'space',
    # Qt.Key_Prior : 'Prior',
    # Qt.Key_Next : 'Next',
    Qt.Key_End: 'End',
    Qt.Key_Home: 'Home',
    Qt.Key_Left: 'Left',
    Qt.Key_Up: 'Up',
    Qt.Key_Right: 'Right',
    Qt.Key_Down: 'Down',
    Qt.Key_SysReq: 'Snapshot',
    Qt.Key_Insert: 'Insert',
    Qt.Key_Delete: 'Delete',
    Qt.Key_Help: 'Help',
    Qt.Key_0: '0',
    Qt.Key_1: '1',
    Qt.Key_2: '2',
    Qt.Key_3: '3',
    Qt.Key_4: '4',
    Qt.Key_5: '5',
    Qt.Key_6: '6',
    Qt.Key_7: '7',
    Qt.Key_8: '8',
    Qt.Key_9: '9',
    Qt.Key_A: 'a',
    Qt.Key_B: 'b',
    Qt.Key_C: 'c',
    Qt.Key_D: 'd',
    Qt.Key_E: 'e',
    Qt.Key_F: 'f',
    Qt.Key_G: 'g',
    Qt.Key_H: 'h',
    Qt.Key_I: 'i',
    Qt.Key_J: 'j',
    Qt.Key_K: 'k',
    Qt.Key_L: 'l',
    Qt.Key_M: 'm',
    Qt.Key_N: 'n',
    Qt.Key_O: 'o',
    Qt.Key_P: 'p',
    Qt.Key_Q: 'q',
    Qt.Key_R: 'r',
    Qt.Key_S: 's',
    Qt.Key_T: 't',
    Qt.Key_U: 'u',
    Qt.Key_V: 'v',
    Qt.Key_W: 'w',
    Qt.Key_X: 'x',
    Qt.Key_Y: 'y',
    Qt.Key_Z: 'z',
    Qt.Key_Asterisk: 'asterisk',
    Qt.Key_Plus: 'plus',
    Qt.Key_Minus: 'minus',
    Qt.Key_Period: 'period',
    Qt.Key_Slash: 'slash',
    Qt.Key_F1: 'F1',
    Qt.Key_F2: 'F2',
    Qt.Key_F3: 'F3',
    Qt.Key_F4: 'F4',
    Qt.Key_F5: 'F5',
    Qt.Key_F6: 'F6',
    Qt.Key_F7: 'F7',
    Qt.Key_F8: 'F8',
    Qt.Key_F9: 'F9',
    Qt.Key_F10: 'F10',
    Qt.Key_F11: 'F11',
    Qt.Key_F12: 'F12',
    Qt.Key_F13: 'F13',
    Qt.Key_F14: 'F14',
    Qt.Key_F15: 'F15',
    Qt.Key_F16: 'F16',
    Qt.Key_F17: 'F17',
    Qt.Key_F18: 'F18',
    Qt.Key_F19: 'F19',
    Qt.Key_F20: 'F20',
    Qt.Key_F21: 'F21',
    Qt.Key_F22: 'F22',
    Qt.Key_F23: 'F23',
    Qt.Key_F24: 'F24',
    Qt.Key_NumLock: 'Num_Lock',
    Qt.Key_ScrollLock: 'Scroll_Lock',
    }

def _qt_key_to_key_sym(key):
    """ Convert a Qt key into a vtk keysym.

    This is essentially copied from the c++ implementation in
    GUISupport/Qt/QVTKInteractorAdapter.cxx.
    """

    if key not in _keysyms:
        return None

    return _keysyms[key]
