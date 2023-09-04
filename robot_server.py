import sys
import time
import asyncio

MAXBUF = 1023

class AsyncServer:
    def __init__(self, name='Controller', ip=None, port=1000, rate=100, offline=False, verbose=False):
        """This is the object that handles serial command inputs and directs the servo positions
        according to the commands given.

        Parameters:
        -----------
        name        : (str)     The custom name for the class
        ip          : (str)     The IP address to use to start the server
        port        : (int)     Port number on ip address to allow client connections
        rate        : (int)     Frequency of publishing rate for data to IP address
        simulate    : (bool)    Allow physical control of hardware
        verbose     : (bool)    Enable/disable verbose output text to the terminal
        """
        self.name = name
        if ip is None:
            ip = 'localhost'
        self.ip = ip
        self.port = port
        self.rate = rate
        self.offline = offline
        self.verbose = verbose
        
        # Internal parameters
        self.counter = 0
        self.queue = []
        self.all_stop = False
        self.stop_after_disconnect = True
        self.prev_t = 0
        
        if self.verbose: self.logger("{} object created!".format(self.name))
        
    def logger(self, *argv):
        msg = ''.join(argv)
        print("[{:.3f}][{}] {}".format(time.monotonic(), self.name, msg))

    def start(self):
        """ Makes a call to the asyncronous library to run a main routine """
        asyncio.run(self.main()) # Need to pass the async function into the run method to start

    def stop(self):
        """ Sets a flag to stop running all tasks """
        self.all_stop = True
        
    async def main(self):
        """ Keeping the main tasks and coroutines in a single main function """
        if not self.offline:
            self.logger("Setting up webserver on ( ip: '{}', Port: {} ) ...".format(self.ip, self.port))
            asyncio.create_task(asyncio.start_server(self.serve_client, self.ip, self.port))
        
        # Helper routine to keep publishing messages to the queue instead of waiting on a client
        #asyncio.create_task( self.helper_queue_msgs( 50 ) ) 
        
        #self.logger("Setting up robot update rate")
        #asyncio.create_task( self.update(12) ) 

        self.logger("{} running!".format(self.name))
        
        while self.all_stop != True:
            await asyncio.sleep(0) # Calling #async with sleep for 0 seconds allows coroutines to run

    async def serve_client(self, reader, writer):
        """ A callback function that gets called whenever a new client connection is established. It receives a 
            (reader, writer) pair as two arguments, instances of the StreamReader and StreamWriter classes. 
            Any messages received will then be 'queued' for handling by the controller. 
        """

        response = None
        while self.all_stop != True:
            while response != 'quit' and response !='':
                response = (await reader.read(MAXBUF)).decode('utf8')
                print(response)
                
            self.logger("Client {} disconnected".format(reader))
            writer.close()
            if self.stop_after_disconnect:
                self.logger('Server shutdown')
                self.stop()