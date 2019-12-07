import asyncio
from aiohttp import ClientSession, TCPConnector, ClientResponse
import datetime
import enum
import csv
from typing import Tuple, Optional
from asyncclick import command, option, File, DateTime, STRING
from backoff import expo, on_predicate
from config import LIVETEX_BASE_URL, LOGIN_URL, DIALOGS_URL, DIALOG_INFO, MAX_LIMIT
from helpers import flat


class EventType(enum.Enum):
    TEXT = 'TextMessage'


class EventCreator(enum.Enum):
    EMPLOYEE = 'Employee'
    CLIENT = 'Discourser'


async def login(username: str, password: str, session: ClientSession) -> Tuple[str, str]:
    payload = {'username': username, 'password': password}
    headers = {'Cookie': 'ng_environment=production-3'}
    async with session.post(LOGIN_URL, headers=headers, data=payload) as resp:
        status = (await resp.json())['status']
        if status != 'ok':
            raise ValueError('Wrong credentials')
        return resp.cookies['id'].value, resp.cookies['access_token'].value


class LivetexExtractor:
    def __init__(self, account_id: int, token: str,
                 start: datetime.datetime, end: datetime.datetime,
                 session: ClientSession) -> None:
        self._id = account_id
        self._token = token
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
                messages.append({
                    'dialog_id': topic_id,
                    'text': event['message'],
                    'timestamp': event['ctime'],
                    'author': self._get_message_author(topic, event),
                })
        return messages

    def _get_message_author(self, topic, event) -> Optional[str]:
        creator = event['creator']
        if creator['creatorType'] == EventCreator.EMPLOYEE.value:
            return self._get_employee(creator['userId'])
        elif creator['creatorType'] == EventCreator.CLIENT.value:
            return topic['discourserName']
        return None

    def _get_employee(self, employee_id: str) -> str:
        return employee_id

    @on_predicate(expo, lambda x: x.status != 200, max_time=60)
    async def _make_request(self, method: str, params) -> ClientResponse:
        headers = {'Access-Token': self._token}
        default_params = {'accountId': self._id}
        default_params.update(params)
        return await self._session.get(method, params=default_params, headers=headers)


@command()
@option('--username', prompt='Enter your username', type=STRING, help='Livetex username')
@option('--password', prompt='Enter your password', type=STRING, help='Livetex password')
@option('--start', prompt='Start', type=DateTime(), help='Start extracting from this date')
@option('--end', prompt='End', type=DateTime(), help='Extract messages till this date')
@option('--output', prompt='Output', type=File('w'), help='Output file')
async def main(username, password, start, end, output):
    tasks = []
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        account_id, token = await login(username, password, session)
        extractor = LivetexExtractor(account_id, token, start, end, session)
        topics_short = await extractor.get_dialogs_short()
        for topic in topics_short:
            task = asyncio.ensure_future(extractor.get_dialog_info(topic['topicId']))
            tasks.append(task)

        data = flat(await asyncio.gather(*tasks))

    dict_writer = csv.DictWriter(output, data[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(data)

if __name__ == '__main__':
    main(_anyio_backend='asyncio')
