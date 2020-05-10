from aiohttp import ClientSession, ClientResponse
import asyncio
import datetime
import enum
from typing import Optional, Tuple, List, Dict, Any
from type_helpers import Employee
from backoff import expo, on_predicate, on_exception
from config import (
    LIVETEX_BASE_URL, LOGIN_URL, EMPLOYEES_URL,
    DIALOGS_URL, DIALOG_INFO,
    MAX_LIMIT, BACKOFF_MAX_TIME,
    MAX_CONCURRENCY_LEVEL,
)


class EventType(enum.Enum):
    TEXT = 'TextMessage'


class EventCreator(enum.Enum):
    EMPLOYEE = 'Employee'
    CLIENT = 'Discourser'


class LivetexExtractor:
    def __init__(self, start: datetime.datetime, end: datetime.datetime,
                 session: ClientSession, concurrency_level: int = MAX_CONCURRENCY_LEVEL) -> None:
        self.employees: List[Employee] = []
        self._id: Optional[str] = None
        self._token: Optional[str] = None
        self._session = session
        self._start = start
        self._end = end
        self._sem = asyncio.Semaphore(concurrency_level)

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
        topic = [topic for topic in data['topics'] if topic['id'] == topic_id][0]
        messages = []
        for event in topic['events']:
            if event['eventType'] == EventType.TEXT.value:
                author, is_client = self._get_message_author(topic, event)
                metrics = topic['topicMetric']
                messages.append({
                    'dialog_id': topic_id,
                    'dialog_start': metrics['openTime'],
                    'dialog_end': metrics['closeTime'],
                    'avg_response_time': metrics['answerTime'],  # Avg response time in ms
                    'reaction_time': metrics['responseTime'],  # Time till first response in ms
                    'duration': metrics['duration'],  # Dialog duration in ms
                    'text': event['message'],
                    'timestamp': event['ctime'],
                    'author': author,
                    'is_from_client': is_client,
                })
        return messages

    async def login(self, username: str, password: str):
        payload = {'username': username, 'password': password}
        headers = {'Cookie': 'ng_environment=production-3'}
        async with self._session.post(LOGIN_URL, headers=headers, data=payload) as resp:
            status = (await resp.json())['status']
            if status != 'ok':
                raise ValueError('Wrong credentials')
            self._id = resp.cookies['id'].value
            self._token = resp.cookies['access_token'].value

    async def get_employees(self):
        params = {'include_deleted': 'true'}
        headers = {'Cookie': 'ng_environment=production-3'}
        async with self._session.get(EMPLOYEES_URL, params=params, headers=headers) as resp:
            self.employees = await resp.json()

    def _get_message_author(self, topic, event) -> Tuple[str, bool]:
        creator = event['creator']
        if creator['creatorType'] == EventCreator.EMPLOYEE.value:
            return self._get_employee(creator['userId']), False
        elif creator['creatorType'] == EventCreator.CLIENT.value:
            return topic['discourserName'], True
        else:
            return creator['userId'], False

    def _get_employee(self, employee_id: str) -> str:
        for employee in self.employees:
            if str(employee['id']) == employee_id:
                return ' '.join([employee['last_name'], employee['first_name']])
        return employee_id

    @on_predicate(expo, lambda x: x.status != 200, max_time=BACKOFF_MAX_TIME)
    @on_exception(expo, asyncio.TimeoutError, max_time=BACKOFF_MAX_TIME)
    async def _make_request(self, method: str, params: Dict[str, Any]) -> ClientResponse:
        headers = {'Access-Token': self._token}
        default_params = {'accountId': self._id}
        default_params.update(params)
        async with self._sem:
            return await self._session.get(method, params=default_params, headers=headers)
