
from typing import Tuple
from typing import cast

from wx import DC

from miniogl.Shape import Shape
from miniogl.MiniOglUtils import sign
from miniogl.SizerShape import SizerShape

from miniogl.models.RectangleShapeModel import RectangleShapeModel


class RectangleShape(Shape):
    """
    A rectangle shape.
    """
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0, parent=None):
        """

        Args:
            x:      Shape's x position
            y:      Shape's y position
            width:  Shape's width
            height: Shape's height
            parent: The shape's parent, if any
        """
        super().__init__(x, y, parent)

        self._width:  int = width   # width and height can be < 0 !!!
        self._height: int = height

        self._drawFrame: bool = True
        self._resizable: bool = True

        self._topLeftSizer:  SizerShape = cast(SizerShape, None)
        self._topRightSizer: SizerShape = cast(SizerShape, None)
        self._botLeftSizer:  SizerShape = cast(SizerShape, None)
        self._botRightSizer: SizerShape = cast(SizerShape, None)

        self._ox: int = 0   # This is done in Shape but Pycharm can't see this in the ShowSizer() code
        # set the model of the shape (MVC pattern)
        self._model: RectangleShapeModel = RectangleShapeModel(self)
        self._model.SetPosition(x=x, y=y)
        self._model.SetSize(width=width, height=height)

    @property
    def selected(self) -> bool:
        """
        Override Shape

        Returns: 'True' if selected 'False' otherwise
        """
        return self._selected

    @selected.setter
    def selected(self, state: bool):
        self._selected = state
        if self._resizable:
            self.ShowSizers(state)

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, state: bool):
        self._resizable = state

    def GetTopLeft(self) -> Tuple[int, int]:
        """
        Get the coordinates of the top left point in diagram coordinates.

        @return (double, double)
        """
        x, y = self.GetPosition()
        x -= self._ox
        y -= self._oy
        width, height = self.GetSize()
        if width < 0:
            x += width
        if height < 0:
            y += height
        return x, y

    def SetTopLeft(self, x, y):
        """
        Set the position of the top left point.

        @param  x
        @param y : new position
        """
        x += self._ox
        y += self._oy
        width, height = self.GetSize()
        if width < 0:
            x -= width
        if height < 0:
            y -= height
        self._x, self._y = x, y

    def Draw(self, dc: DC, withChildren: bool = False):
        """
        Draw the rectangle on the dc.

        Args:
            dc:
            withChildren:

        Returns:

        """
        if self._visible:
            Shape.Draw(self, dc, False)
            if self._drawFrame:
                sx, sy = self.GetPosition()
                sx, sy = sx - self._ox, sy - self._oy
                width, height = self.GetSize()

                dc.DrawRectangle(sx, sy, width, height)
            if withChildren:
                self.DrawChildren(dc)
            if self._topLeftSizer is not None:
                self._topLeftSizer.Draw(dc, False)

    def DrawBorder(self, dc):
        """
        Draw the border of the shape, for fast rendering.
        """
        Shape.DrawBorder(self, dc)
        sx, sy = self.GetPosition()
        sx, sy = sx - self._ox, sy - self._oy
        width, height = self.GetSize()
        dc.DrawRectangle(sx, sy, width, height)

    def SetDrawFrame(self, draw):
        """
        Choose to draw a frame around the rectangle.

        @param bool draw : True to draw the frame
        """
        self._drawFrame = draw

    def Inside(self, x, y) -> bool:
        """
        True if (x, y) is inside the rectangle.

        Args:
            x:
            y:

        Returns:
        """
        # this also works if width and/or height is negative.
        sx, sy = self.GetPosition()
        # take a minimum of 4 pixels for the selection
        width, height = self.GetSize()
        width  = sign(width)  * max(abs(width),  4)
        height = sign(height) * max(abs(height), 4)
        topLeftX: int = sx - self._ox
        topLeftY: int = sy - self._oy

        topXLeftIsInside:  bool  = x >= topLeftX
        topXRightIsInside: bool  = x <= topLeftX + width
        topYLeftIsInside:  bool  = y >= topLeftY
        topYRightIsInside: bool  = y <= topLeftY + height
        if topXLeftIsInside and topXRightIsInside and topYLeftIsInside and topYRightIsInside:
            return True
        else:
            return False

    def GetSize(self) -> Tuple[int, int]:
        """
        Get the size of the rectangle.

        Returns:
            A tuple of width, height
        """
        return self._width, self._height

    def GetHeight(self):
        return self._height

    def Detach(self):
        """
        Detach the shape from its diagram.
        This is the way to delete a shape. All anchor points are also
        removed, and link lines too.
        """
        # do not detach a protected shape
        if self._diagram is not None and not self._protected:
            Shape.Detach(self)
            self.ShowSizers(False)

    def ShowSizers(self, state: bool = True):
        """
        Show the four sizer shapes if state is True.

        @param state
        """
        width, height = self.GetSize()
        if state and not self._topLeftSizer:
            self._topLeftSizer  = SizerShape(-self._ox, -self._oy, self)
            self._topRightSizer = SizerShape(-self._ox + width - 1, self._oy, self)
            self._botLeftSizer  = SizerShape(-self._ox, -self._oy + height - 1, self)
            self._botRightSizer = SizerShape(-self._ox + width - 1, -self._oy + height - 1, self)

            self._diagram.AddShape(self._topLeftSizer)
            self._diagram.AddShape(self._topRightSizer)
            self._diagram.AddShape(self._botLeftSizer)
            self._diagram.AddShape(self._botRightSizer)
        elif not state and self._topLeftSizer is not None:
            self._topLeftSizer.Detach()
            self._topRightSizer.Detach()
            self._botLeftSizer.Detach()
            self._botRightSizer.Detach()

            self._topLeftSizer  = cast(SizerShape, None)
            self._topRightSizer = cast(SizerShape, None)
            self._botLeftSizer  = cast(SizerShape, None)
            self._botRightSizer = cast(SizerShape, None)

    def SetSize(self, width, height):
        """
        Set the size of the rectangle.

        @param  width
        @param height
        """
        self._width, self._height = width, height

        if self.HasDiagramFrame():
            self.UpdateModel()

        for anchor in self._anchors:
            ax, ay = anchor.GetPosition()
            # Reset position to stick the border
            anchor.SetPosition(ax, ay)

    def Resize(self, sizer, x, y):
        """
        Resize the rectangle according to the new position of the sizer.
        Not used to programmatically resize a shape. Use `SetSize` for this.

        Args:
            sizer:
            x:      x position of the sizer
            y:      y position of the sizer

        """
        tlx, tly = self.topLeft
        w, h = self.GetSize()
        sw, sh = sign(w), sign(h)
        w, h = abs(w), abs(h)
        if sizer is self._topLeftSizer:
            nw = sw * (w - x + tlx)
            nh = sh * (h - y + tly)
            self._ox = self._ox * nw // w
            self._oy = self._oy * nh // h
            self.SetSize(nw, nh)
            self.SetTopLeft(x, y)
            self._topRightSizer.SetRelativePosition(nw - 1, 0)
            self._botLeftSizer.SetRelativePosition(0, nh - 1)
            self._botRightSizer.SetRelativePosition(nw - 1, nh - 1)
        elif sizer is self._topRightSizer:
            nw = sw * (x - tlx)
            nh = sh * (tly + h - y)
            self.SetTopLeft(tlx, y)
            self.SetSize(nw + 1, nh)
            self._topRightSizer.SetRelativePosition(nw, 0)
            self._botRightSizer.SetRelativePosition(nw, nh - 1)
            self._botLeftSizer.SetRelativePosition(0, nh - 1)
        elif sizer is self._botLeftSizer:
            nw = sw * (w - x + tlx)
            nh = sh * (y - tly)
            self.SetTopLeft(x, tly)
            self.SetSize(nw, nh + 1)
            self._botLeftSizer.SetRelativePosition(0, nh)
            self._botRightSizer.SetRelativePosition(nw - 1, nh)
            self._topRightSizer.SetRelativePosition(nw - 1, 0)
        elif sizer is self._botRightSizer:
            nw = sw * (x - tlx)
            nh = sh * (y - tly)
            self.SetSize(nw + 1, nh + 1)
            self._botLeftSizer.SetRelativePosition(0, nh)
            self._botRightSizer.SetRelativePosition(nw, nh)
            self._topRightSizer.SetRelativePosition(nw, 0)

    def UpdateFromModel(self):
        """
        Updates the shape position and size from the model in the light of a
        change of state of the diagram frame (here it's only for the zoom)
        """

        #  change the position of the shape from the model
        Shape.UpdateFromModel(self)

        #  get the model size
        width, height = self.model.GetSize()

        #  get the diagram frame ratio between the shape and the model
        ratio = self.diagram.panel.currentZoom

        # set the new size to the shape.
        self._width  = round(width * ratio)
        self._height = round(height * ratio)

    def UpdateModel(self):
        """
        Updates the model when the shape (view) is moved or resized.
        """
        #  change the coordinates of model
        Shape.UpdateModel(self)

        #  get the size of the shape (view)
        width, height = self.GetSize()

        # get the ratio between the model and the shape (view) from
        # the diagram frame where the shape is displayed.
        ratio = self.diagram.panel.currentZoom

        # set the new size to the model.
        self.model.SetSize(round(width//ratio), round(height//ratio))

    def __str__(self) -> str:
        return f'RectangleShape-{self._id}'

    def __repr__(self) -> str:
        return self.__str__()
