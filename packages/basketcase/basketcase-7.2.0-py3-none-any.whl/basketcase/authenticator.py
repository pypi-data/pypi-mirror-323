import typing
import logging
from .models import Session

if typing.TYPE_CHECKING:
    import requests
    from . import storage


class Authenticator:
    """
    Session manager for BasketCase.
    """

    def __init__(
            self,
            http_client: 'requests.Session',
            storage_manager: 'storage.Storage'
    ):
        self.http_client = http_client
        self.storage = storage_manager
        self.logger = logging.getLogger(__name__)

    def load_session(self, session_id: int):
        session = self.storage.get_one_by_id(session_id)

        if not session:
            raise RuntimeError('Session not found')

        self.http_client.cookies.set('sessionid', session.cookie_id)

    def load_default(self):
        """Load the default session, if one exists"""

        sessions = self.storage.get_all()

        if len(sessions) == 1:
            # A single session is treated as the default
            self.logger.debug(f'There is only one session, so it will be loaded: {sessions[0].rowid}')
            self.http_client.cookies.set('sessionid', sessions[0].cookie_id)
        else:
            self.logger.debug('Multiple sessions exist.')
            for session in sessions:
                if not session.is_default:
                    continue

                self.logger.debug(f'Loading session: {session.rowid}')
                self.http_client.cookies.set('sessionid', session.cookie_id)

    def get_sessions(self) -> list[Session]:
        sessions = list()

        for session in self.storage.get_all():
            description = session.first_used

            if session.description:
                description = session.description

            if session.is_default:
                description += ' (default)'

            session.description = description
            sessions.append(session)

        return sessions

    def set_default_session(self, session_id: int):
        session = self.storage.get_one_by_id(session_id)

        if not session:
            raise RuntimeError('Session not found')

        if session.is_default:
            raise RuntimeError('Session is already default')

        session.is_default = 1
        self.storage.update(session)

    def unset_default_session(self):
        self.storage.reset_default()

    def forget_session(self, session_id: int):
        session = self.storage.get_one_by_id(session_id)

        if not session:
            raise RuntimeError('Session not found')

        self.storage.delete(session)

    def new_session(self, session: Session):
        session_id = self.storage.insert(session)
        return session_id
