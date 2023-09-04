import sys
import asyncio

async def handle_client(reader, writer):
    request = None
    while request != 'quit' or '' or '\n':
        request = (await reader.read(255)).decode('utf8')
        #response = str(eval(request)) + '\n'
        if request != '\n' or '':
            print("Received: {}".format(request))
        #writer.write(response.encode('utf8'))
        #await writer.drain()
    #writer.close()

async def run_server(host, port):
    server = await asyncio.start_server(handle_client, host, port)
    async with server:
        await server.serve_forever()




"""
from aiohttp import web
import socketio
import pathlib

PROJECT_PATH = pathlib.Path(__file__).parent

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)


async def index(request):
    # Serve the client-side application.
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    print("message ", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

"""
if __name__ == '__main__':


    HOST = '192.168.1.164' # '127.0.0.1'
    PORT = 5000

    if len(sys.argv)>1:
        HOST = sys.argv[1]
        
    # Starting server
    print("Starting server on host {}, port {}".format(HOST, PORT))
    asyncio.run(run_server(HOST, PORT))
    # app.router.add_static('/static', 'static')
    #app.router.add_get('/', index)

    #web.run_app(app)
