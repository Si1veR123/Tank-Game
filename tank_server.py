import socket, queue, time, json
from threading import Thread

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '192.168.1.118'
    finally:
        s.close()
    return IP

server = get_ip()
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error:
    print('Error binding IP and port')

s.listen(4)
print("Waiting for a connection, Server Started")

main_q = queue.Queue()


def threaded_client(p):
    p = str(p)
    conn = conn_dict[p][0]

    conn.send(p.encode())

    while True:
        if p == '1':
            if conn.recv(100).decode() == 'go':
                main_q.put('go')
                break
            else:
                conn.send('incorrect'.encode())
        else:
            if not main_q.empty():
                break

    conn.send('ready'.encode())

    time.sleep(1)

    conn.send(json.dumps(('pnum', len(conn_dict))).encode())

    other_conn = [op[1][0] for op in conn_dict.items() if op[0] != p]

    while True:

        try:
            data = conn.recv(100)
        except ConnectionResetError:
            for other_connection in other_conn:
                other_connection.send(json.dumps(('left', p)).encode())
            del conn_dict[p]
            break
        if data.decode() == 'end':
            break

        for other_connection in other_conn:
            other_connection.send(data)


player = 1
conn_dict = {}
all_threads = []

while True:
    conn, addr = s.accept() # get connection data from client
    conn_dict[str(player)] = (conn, ) # saves player num : connection info in dictionary
    thread = Thread(target=threaded_client, args=(player, ), daemon=True)
    thread.start()
    all_threads.append(thread)
    print("Connected to:", addr)
    player += 1
