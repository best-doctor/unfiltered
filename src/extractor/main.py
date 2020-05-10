
import asyncio
from aiohttp import ClientSession, TCPConnector
import csv
from tqdm import tqdm
from asyncclick import command, option, File, DateTime, INT
from helpers import flat
from config import MAX_CONCURRENCY_LEVEL
from extractor import LivetexExtractor
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger('backoff').setLevel(logging.ERROR)


@command()
@option('--username', prompt='Enter your username', help='Livetex username')
@option('--password', prompt='Enter your password', hide_input=True, help='Livetex password')
@option('--start', prompt='Start', type=DateTime(), help='Start extracting from this date')
@option('--end', prompt='End', type=DateTime(), help='Extract messages till this date')
@option('--output', prompt='Output', type=File('w'), help='Output file')
@option('--njobs', type=INT, default=MAX_CONCURRENCY_LEVEL, help='Set max concurrency level')
async def main(username, password, start, end, output, njobs):
    tasks = []
    data = []
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        extractor = LivetexExtractor(
            start, end, session,
            concurrency_level=njobs,
        )
        logging.info('Logging in with the given credentials...')
        await extractor.login(username, password)
        logging.info('Successful login!')
        logging.info('Fetching employee list...')
        await extractor.get_employees()
        logging.info('Employee list received!')
        topics_short = await extractor.get_dialogs_short()
        if not topics_short:
            return
        topics_count = len(topics_short)
        logging.info('Fetching %i dialogs...', topics_count)
        for topic in topics_short:
            task = asyncio.create_task(extractor.get_dialog_info(topic['topicId']))
            tasks.append(task)
        try:
            for res in tqdm(asyncio.as_completed(tasks), total=topics_count):
                data.append(await res)
        finally:
            data = flat(data)
            dict_writer = csv.DictWriter(output, data[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(sorted(data, key=lambda x: x['dialog_start'] + x['timestamp']))

if __name__ == '__main__':
    main(_anyio_backend='asyncio')
