import socket
import vim_bridge

from vimpdb import config

# after call of initialize function,
# pointer to vim module
# instead of importing vim module
vim = None

# after call of initialize function,
# holds a Controller instance
controller = None


def initialize(module):
    global vim
    global controller
    vim = module
    controller = Controller()


def buffer_create():
    source_buffer = vim.current.buffer.name
    vim.command('silent rightbelow 5new -vimpdb-')
    vim.command('set buftype=nofile')
    vim.command('set noswapfile')
    vim.command('set nonumber')
    vim.command('set nowrap')
    buffer = vim.current.buffer
    while True:
        vim.command('wincmd w')  # switch back window
        if source_buffer == vim.current.buffer.name:
            break
    return buffer


def buffer_find():
    for win in vim.windows:
        try:  # FIXME: Error while new a unnamed buffer
            if '-vimpdb-' in win.buffer.name:
                return win.buffer
        except:
            pass
    return None


@vim_bridge.bridged
def _PDB_buffer_write(message):
    pdb_buffer = buffer_find()
    if pdb_buffer is None:
        pdb_buffer = buffer_create()

    pdb_buffer[:] = None

    for line in message:
        pdb_buffer.append(line)
    del pdb_buffer[0]


@vim_bridge.bridged
def _PDB_buffer_close():
    vim.command('silent! bwipeout -vimpdb-')


def watch_create():
    source_buffer = vim.current.buffer.name
    vim.command('silent rightbelow 40vnew -watch-')
    vim.command('set buftype=nofile')
    vim.command('set noswapfile')
    vim.command('set nonumber')
    vim.command('set nowrap')
    buffer = vim.current.buffer
    while True:
        vim.command('wincmd w')   # switch back window
        if source_buffer == vim.current.buffer.name:
            break
    return buffer


def watch_find():
    for win in vim.windows:
        try:   # FIXME: Error while new a unnamed buffer
            if '-watch-' in win.buffer.name:
                return win.buffer
        except:
            pass
    return None


def watch_get():
    watch_buffer = watch_find()
    if watch_buffer is None:
        watch_buffer = watch_create()
    return watch_buffer


@vim_bridge.bridged
def _PDB_watch_reset():
    watch_buffer = watch_get()
    watch_buffer[:] = None


@vim_bridge.bridged
def _PDB_watch_write(message):
    watch_buffer = watch_get()

    for line in message:
        watch_buffer.append(line)
    if watch_buffer[0].strip() == '':
        del watch_buffer[0]


@vim_bridge.bridged
def _PDB_watch_close():
    vim.command('silent! bwipeout -watch-')


# socket management
class Controller(object):

    def __init__(self):
        configuration = config.getRawConfiguration()
        self.port = configuration.port
        self.host = '127.0.0.1'
        self.socket = None

    def init_socket(self):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                socket.IPPROTO_UDP)

    def socket_send(self, message):
        self.init_socket()
        self.socket.sendto(message, (self.host, self.port))

    def socket_close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None


@vim_bridge.bridged
def PDB_send_command(message):
    controller.socket_send(message)


@vim_bridge.bridged
def _PDB_socket_close():
    controller.socket_close()
