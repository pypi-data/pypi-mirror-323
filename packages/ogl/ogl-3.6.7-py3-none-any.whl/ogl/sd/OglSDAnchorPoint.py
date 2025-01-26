
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import MouseEvent

from miniogl.Shape import Shape
from miniogl.AnchorPoint import AnchorPoint
from miniogl.ShapeEventHandler import ShapeEventHandler

from ogl.sd.OglSDAnchorType import OglSDAnchorType

if TYPE_CHECKING:
    from ogl.sd.OglSDMessage import OglSDMessage


# Make it bigger so we can easily catch message end point moves
SELECTION_ZONE: int = 20


class OglSDAnchorPoint(AnchorPoint, ShapeEventHandler):
    """
    After creation make sure and set the
        oglSDAnchorType
        associatedMessage

    """

    def __init__(self, x: int, y: int, parent: Shape):
        from ogl.sd.OglSDMessage import OglSDMessage

        self._sdApLogger: Logger = getLogger(__name__)

        super().__init__(x=x, y=y, parent=parent)

        self.selectionZone = SELECTION_ZONE

        self._oglSDAnchorType:   OglSDAnchorType = OglSDAnchorType.NOT_SET
        self._associatedMessage: OglSDMessage    = cast(OglSDMessage, None)

    @property
    def oglSDAnchorType(self) -> OglSDAnchorType:
        return self._oglSDAnchorType

    @oglSDAnchorType.setter
    def oglSDAnchorType(self, newValue: OglSDAnchorType):
        self._oglSDAnchorType = newValue

    @property
    def associatedMessage(self):
        return self._associatedMessage

    @associatedMessage.setter
    def associatedMessage(self, newValue: 'OglSDMessage'):
        self._associatedMessage = newValue

    def OnLeftUp(self, event: MouseEvent):
        """
        Need additional behavior to report back new line position to SDInstance
        Report moves from AnchorPoints to PyutSDMessage

        Args:
            event:
        """

        assert self.oglSDAnchorType != OglSDAnchorType.NOT_SET, 'Developer error'
        assert self.associatedMessage is not None,              'Developer Error'

        newTime: int = self.GetPosition()[1]
        self._sdApLogger.debug(f'OnLeftUp: {self.oglSDAnchorType} {newTime} {self.associatedMessage}')

        self.associatedMessage.updateMessageTime(anchorType=self.oglSDAnchorType, newTime=newTime)

    def __str__(self) -> str:
        x, y = self.GetPosition()
        draggable: bool = self._draggable
        return f'OglSDAnchorPoint[({x},{y}) - {draggable=}]'

    def __repr__(self):
        return self.__str__()
