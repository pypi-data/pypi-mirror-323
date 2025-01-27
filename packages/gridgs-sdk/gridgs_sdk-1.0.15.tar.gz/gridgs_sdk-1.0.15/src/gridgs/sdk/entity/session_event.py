from .session import Session, session_from_dict


class SessionEvent:
    EVENT_CREATE = 'created'
    EVENT_UPDATE = 'updated'
    EVENT_REMOVE = 'removed'

    def __init__(self, type: str, session: Session):
        self.__type = type
        self.__session = session

    @property
    def type(self) -> str:
        return self.__type

    @property
    def session(self) -> Session:
        return self.__session


def session_event_from_dict(obj: dict) -> SessionEvent:
    return SessionEvent(type=obj['type'], session=session_from_dict(obj['entity']))
