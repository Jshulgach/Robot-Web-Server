import re
import sys
import time
import glob
import serial
import usb.core # pip install pyusb 1.2.1 and libusb
import asyncio
import subprocess

MAXBUF = 255
COMMAND_DELIMITER = ";"  # multiple commands should be parsed too
ARGUMENT_DELIMITER = ":" # expecting arguements to be spaced

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
    
class AsyncServer:
    def __init__(self, name='Robot Server', ip=None, port=1000, serial_port='COM5', baudrate=115200, rate=100, offline=False, use_serial=True, verbose=False):
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
        self.usb_serial = None
        self.offline = offline
        self.use_serial = use_serial
        self.verbose = verbose
        
        # Internal parameters
        self.counter = 0
        self.queue = []
        self.all_stop = False
        self.stop_after_disconnect = True
        self.response = None
        self.prev_t = 0
        
        self.usb_serial = self.connect_to_serial(serial_port, baudrate)
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
        """ Keeping the main tasks and coroutines in a single main function 
        """
        if not self.offline:
            self.logger("Setting up webserver on ( ip: '{}', Port: {} ) ...".format(self.ip, self.port))
        
            server = await asyncio.start_server(self.serve_client, self.ip, self.port)
            self.logger("{} running!".format(self.name))
            async with server:
                await server.serve_forever()
        #    asyncio.create_task(asyncio.start_server(self.serve_client, self.ip, self.port))
        #
        ##if self.verbose: self.logger("Setting up messaging update rate")
        asyncio.create_task( self.update(10) )
        #
        
        #
        #while self.all_stop != True:
        #    await asyncio.sleep(0) # Calling #async with sleep for 0 seconds allows coroutines to run
        
        

    async def serve_client(self, reader, writer):
        """ A callback function that gets called whenever a new client connection is established. It receives a 
            (reader, writer) pair as two arguments, instances of the StreamReader and StreamWriter classes. 
            Any messages received will then be 'queued' for handling by the controller. 
        """
        response = None
        state = 0
        while self.all_stop != True:
            while response != 'quit' and response !='' and response !='\n':
                #self.logger("reading")
                self.response = (await reader.read(MAXBUF)).decode('utf8')
                if self.verbose: self.logger(self.response)
                
                # Convert incommming user command to robot commands
                #self.logger("parsing")
                commands = self.parse_command(self.response)
                
                for cmd in commands:
                    self.logger("Sending: {}".format(str(cmd)))
                    '''
                    if state == 0:
                        self.logger("green")
                        self.usb_serial.write(b'led:0,100,0;')
                        #self.usb_serial.write(b'g;')
                        state = 1
                    elif state == 1:
                        self.logger("blue")
                        self.usb_serial.write(b'led:0,0,100;')
                        #self.usb_serial.write(b'b;')
                        state = 0
                     '''
                    self.usb_serial.write(cmd.encode('utf8'))
                    #self.logger("done")
                    
                #self.logger("check in waiting")
                #if self.usb_serial.in_waiting:        
                #    msg = self.usb_serial.read(self.usb_serial.inWaiting()).decode("utf-8")
                #    self.logger(msg)
                #self.logger("done")
            
            self.logger("Client {} disconnected".format(reader))
            writer.close()
            if self.stop_after_disconnect:
                self.logger('Server shutdown')
                self.stop()


    async def update(self, interval=100):
        """ Asyncronous co-routing that sends messages to the connected device.
        """
        while self.all_stop != True: 
            if self.usb_serial.in_waiting:  
                while self.usb_serial.in_waiting:            
                    print(self.usb_serial.readline().decode("utf-8"))

                #if self.s.is_open and self.response:
                #    print('writing')
                #    self.s.write(self.response.encode('utf8'))
                #    self.response = None
                
            await asyncio.sleep(1 / int(interval))
            #await asyncio.sleep(0) # handle this as fast as possible compared to the other coroutines           
        if self.verbose: self.logger("Updating stopped")


    def parse_command(self, incoming_msg):
        """ Helper function that converts the incomming command to the robot-specific commands
        """
        cmd_list = []
        commands = incoming_msg.split(COMMAND_DELIMITER)
        for command in commands:           
            if command != '' and command != '\r' and command != '\n':
                cmd_list.append(command+';')
        return cmd_list

    def connect_to_serial(self, port, baud):
        s = None
        if self.use_serial:
            self.logger("Serial Enabled. Looking for device on port {}".format(port))
            try:
                s = serial.Serial(port=port, baudrate=baud, timeout=None)
                if s.is_open: self.logger("Device found. Successful connection using port {}".format(s.port))
            except:
                self.logger("Failure to connect to device on ")
        return s