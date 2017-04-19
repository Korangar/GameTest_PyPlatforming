from input import poll
from player import Player
from window import PygameWindow
from pygame import init, event
from pygame.locals import *
import timing

if __name__ == "__main__":
    # app init
    init()
    window = PygameWindow()

    # game init
    players = [None, None, None, None]

    # game loop
    last_update = timing.now() - timing.update_delay
    update_loops_max = 5
    update_loops = 0
    while True:
        # update timing parameters
        time_since_update = timing.now() - last_update
        timing.delta_time = time_since_update / 1000

        # event pump for pygame
        event.pump()
        for e in event.get():
            if e.type == QUIT:
                quit()

        if time_since_update >= timing.update_delay and update_loops < update_loops_max:
            # update timing parameters
            next(timing.update_counter)
            last_update += timing.update_delay
            update_loops += 1

            # input polling
            poll(players)

            # game update, should be in world optimaly
            for player in players:  # type: Player
                if player:
                    player.update()

        else:
            # update timing parameters
            next(timing.redraw_counter)
            update_loops = 0

            # update the screen
            window.render(players)
