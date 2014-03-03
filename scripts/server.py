import sys
import socket
import signal
import select

BUFSIZE = 1024

class ChatServer:

    def __init__(self, port=8989, listen=5):

        # Connected Users
        self.users = {}

        # Commands
        self.cmds  = {
            'quit'  : self.quit,   # Quit user
            'leave' : self.quit,   # Quit user
            'join'  : self.join,   # Join user to a room
            'rooms' : self.rooms,  # Show available rooms & count of users in each room
            'who'   : self.who,    # Show user list in the current room
        }

        # To see how may clients connected
        self.clients = 0

        # Establish server
        self.server  = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        try:
            self.server.bind( ('', port) )
        except socket.error as msg:
            sys.stderr.write('Bind Error. Code: ' + str(msg[0]) + ' ' + str(msg[1]) )
            sys.exit(1)

        self.server.listen(listen)
        print 'Listening on port ' + str(port) + ' ...'

        # Handle interrupt here
        signal.signal( signal.SIGINT, self.sigint_handle )

    def sigint_handle(self, signum, frame):
        print "\nShutting down the server"
        for o in self.outputs:
            o.close()
        self.server.close()

    def accept(self):

        self.inputs  = [self.server, sys.stdin]
        self.outputs = []
        running = 1

        while running:
            try:
                inputs, outputs, excepts = select.select( self.inputs, self.outputs, [] )
            except select.error as e:
                sys.stderr.write( str(e[1]) + '\n' )
                break
            except socket.error as e:
                sys.stderr.write( str(e[1]) + '\n' )
                break

            for s in inputs:
                if s == self.server:

                    client, address = self.server.accept()
                    print "Connected by " + address[0] + ':' + str(address[1])

                    self.clients += 1
                    client.send('<== Welcome to XYZ chat server\n')
                    client.send('<== Login Name?\n')
                    client.send('==> ')

                    self.inputs.append(client)

                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    running = 0
                else:
                    data = s.recv(BUFSIZE)

                    if data:
                        # If data starts with a '/', then it is a command
                        # If valid command, proceed with action otherwise
                        # show appropirate message
                        if data.find('/') == 0:

                            cmd = data.replace('/', '')
                            cmd = cmd.rstrip('\r\n')
                            #sys.stdout.write( '<== ' + repr(cmd) )
                            if self.cmds.has_key(cmd):
                                self.cmds[cmd](client, address)
                                break
                            else:
                                s.send("<== Invalid command '/" + cmd + "' used\n")
                                s.send('==> ')
                        else:
                            # Check if login name already taken or not
                            user = data.rstrip('\r\n')
                            if self.users.has_key(user):
                                s.send( '<== Sorry, name taken.\n' )
                                s.send( '<== Login Name?\n' )
                                s.send( '==> ' )
                            else:
                                self.users[user] = 1
                                s.send( '<== Welcome ' + user + '!\n' )
                                s.send( '==> [' + user + ']:'  )
                    else:
                        self.clients -= 1
                        s.close()
                        self.inputs.remove(s)


        self.server.close()

    def quit(self, client, address):
        self.clients -= 1
        print "Disconnected by " + address[0] + ':' + str(address[1])
        client.send('<== BYE\n')
        client.close()
        self.inputs.remove(client)

    def join(self,client, address):
        print "Join"

    def who(self):
        print "Who"

    def rooms(self):
        print "Rooms"

if __name__ == "__main__":
    ChatServer().accept()

