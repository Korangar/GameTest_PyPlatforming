from input import poll
from player import Player
from window import init as window_init
from window import render
from pygame import init as game_init
from pygame import event, time, quit
from pygame.locals import *

FPS = 30
delta = 1.0 / FPS

game_init()
window_init()
clock = time.Clock()
players = [None, None, None, None]
done = False
while not done:
    for e in event.get():
        if e.type == QUIT:
            done = True
    poll(players)
    for player in players:  # type: Player
        if player:
            player.update(delta)
    render(players)
    clock.tick(FPS)
quit()
