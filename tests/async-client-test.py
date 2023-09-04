import sys
import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')

@sio.event
async def my_message(data):
    print('message received with ', data)
    await sio.emit('my response', {'response': 'my response'})

@sio.event
async def disconnect():
    print('disconnected from server')

async def main(domain):
    await sio.connect('http://127.0.0.1:5000')
    await sio.wait()

if __name__ == '__main__':

    domain = 'http://172.26.81.178:5000'

    if len(sys.argv) > 1:
        domain = sys.argv[1]

    asyncio.run(main(domain))