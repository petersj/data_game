from data_game.GameState import GameState, SceneManager, GameProgress
import os

default_save_slot = 1

def main():
    game_state = GameState()
    game_state.load_or_create_progress(save_slot=default_save_slot)
    SceneManager.instantiate_game(game_state)
    SceneManager.change_scene(game_state.initial_scene)
    while(True):
        SceneManager.update()

if __name__ == '__main__':
    main()