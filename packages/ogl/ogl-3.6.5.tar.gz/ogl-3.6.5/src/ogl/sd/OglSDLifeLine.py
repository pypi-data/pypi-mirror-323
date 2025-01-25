
from logging import Logger
from logging import getLogger

from wx import BLACK
from wx import DC
from wx import PENSTYLE_SHORT_DASH
from wx import Pen

from miniogl.LineShape import LineShape

from ogl.sd.OglSDAnchorPoint import OglSDAnchorPoint


class OglSDLifeLine(LineShape):

    def __init__(self, srcAnchor: OglSDAnchorPoint, dstAnchor: OglSDAnchorPoint):

        super().__init__(srcAnchor=srcAnchor, dstAnchor=dstAnchor)

        self._lifeLinePen = Pen(BLACK, width=1, style=PENSTYLE_SHORT_DASH)

        self.oglLifeLineLogger: Logger = getLogger(__name__)

    @property   # type: ignore
    def sourceAnchor(self) -> OglSDAnchorPoint:
        return self._srcAnchor  # type: ignore

    @sourceAnchor.setter
    def sourceAnchor(self, theNewValue: OglSDAnchorPoint):
        self._srcAnchor = theNewValue

    @property   # type: ignore
    def destinationAnchor(self) -> OglSDAnchorPoint:
        return self._dstAnchor  # type: ignore

    @destinationAnchor.setter
    def destinationAnchor(self, theNewValue: OglSDAnchorPoint):
        self._dstAnchor = theNewValue

    def Draw(self, dc: DC, withChildren: bool = True):

        self.pen = self._lifeLinePen
        super().Draw(dc, withChildren)

    def AddAnchor(self, x: int, y: int, anchorType=None):
        """
        Add an anchor point to the shape.
        A line can be linked to it. The anchor point will stay bound to the
        shape and move with it. It is protected against deletion (by default)
        and not movable by itself.

        Args:
            x: position of the new point, relative to the origin of the shape
            y: position of the new point, relative to the origin of the shape
            anchorType:  Not used in this override

        Returns:    the created anchor
        """
        from ogl.sd.OglSDAnchorPoint import OglSDAnchorPoint     # I don't like in module imports but there is a cyclical dependency somewhere

        oglSDAnchorPoint: OglSDAnchorPoint = OglSDAnchorPoint(x, y, self)
        oglSDAnchorPoint.protected = True
        self._anchors.append(oglSDAnchorPoint)
        # if the shape is not yet attached to a diagram, the anchor points
        # will be attached when Attach is called on the shape.
        if self._diagram is not None:
            self._diagram.AddShape(oglSDAnchorPoint)
        return oglSDAnchorPoint

    def __str__(self) -> str:
        return f'OglSDLifeLine-{self._id}'

    def __repr__(self) -> str:
        return self.__str__()
