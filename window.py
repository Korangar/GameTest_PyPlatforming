from pygame import display, draw, font, Surface, transform
from world import FIELD
from pygame.locals import *
from player import PlayerEntity


CLR_black = (0, 0, 0)
CLR_darkgray = (75, 75, 75)
CLR_grayishwhite = (200, 200, 200)
CLR_white = (255, 255, 255)
CLR_pinkish = (255, 0, 110)
CLR_blueish = (0, 148, 255)
CLR_orange = (255, 106, 0)
CLR_red = (255, 0, 0)
TILE_CLRs = {0: CLR_black, 1: CLR_darkgray, 2: CLR_blueish}
PLAYER_CLRs = {0: CLR_white, 1: CLR_pinkish, 2: CLR_blueish, 3: CLR_orange}
TILE_scale = 16


class PygameWindow:
    def __init__(self):
        font.init()
        display.init()
        # init screen
        self.raw_w, self.raw_h = len(FIELD[0]) * TILE_scale, len(FIELD) * TILE_scale
        self.scale = 1
        self.resolution = int(self.raw_w * self.scale), int(self.raw_h * self.scale)
        self.display_surface = display.set_mode(self.resolution)
        # init a debug font
        self.debug_font = font.Font(None, 10)
        self.effect_smoke = []

    def render(self, player):
        canvas = self.draw_field(player)
        self.draw_effects(canvas)
        self.display_surface.fill(CLR_black)
        transform.scale(canvas, self.resolution, self.display_surface)
        display.flip()

    def draw_field(self, players):
        canvas = Surface((self.raw_w, self.raw_h))
        for row in range(len(FIELD)):
            for col in range(len(FIELD[0])):
                scr_x = col * TILE_scale
                scr_y = row * TILE_scale
                subsurf = canvas.subsurface((scr_x, scr_y, TILE_scale, TILE_scale))
                subsurf.fill(TILE_CLRs[FIELD[row][col]])
        for i in range(4):
            player = players[i]  # type: PlayerEntity
            player_color = PLAYER_CLRs[i]
            if player:
                pos_x = (player.position.x + 0.0) * TILE_scale
                pos_y = (player.position.y - 1.0) * TILE_scale
                draw.rect(canvas, player_color, (pos_x, pos_y, TILE_scale, TILE_scale * 2), 0)
                aim_origin = player.get_shoot_origin()*TILE_scale
                draw.line(canvas, CLR_red, aim_origin, aim_origin + player.look_direction*TILE_scale*30)
                for e in player.events:
                    if e is "jump":
                        self.add_effect((pos_x + 0.5 * TILE_scale, pos_y + 2 * TILE_scale), player_color)
                        player.events.remove(e)
                    else:
                        pass
                # because those events are triggered by input.poll()
                # they get reset instantly afterwards
                # when the commands are passed as events to player update this reset will be moved to player update
                player.events = []
        return canvas

    def add_effect(self, pos, clr):
        x = int(pos[0])
        y = int(pos[1])
        self.effect_smoke.append(((x, y), 0, clr))

    def draw_effects(self, canvas):
        new_effect_list = []
        for state in self.effect_smoke:
            b, state = self.frame_effect_smoke(canvas, state)
            if b:
                new_effect_list.append(state)
        self.effect_smoke = new_effect_list

    def frame_effect_smoke(self, canvas, state):
        pos, step, color = state
        ful_duration = 30.0

        timefactor = step/ful_duration
        rad = int(20 * timefactor) + 1

        clr = tuple(map(lambda x: x*(1-timefactor), color))
        draw.circle(canvas, clr, pos, rad, 1)
        return (step+1 < ful_duration), (pos, step+1, color)
