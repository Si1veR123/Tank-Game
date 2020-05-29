import pygame, os, queue, json, math, tkinter, time
from tank import Tank
from network_client import Network
from threading import Thread


def resize(surface, dimensions):
    return pygame.transform.scale(surface, dimensions)


def receive_thread(thread_client, q):
    while True:
        data = thread_client.receive()

        try:
            json_data = json.loads(data)
            print('Put: {}'.format(json_data))
            q.put(json_data)

        except json.JSONDecodeError:
            print('app.py is splitting json...')
            end_bracket = False
            for count, letter in enumerate(data):
                if end_bracket:
                    if letter == '[':
                        data = data[:count] + '|' + data[count:]

                end_bracket = False

                if letter == ']':
                    end_bracket = True

            json_data = data.split('|')

            print(json_data)
            for item in json_data:
                print('Splitted: {}'.format(item))
                q.put(json.loads(item))


def find_distance(val1x, val1y, val2x, val2y):
    distancex = val2x - val1x
    distancey = val2y - val1y
    distancepoints = math.sqrt(distancex ** 2 + distancey ** 2)
    return distancepoints

def gun_pos(coords, dir):
    player_x, player_y = coords
    if dir == 'up':
        bullet_coords = (player_x + 40, player_y - 10)
    elif dir == 'left':
        bullet_coords = (player_x - 10, player_y + 40)
    elif dir == 'right':
        bullet_coords = (player_x + 90, player_y + 40)
    elif dir == 'down':
        bullet_coords = (player_x + 40, player_y + 90)
    else:
        bullet_coords = (0, 0)
    return bullet_coords


def rotate_three(surface: pygame.Surface):
    surface_down = pygame.transform.rotate(surface, 180)
    surface_left = pygame.transform.rotate(surface, 90)
    surface_right = pygame.transform.rotate(surface, 270)
    return surface_down, surface_left, surface_right


red_tank = pygame.image.load('images/tank_red.png')
blue_tank = pygame.image.load('images/tank_blue.png')
green_tank = pygame.image.load('images/tank_green.png')
yellow_tank = pygame.image.load('images/tank_yellow.png')

red_tank_down, red_tank_left, red_tank_right = rotate_three(red_tank)
blue_tank_down, blue_tank_left, blue_tank_right = rotate_three(blue_tank)
green_tank_down, green_tank_left, green_tank_right = rotate_three(green_tank)
yellow_tank_down, yellow_tank_left, yellow_tank_right = rotate_three(yellow_tank)

colour_dict = {
    '1': (red_tank, red_tank_down, red_tank_left, red_tank_right),
    '2': (blue_tank, blue_tank_down, blue_tank_left, blue_tank_right),
    '3': (green_tank, green_tank_down, green_tank_left, green_tank_right),
    '4': (yellow_tank, yellow_tank_down, yellow_tank_left, yellow_tank_right)
}

client = Network()
if client.player == '1':
    while True:
        print("Waiting for you to type 'go': ")
        client.send(input())
        if client.receive() == 'ready':
            break
        else:
            print('Incorrect Input')
else:
    print('Waiting')
    client.receive()

player = Tank(client.player, colour_dict)

pygame.init()

backgrounds = [resize(pygame.image.load('images/bg_tl.png'), (1000, 1000)),
               resize(pygame.image.load('images/bg_tr.png'), (1000, 1000)),
               resize(pygame.image.load('images/bg_bl.png'), (1000, 1000)),
               resize(pygame.image.load('images/bg_br.png'), (1000, 1000))]

bullet_img_up = resize(pygame.image.load('images/bullet.png'), (20, 20))
bullet_img_down, bullet_img_left, bullet_img_right = rotate_three(bullet_img_up)

arrow_up = pygame.image.load('images/arrow.png')
arrow_down, arrow_left, arrow_right = rotate_three(arrow_up)

bushes = resize(pygame.image.load('images/bushes.png'), (1000, 1000))

os.environ['SDL_VIDEO_CENTERED'] = '1'

root = pygame.display.set_mode(size=(1000, 1000))
pygame.display.set_caption('Tank PVP')


recv_q = queue.Queue()
recv_thread = Thread(target=receive_thread, args=(client, recv_q), daemon=True)
recv_thread.start()

other_positions = {}


bullets = []
lasers = []

bullet_speed = 12

clock = pygame.time.Clock()

font = pygame.font.SysFont(pygame.font.get_default_font(), 50)

bullet_cooldown = 0
bullet_overheated = False
bullet_pressed = 0
last_changed = 0
running = True
while running:
    start_timer = time.time()
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    root.fill((255, 255, 255))
    root.blit(backgrounds[player.screen-1], (0, 0))
    root.blit(player.image, player.coords)

    key = pygame.key.get_pressed()

    # get movement keys
    player.prevdir = player.dir
    player.prevstopped = player.stopped
    if key[pygame.K_LEFT]:
        player.stopped = False
        player.dir = 'left'

    elif key[pygame.K_RIGHT]:
        player.stopped = False
        player.dir = 'right'

    elif key[pygame.K_UP]:
        player.stopped = False
        player.dir = 'up'

    elif key[pygame.K_DOWN]:
        player.stopped = False
        player.dir = 'down'

    else:
        player.stopped = True

    player.move()

    if player.prevdir != player.dir or player.prevstopped is not player.stopped:
        if not player.stopped:
            client.send(json.dumps(('pturn', (player.coords, player.dir, client.player, player.screen))))
        else:
            client.send(json.dumps(('pturn', (player.coords, 'stopped', client.player, player.screen))))


    """
    Firing bullets and checking and drawing overheat
    """

    if pygame.time.get_ticks() > bullet_pressed and not bullet_overheated:
        if key[pygame.K_SPACE]:
            bullet_coords = gun_pos(player.coords, player.dir)
            bullet_cooldown -= 20
            bullet_pressed = pygame.time.get_ticks() + 300

            bullets.append([bullet_coords, player.dir, player.screen])
            client.send(json.dumps(('pshot', ['bullet', bullet_coords, player.dir, player.screen])))

    if bullet_cooldown < 20 and not bullet_overheated:
        bullet_overheated = True
        bullet_cooldown = 0

    if pygame.time.get_ticks() > bullet_pressed and bullet_cooldown < 100:
        bullet_cooldown += 1
        if bullet_cooldown > 50 and bullet_overheated:
            bullet_overheated = False

    if bullet_overheated:
        cooldown_colour = (255, 0, 0)
    elif bullet_cooldown == 100:
        cooldown_colour = (0, 0, 255)
    else:
        cooldown_colour = (0, 255, 0)

    bullet_cooldown_text = font.render(str(bullet_cooldown), False, cooldown_colour)
    root.blit(bullet_cooldown_text, (0, 20))
    root.blit(bullet_img_right, (5, 0))

    """
    Firing lasers
    """
    if key[pygame.K_LCTRL]:
        laser_info = [
            gun_pos(player.coords, player.dir),
            player.dir,
            player.screen
        ]

        lasers.append(laser_info)
        client.send(json.dumps(laser_info))

    """
    Drawing lasers
    for laser in lasers:
        if laser[1] == 'up':
            laser_orientaion = laser_up
            if laser[2] == player.screen:
                laser_same = True
            elif laser[2] == player.screen + 2:
                laser_visible = True
        elif laser[1] == 'down':
            laser_orientaion = laser_down
        elif laser[1] == 'left':
            laser_orientaion = laser_left
        elif laser[1] == 'right':
            laser_orientaion = laser_right
    """

    """
    Limit speed of screen switching
    """
    if pygame.time.get_ticks() > last_changed + 3000:
        player_changed_screen = player.check_offscreen(switch_sides=True)
    else:
        player_changed_screen = player.check_offscreen()

    if player_changed_screen:
        last_changed = pygame.time.get_ticks()
        client.send(json.dumps(('pscreen', (client.player, player.screen, player.coords))))

    """
    Receiving data from server
    """
    if not recv_q.empty():
        recv_data = recv_q.get()
        print('Received', recv_data)
        if recv_data[0] == 'pturn':
            data = recv_data[1]
            other_positions[data[2]] = (data[0], data[1], data[3])
        elif recv_data[0] == 'pshot':
            data = recv_data[1]
            if data[0] == 'bullet':
                bullets.append([data[1], data[2], data[3]])
            elif data[0] == 'laser':
                lasers.append((data[1], data[2], data[3]))
        elif recv_data[0] == 'pnum':
            for num in range(recv_data[1]):
                num += 1
                if str(num) != client.player:
                    other_positions[str(num)] = ((470, 470), 'stopped', str(num))
        elif recv_data[0] == 'pscreen':
            data = recv_data[1]
            players_current_info = other_positions[data[0]]
            players_new_info = (data[2], players_current_info[1], data[1])
            other_positions[data[0]] = players_new_info
        elif recv_data[0] == 'left':
            print('left', recv_data[1])
            p_left = recv_data[1]
            del other_positions[p_left]

    for bullet in bullets:
        """
        Check bullet boundaries
        """
        # bullet hits right
        if bullet[0][0] > 1000:
            if bullet[2] in (1, 3):
                bullet[2] += 1
                bullet[0] = (0, bullet[0][1])
            else:
                bullets.remove(bullet)
        # bullet hits left
        elif bullet[0][0] < 0:
            if bullet[2] in (2, 4):
                bullet[2] -= 1
                bullet[0] = (1000, bullet[0][1])
            else:
                bullets.remove(bullet)
        # bullet hits bottom
        elif bullet[0][1] > 1000:
            if bullet[2] in (1, 2):
                bullet[2] += 2
                bullet[0] = (bullet[0][0], 0)
            else:
                bullets.remove(bullet)
        # bullet hits top
        elif bullet[0][1] < 0:
            if bullet[2] in (3, 4):
                bullet[2] -= 2
                bullet[0] = (bullet[0][0], 1000)
            else:
                bullets.remove(bullet)

        """
        Drawing and updating positions of bullets
        """
        if bullet[1] == 'left':
            x, y = bullet[0]
            bullet[0] = (x - bullet_speed, y)
            if bullet[2] == player.screen:
                root.blit(bullet_img_left, (bullet[0]))
        elif bullet[1] == 'right':
            x, y = bullet[0]
            bullet[0] = (x + bullet_speed, y)
            if bullet[2] == player.screen:
                root.blit(bullet_img_right, (bullet[0]))
        elif bullet[1] == 'up':
            x, y = bullet[0]
            bullet[0] = (x, y - bullet_speed)
            if bullet[2] == player.screen:
                root.blit(bullet_img_up, (bullet[0]))
        elif bullet[1] == 'down':
            x, y = bullet[0]
            bullet[0] = (x, y + bullet_speed)
            if bullet[2] == player.screen:
                root.blit(bullet_img_down, (bullet[0]))


    """
    Drawing other tanks
    """
    for tank in other_positions.items(): # (player, (position, direction))
        enemy_tank_pos, enemy_tank_dir, enemy_tank_screen = tank[1]
        enemy_tank_screen = int(enemy_tank_screen)
        other_tank_images = colour_dict[str(tank[0])]

        if enemy_tank_dir == 'up' or enemy_tank_dir == 'stopped':
            if enemy_tank_screen == player.screen:
                root.blit(other_tank_images[0], enemy_tank_pos)
            if enemy_tank_dir != 'stopped':
                enemy_tank_pos = (enemy_tank_pos[0], enemy_tank_pos[1]-player.speed)

        elif enemy_tank_dir == 'down':
            if enemy_tank_screen == player.screen:
                root.blit(other_tank_images[1], enemy_tank_pos)
            enemy_tank_pos = (enemy_tank_pos[0], enemy_tank_pos[1]+player.speed)

        elif enemy_tank_dir == 'left':
            if enemy_tank_screen == player.screen:
                root.blit(other_tank_images[2], enemy_tank_pos)
            enemy_tank_pos = (enemy_tank_pos[0]-player.speed, enemy_tank_pos[1])

        elif enemy_tank_dir == 'right':
            if enemy_tank_screen == player.screen:
                root.blit(other_tank_images[3], enemy_tank_pos)
            enemy_tank_pos = (enemy_tank_pos[0]+player.speed, enemy_tank_pos[1])

        other_positions[tank[0]] = (enemy_tank_pos, enemy_tank_dir, enemy_tank_screen)

        if enemy_tank_screen != player.screen:
            if enemy_tank_screen - player.screen == 1 and enemy_tank_screen != 3:
                arrow_coords = (980, enemy_tank_pos[1])
                root.blit(arrow_up, arrow_coords)
            elif enemy_tank_screen - player.screen == -1 and enemy_tank_screen != 2:
                arrow_coords = (20, enemy_tank_pos[1])
                root.blit(arrow_down, arrow_coords)
            elif enemy_tank_screen - player.screen == 2:
                arrow_coords = (enemy_tank_pos[0], 980)
                root.blit(arrow_right, arrow_coords)
            elif enemy_tank_screen - player.screen == -2:
                arrow_coords = (enemy_tank_pos[0], 20)
                root.blit(arrow_left, arrow_coords)


    for bullet in bullets:
        if find_distance(player.coords[0]+50, player.coords[1]+50, bullet[0][0], bullet[0][1]) < 50:
            if bullet[2] == player.screen:
                quit()

    if not len(other_positions) and pygame.time.get_ticks() > 3000:
        running = False

    root.blit(bushes, (0, 0))

    pygame.display.update()
    runtime = int(round(time.time() - start_timer, 2)*200)
    player.speed = runtime
    bullet_speed = runtime*2

client.send('end')

won = tkinter.Tk()
tkinter.Label(won, text='You Won', fg='blue').pack()
won.mainloop()
