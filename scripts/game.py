from data_game.GameState import GameState, SceneManager, GameProgress
import os
import pygame

# pygame.init()

default_save_slot = 1

def main():
    ## Setup game data
    game_state = GameState()
    game_state.load_or_create_progress(save_slot=default_save_slot)
    SceneManager.instantiate_game(game_state)
    SceneManager.change_scene(game_state.initial_scene)

    ## Setup clock
    clock = pygame.time.Clock()
    start_time = clock.tick()

    ## Main loop
    while(True):
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        # if events:
        #     print(events)

        # Update
        SceneManager.update()

        # Render
        SceneManager.render()
        clock.tick(60)

if __name__ == '__main__':
    main()