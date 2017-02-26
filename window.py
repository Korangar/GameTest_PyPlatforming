from pygame import display, draw, font, Surface, transform
from world import FIELD
from pygame.locals import *

CLR_black = (0, 0, 0)
CLR_darkgray = (75, 75, 75)
CLR_grayishwhite = (200, 200, 200)
CLR_white = (255, 255, 255)
CLR_pinkish = (255, 0, 110)
CLR_blueish = (0, 148, 255)
CLR_orange = (255, 106, 0)
CLR_red = (255, 0, 0)
p_CLRs = [CLR_white, CLR_pinkish, CLR_blueish, CLR_orange]
effect_smoke = []
TILE_scale = 16


def get_perfect_size():
    import world
    return len(world.FIELD[0]) * TILE_scale, len(world.FIELD) * TILE_scale


def init():
    global SCR, SCR_scale, SCR_resolution, FONT_debug
    font.init()
    display.init()
    #init screen
    w, h = get_perfect_size()
    SCR_scale = 1
    SCR_resolution = int(w * SCR_scale), int(h * SCR_scale)
    SCR = display.set_mode(SCR_resolution)
    #init a debug font
    FONT_debug = font.Font(None, 10)


def draw_tile(canvas, ID):
    fill_colors = {0: CLR_black, 1: CLR_darkgray}
    draw.rect(canvas, fill_colors.get(ID), canvas.get_clip())


def draw_field():
    canvas = Surface(get_perfect_size())
    for row in range(len(FIELD)):
        for col in range(len(FIELD[0])):
            scr_x = col * TILE_scale
            scr_y = row * TILE_scale
            canvas.set_clip((scr_x, scr_y, TILE_scale, TILE_scale))
            draw_tile(canvas, FIELD[row][col])
            canvas.set_clip()
    return canvas


def draw_player(canvas, player, draw_clr):
    if player:
        pos = (player.POSITION[0]) * TILE_scale, (player.POSITION[1] - 1.0) * TILE_scale
        draw.rect(canvas, draw_clr, (pos[0], pos[1], TILE_scale, TILE_scale * 2), 0)


def frame_effect_smoke(canvas, state):
    pos, step = state
    ful_duration = 30.0

    timefactor = step/ful_duration
    rad = int(20 * timefactor) + 1
    width = int(10 * timefactor)

    c_val = int(200 * (1-timefactor))
    clr = (c_val, c_val, c_val)
    draw.circle(canvas, clr, pos, rad, width)
    return (step+1 < ful_duration), (pos, step+1)


def draw_effects(canvas):
    global effect_smoke
    new_effect_list = []
    for state in effect_smoke:
        b, state = frame_effect_smoke(canvas, state)
        if b:
            new_effect_list.append(state)
    effect_smoke = new_effect_list


def render(players):
    canvas = draw_field()
    for i in range(4):
        draw_player(canvas, players[i], p_CLRs[i])
    draw_effects(canvas)
    transform.scale(canvas, SCR_resolution, SCR)
    display.flip()


def add_effect(pos):
    x = int(pos[0])
    y = int(pos[1])
    effect_smoke.append(((x, y), 0))
