# examples/server_simple.py
from aiohttp import web

async def chatter_handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def get_robot_handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def post_robot_handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Received post, " + name
    return web.Response(text=text)

async def client_handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)



app = web.Application()
app.add_routes([web.get('/robot', get_robot_handle),
                web.post('/robot', post_robot_handle
                )])

if __name__ == '__main__':
    web.run_app(app)