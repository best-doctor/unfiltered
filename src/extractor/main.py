
import asyncio
from aiohttp import ClientSession, TCPConnector
import csv
from asyncclick import command, option, File, DateTime, STRING
from helpers import flat
from extractor import LivetexExtractor


@command()
@option('--username', prompt='Enter your username', type=STRING, help='Livetex username')
@option('--password', prompt='Enter your password', type=STRING, help='Livetex password')
@option('--start', prompt='Start', type=DateTime(), help='Start extracting from this date')
@option('--end', prompt='End', type=DateTime(), help='Extract messages till this date')
@option('--output', prompt='Output', type=File('w'), help='Output file')
async def main(username, password, start, end, output):
    tasks = []
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        extractor = LivetexExtractor(username, password, start, end, session)
        await extractor.login(session)
        await extractor.get_employees(session)
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
