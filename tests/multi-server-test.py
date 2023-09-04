import asyncio
import threading
import time
import typing

import requests
from requests.adapters import HTTPAdapter

from uvicorn.config import Config
from uvicorn.main import Server


def test_run_signal_multi_threads():

    async def app3(scope, receive, send):
        """
        Send a slowly streaming HTTP response back to the client.
        """
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ]
        })
        for chunk in [b'Hello', b', ', b'world!']:
            await send({
                'type': 'http.response.body',
                'body': chunk,
                'more_body': True
            })
            await asyncio.sleep(5)
        await send({
            'type': 'http.response.body',
            'body': b'',
        })

    async def app2(scope, receive, send):
        """
        Echo the method and path back in an HTTP response.
        """
        assert scope['type'] == 'http'
        for i in scope.items():
            print(i)
        #print(receive)
        #print(send)

        body = f'Received {scope["method"]} request to {scope["path"]}'
        if scope["method"] == 'POST':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/plain'],
                ]
            })
            await send({
                'type': 'http.response.body',
                'body': body.encode('utf-8'),
            })


    class App:
        def __init__(self, scope):
            if scope["type"] != "http":
                raise Exception()

        async def __call__(self, receive, send):
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b"", "more_body": False})

    def join_t(*threads: threading.Thread) -> typing.List[None]:
        return [t.join() for t in threads]

    def start_threads(*threads: threading.Thread) -> typing.List[None]:
        return [t.start() for t in threads]

    def event_thread(
        worker: typing.Awaitable, loop, *args, **kwargs
    ) -> threading.Thread:
        def _worker(*args, **kwargs):
            try:
                loop.run_until_complete(worker(*args, **kwargs))
            except Exception as e:
                print(e)
            finally:
                loop.close()

        return threading.Thread(target=_worker, args=args, kwargs=kwargs)

    threads_count = 1
    loops = [asyncio.new_event_loop() for i in range(threads_count)]
    for loop in loops:
        asyncio.set_event_loop(loop)
    configs = [
        Config(
            app=app2, # App,
            port=5000 + i,
            loop=loops[i],
            #limit_max_requests=1,
            lifespan="off",
            #exit_signals=None,
        )
        for i in range(threads_count)
    ]
    servers = [Server(config=configs[i]) for i in range(threads_count)]
    workers = [event_thread(servers[i].serve, loop=loops[i]) for i in range(threads_count)]
    start_threads(*workers)
    time.sleep(1)

    count = 0
    while True:
            port = 5000
            #for x in range(threads_count):
            #port = 5000 + x
            #s = requests.Session()
            #s.mount(f"http://127.0.0.1:{port}", HTTPAdapter(max_retries=1))

            #r = requests.post(f"http://127.0.0.1:{port}", data=str(count))
            query = {'query_string': 'hello world'}
            res = requests.post(f"http://127.0.0.1:{port}", data=query)
            #print(res.text)
            count += 1
            time.sleep(1)

            #response = requests.get(f"http://127.0.0.1:{port}")
            #print(response.text)
            #response = requests.get(f"http://127.0.0.1:{port}")
            #print(response.text)
            #response = requests.get(f"http://127.0.0.1:{port}")
            #print(response.text)

            #assert response.status_code == 204

    join_t(*workers)
    print('join')

test_run_signal_multi_threads()
print("done")