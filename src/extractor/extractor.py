from aiohttp import ClientSession, ClientResponse
import datetime
import enum
from typing import Optional, Tuple
from backoff import expo, on_predicate
from config import (
    LIVETEX_BASE_URL, LOGIN_URL, EMPLOYEES_URL,
    DIALOGS_URL, DIALOG_INFO,
    MAX_LIMIT, BACKOFF_MAX_TIME,
)


class EventType(enum.Enum):
    TEXT = 'TextMessage'


class EventCreator(enum.Enum):
    EMPLOYEE = 'Employee'
    CLIENT = 'Discourser'


class LivetexExtractor:
    def __init__(self, username: str, password: str,
                 start: datetime.datetime, end: datetime.datetime,
                 session: ClientSession) -> None:
        self.username = username
        self.password = password
        self.employees = []
        self._id = None
        self._token = None
        self._session = session
        self._start = start
        self._end = end

    async def get_dialogs_short(self, limit: int = MAX_LIMIT):
        params = {
            'startTime': int(1000 * self._start.timestamp()),
            'endTime': int(1000 * self._end.timestamp()),
            'limit': limit,
        }
        resp = await self._make_request(LIVETEX_BASE_URL + DIALOGS_URL, params)
        data = await resp.json()
        if data['total'] > limit:
            return await self.get_dialogs_short(limit * 2)
        return data['result']

    async def get_dialog_info(self, topic_id: str):
        params = {
            'startTime': int(1000 * self._start.timestamp()),
            'endTime': int(1000 * self._end.timestamp()),
            'topicId': topic_id,
        }
        resp = await self._make_request(LIVETEX_BASE_URL + DIALOG_INFO, params)
        data = await resp.json()
        topic = data['topics'][0]
        messages = []
        for event in topic['events']:
            if event['eventType'] == EventType.TEXT.value:
                author, is_client = self._get_message_author(topic, event)
                messages.append({
                    'dialog_id': topic_id,
                    'text': event['message'],
                    'timestamp': event['ctime'],
                    'author': author,
                    'is_from_client': is_client,
                })
        return messages

    async def login(self, session: ClientSession):
        payload = {'username': self.username, 'password': self.password}
        headers = {'Cookie': 'ng_environment=production-3'}
        async with session.post(LOGIN_URL, headers=headers, data=payload) as resp:
            status = (await resp.json())['status']
            if status != 'ok':
                raise ValueError('Wrong credentials')
            self._id = resp.cookies['id'].value
            self._token = resp.cookies['access_token'].value

    async def get_employees(self, session: ClientSession):
        params = {'include_deleted': 'true'}
        headers = {'Cookie': 'ng_environment=production-3'}
        async with session.get(EMPLOYEES_URL, params=params, headers=headers) as resp:
            self.employees = await resp.json()

    def _get_message_author(self, topic, event) -> Optional[Tuple[str, bool]]:
        creator = event['creator']
        if creator['creatorType'] == EventCreator.EMPLOYEE.value:
            return self._get_employee(creator['userId']), False
        elif creator['creatorType'] == EventCreator.CLIENT.value:
            return topic['discourserName'], True
        return None

    def _get_employee(self, employee_id: str) -> Optional[str]:
        for employee in self.employees:
            if str(employee['id']) == employee_id:
                return ' '.join([employee['last_name'], employee['first_name']])

    @on_predicate(expo, lambda x: x.status != 200, max_time=BACKOFF_MAX_TIME)
    async def _make_request(self, method: str, params) -> ClientResponse:
        headers = {'Access-Token': self._token}
        default_params = {'accountId': self._id}
        default_params.update(params)
        return await self._session.get(method, params=default_params, headers=headers)
