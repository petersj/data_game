import json
# from typing import TypedDict, NotRequired, Required
from .Level import all_level_refs_set, LevelRefSet, LevelProgress
from .Worker import Worker, get_preset_worker
from .GameObject import TextSurface, InteractiveTextSurface
import pickle
import os
import time
import pygame

## Settings
format_savefile_path = lambda x: 'sav{}.pickle'.format(x)
auto_save_on_level_end = False

pygame.init()

class SceneManager:
    current_scene = None
    game_state = None

    @staticmethod
    def instantiate_game(game_state):
        SceneManager.game_state = game_state

    @staticmethod
    def change_scene(new_scene):
        # if SceneManager.current_scene is not None:
        #     current_scene.unload()
        SceneManager.current_scene = new_scene
        SceneManager.current_scene.load(SceneManager.game_state)

    @staticmethod
    def update():
        SceneManager.current_scene.update()

    @staticmethod
    def render():
        SceneManager.current_scene.render()
        pygame.display.flip()

class Scene:
    def load():
        pass
    def update():
        pass
    def render():
        pass

class UnityScene:
    def load(self, game_state):
        self.game_state = game_state
        self.background = pygame.Surface(self.game_state.screen.get_size())
        self.message_surface_size = (1000, 200)
        self.message_surface_pos = (100, 500)
        self.message_surface = TextSurface(pos=self.message_surface_pos, size=self.message_surface_size, text='THIS IS A TEST')


    def update(self):
        events = pygame.event.get()
        # for event in events:
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if pygame.Rect(self.message_surface_pos, self.message_surface_size).collidepoint(event.pos):
            #         self.message_surface.active = True
            #     else:
            #         self.message_surface.active = False
            # if event.type == pygame.KEYDOWN and self.message_surface.active:
            #     self.message_surface.keydown_events.append(event)


        self.message_surface.update()

    def render(self):
        self.background.fill((0, 0, 0))
        self.message_surface.render(self.background)
        self.game_state.screen.blit(self.background, (0, 0))

class GameProgress:
    def __init__(self, available_levels=None, level_progress_dict=None):
        self.available_levels = available_levels
        self.level_progress_dict = level_progress_dict
        if not self.available_levels:
            self.available_levels = LevelRefSet(dict())
            self.level_progress_dict = dict()
            self.unlock_level_by_num(0)

    def is_level_unlocked(self, num):
        return self.available_levels.contains_num(num)

    def unlock_level_by_num(self, num=None):
        self.available_levels.add_level_by_num(num)
        if num not in self.level_progress_dict.keys():
            self.level_progress_dict.update({num: LevelProgress(num)})

class GameState:
    def __init__(self):
        self.all_level_refs_set = all_level_refs_set
        self._current_level_num = None
        self.game_progress = None
        self.workers = []
        self.screen = pygame.display.set_mode((1280,720))

    @property
    def initial_scene(self):
        return UnityScene()

    @property
    def current_level_num(self):
        return self._current_level_num
    @current_level_num.setter
    def current_level_num(self, level=None):
        self._current_level_num = level

    ## LEVEL UTILITIES
    def level_exists(self, num):
        return self.all_level_refs_set.contains_num(num)
    def is_level_unlocked(self, num):
        return self.game_progress.is_level_unlocked(num)
    def is_level_unlockable(self, num):
        return self.level_exists(num) and not self.is_level_unlocked(num)
    def unlock_level_by_num(self, num=None):
        if self.is_level_unlockable(num):
            self.game_progress.unlock_level_by_num(num)
    def get_level_by_num(self, num):
        return self.all_level_refs_set.get_level_by_num(num)
    def unlock_all(self):
        for num in range(10):
            self.unlock_level_by_num(num)


    ## SAVE/LOAD UTILITIES
    def load_or_create_progress(self, save_slot=1):
        save_path = format_savefile_path(save_slot)
        try:
            if os.path.exists(save_path):
                with open(save_path, 'rb') as savefile:
                    obj = pickle.load(savefile)
                    self.game_progress = GameProgress(available_levels=LevelRefSet(obj['available_levels']), level_progress_dict=obj['level_progress_dict'])
        except:
            print('(WARNING: FAILED TO LOAD FROM FILE {})'.format(save_path))
            self.game_progress = GameProgress()
    def reset_progress(self, save_slot=1):
        self.game_progress = GameProgress()
    def save_progress(self, save_slot=1):
        save_path = format_savefile_path(save_slot)
        # print(save_path)
        try:
            with open(save_path, 'wb') as savefile:
                obj = {
                    'available_levels': self.game_progress.available_levels.level_refs
                    , 'level_progress_dict': self.game_progress.level_progress_dict
                    }
                print({level_num:{'max_score':progress.max_score, 'max_round':progress.max_round} for level_num, progress in obj['level_progress_dict'].items()})
                pickle.dump(obj, savefile)
        except:
            print('(WARNING: FAILED TO SAVE)')
    def backup_progress(self):
        self.save_progress(save_slot=0)
    def load_backup_progress(self):
        self.load_or_create_progress(save_slot=0)

    ## WORKER UTILITIES
    def add_worker(self, worker=None):
        if worker:
            self.workers.append(worker)

