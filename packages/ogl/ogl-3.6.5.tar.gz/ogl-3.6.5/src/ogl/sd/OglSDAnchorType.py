from enum import Enum


class OglSDAnchorType(Enum):

    SourceTime      = 'SourceTime'
    DestinationTime = 'DestinationTime'
    NOT_SET         = 'Not Set'

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()
