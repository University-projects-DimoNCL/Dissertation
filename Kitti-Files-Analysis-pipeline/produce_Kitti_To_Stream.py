import faust
from aiofile import LineReader, AIOFile
from time import sleep

app = faust.App('Kitti_producer', broker='kafka:\\localhost:9092')
topic = app.topic('kitti_files', value_serializer='raw')


# noinspection PyTypeChecker
@app.task
async def load_in_stream():
    async with AIOFile(
            '/home/dimo/PycharmProjects/pythonProject/inputs/Kitti '
            'Files/Buses/GNE_663_110520_1614_1634_Cam06_all_dla34_0.3_results.txt',
            'r',
            encoding="utf-8") as afp:
        async for line in LineReader(afp):
            await topic.send(value=line, value_serializer='raw')
            print('success')
            print(line)
            sleep(0.1)


if __name__ == '__main__':
    app.main()
