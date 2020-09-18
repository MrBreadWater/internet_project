import pygame
import pygame.gfxdraw as antialiase
import socket
import threading
from threading import Lock
import time
from datetime import datetime
import errno

timestamp = lambda: datetime.now().strftime("%I:%M:%S.%f %p")

class Connection:
    def __init__(self, BUFFER_SIZE=1024, TCP_IP='127.0.0.1', LISTEN_PORT=41414, SEND_PORT=1337, SERVER=True):
        self.BUFFER_SIZE = BUFFER_SIZE
        self.LISTEN_PORT = LISTEN_PORT
        self.SEND_PORT = SEND_PORT
        self.SERVER = SERVER
        self.TCP_IP = TCP_IP
        self.data = None
        self.lock = Lock()
        self.conn = None
        self.thread = threading.Thread(target=self.read_data, daemon=True)
        self.thread.start()
        self.data = ''
    
    def read_data(self):
        retry = 0

        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.SERVER:
                    self.socket.bind((self.TCP_IP, self.LISTEN_PORT))
                    self.socket.listen(1)
                    
                    print("[%s] Acting as server! Waiting..." % timestamp())
                    self.conn, self.addr = self.socket.accept()
                    print("[%s] Connected to client!" % timestamp())
                    self.socket.settimeout(.1)
                    
                else:
                    print("[%s] Acting as client! Connecting..." % timestamp())
                    self.socket.connect((self.TCP_IP, self.LISTEN_PORT))
                    self.socket.sendall(b'TEST MESSAGE; CONNECTION ACQUIRED!')
                    self.socket.settimeout(1)
                    
                    
                break
            except socket.error as e:
                #self.data = e
                if e.errno == errno.EADDRINUSE:
                    retry += 1
                    if retry >=3:
                        raise Exception("Maximum retries reached!")
                        #self.data = 'maxtries'
                        break
                    print("[%s] Another server is already running! Switching ports and retrying (%d/3)..." % (timestamp(), retry))
                    #sp = self.SEND_PORT
                    #self.SEND_PORT = self.LISTEN_PORT
                    #self.LISTEN_PORT = sp
                    self.SERVER = not self.SERVER
                else:
                    print(f"[{timestamp()}] Another error occured! {e}")
                    break
        
        #with self.
        while True:
            self.data = ''
            data = True
            
            if self.SERVER:
                connection = self.conn
                msg = bytes("Hello, client! %s" % timestamp(), encoding='utf-8')
            else:
                connection = self.socket
                msg = bytes("Hello, server! %s" % timestamp(), encoding='utf-8')
                
            try:
                data = connection.recv(self.BUFFER_SIZE).decode()
            except socket.timeout:
                data = ''
                    
            self.data += data
            connection.sendall(msg)
                        
            print("<<", self.data)
            print(">>", msg)
                        
            
            time.sleep(1)
            
    def send_data(self, data):
        if self.conn:
            self.conn.send(data)
        

# Pygame boilerplate
#pygame.init()

conn = Connection()

ON = True
WIDTH, HEIGHT = (1000, 500)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
pygame.init()
# Margins
LEFT_MARGIN = 50
TOP_MARGIN = 50
BOTTOM_MARGIN = 50

BACKGROUND = (255, 255, 255)  # Background color
CARD_ON_COLOR = (0, 0, 0)  # color of an "active"/"on" card

CELL_SIZE = 100  # side length of each cell
NUM_POS_CELLS = 4  # number of positive-exponent cells
NUM_NEG_CELLS = 4  # number of negative-exponent cells

NUMBER_DIMS = (6, 7)  # dimensions of each text character (in Pixel objects)
PIXEL_SIZE = 5  # width and height of a Pixel object
TEXT_SPACING = 1  # spacing between text characters (in Pixel objects)
ROUND_LENGTH = 3  # number of decimals to round to for each number onscreen

pygame.display.set_caption("Flippy Do")

class Button:
    def __init__(self, center_x, center_y, width, height):
        self.x = center_x
        self.y = center_y
        self.width = width
        self.height = height

    def is_pressed(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.x - self.width / 2 < mouse_x < self.x + self.width / 2:

            if self.y - self.height / 2 < mouse_y < self.y + self.height / 2:

                if True in pygame.mouse.get_pressed():

                    pygame.time.delay(150)  # mouse click occurs over ~1/5 a second

                    if (mouse_x, mouse_y) == pygame.mouse.get_pos():
                        return True
        return False


class TextLabel:
    """
    any text on the screen
    """

    def __init__(self, x, y, text, pixel_size):
        """
        constructor
        :param x: x position on screen
        :param y: y position on screen
        :param text: text to be displayed
        :param pixel_size: size of pixels within each character
        """

        self.x, self.y = x, y

        self.text = str(text)
        self.num_characters = len(self.text)  # number of characters in the string
        self.pixel_size = pixel_size

        self.pixel_grids = []  # list of PixelGrid objects holding each character
        self.length = get_length_in_pixels(self.text, pixel_size=pixel_size)  # x-length of the text in pygame pixels

        self.initiate()

    def initiate(self):
        """
        instantiates a PixelGrid for each character
        :return: None
        """

        for i in range(self.num_characters):
            # creates a new PixelGrid for each character in self.text
            grid = PixelGrid(
                self.x + (i * self.pixel_size) * (NUMBER_DIMS[0] + TEXT_SPACING),
                self.y,
                *NUMBER_DIMS,
                self.pixel_size
            )
            grid.set_pixels_by_array(get_array_from_text(self.text[i]))  # sets character array configuration
            self.pixel_grids.append(grid)

    def set_pos(self, x, y):
        """
        sets position on screen to (x, y)
        :param x: x position on screen
        :param y: y position on screen
        :return: None
        """

        self.x, self.y = x, y  # sets self position vars to match new position values
        for grid in self.pixel_grids:
            grid.x, grid.y = x, y  # adjusts position vars of each PixelGrid to match new position values

        self.initiate()

    def set_text(self, new_text):
        """
        resets text to be displayed to parameter value
        :param new_text: text to be displayed
        :return: None
        """

        self.text = str(new_text)
        self.num_characters = len(self.text)
        self.length = self.num_characters * self.pixel_size

        self.pixel_grids = []
        self.initiate()

    def display(self):
        """
        displays text
        :return: None
        """
        for grid in self.pixel_grids:
            grid.display()
oldconn = ''
while ON:  # Main Update Loop
    # Tests for window closing
    newconn = conn.data

    if not oldconn == newconn:
        print("conn.data: ", newconn)

    oldconn = newconn
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ON = False
            

    WINDOW.fill(BACKGROUND)

    pygame.display.flip()
    CLOCK.tick(100)
