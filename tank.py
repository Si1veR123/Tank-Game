class Tank:
    def __init__(self, player, colour_dict):
        self.coords = (470, 470)
        self.screen = int(player)
        self.speed = 8
        all_images = colour_dict[player]
        self.up_image, self.down_image, self.left_image, self.right_image = all_images
        self.image = self.up_image
        self.dir = 'up'
        self.prevdir = 'up'
        self.stopped = True
        self.prevstopped = True

    def move(self):
        if not self.stopped:
            if self.dir == 'up':
                x, y = self.coords
                self.coords = (x, y-self.speed)
                self.image = self.up_image

            elif self.dir == 'down':
                x, y = self.coords
                self.coords = (x, y+self.speed)
                self.image = self.down_image

            elif self.dir == 'right':
                x, y = self.coords
                self.coords = (x+self.speed, y)
                self.image = self.right_image

            elif self.dir == 'left':
                x, y = self.coords
                self.coords = (x-self.speed, y)
                self.image = self.left_image


    def relative_pos(self, coord):
        if self.dir == 'down':
            return coord[0], coord[1]+90
        elif self.dir == 'right':
            return coord[0]+90, coord[1]
        else:
            return coord

    def check_offscreen(self, switch_sides=False):
        """
        Returns: True if changed screen. None if not
        """
        # check for right side
        if self.relative_pos(self.coords)[0] > 1000:
            if self.screen in (1, 3) and switch_sides:
                self.screen += 1
                self.coords = (1, self.coords[1])
                return True
            else:
                self.coords = (910, self.coords[1])
        # check for bottom
        elif self.relative_pos(self.coords)[1] > 1000:
            if self.screen in (1, 2) and switch_sides:
                self.screen += 2
                self.coords = (self.coords[0], 1)
                return True
            else:
                self.coords = (self.coords[0], 910)
        # check for left side
        elif self.coords[0] < 0:
            if self.screen in (2, 4) and switch_sides:
                self.screen -= 1
                self.coords = (910, self.coords[1])
                return True
            else:
                self.coords = (0, self.coords[1])
        # check for top
        elif self.coords[1] < 0:
            if self.screen in (3, 4) and switch_sides:
                self.screen -= 2
                self.coords = (self.coords[0], 910)
                return True
            else:
                self.coords = (self.coords[0], 0)
