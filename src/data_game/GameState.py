import json
from typing import TypedDict, NotRequired, Required
from .Level import all_level_refs_set, LevelRefSet, LevelProgress
from .Worker import Worker, get_preset_worker
import pickle
import os
import time

#SETTINGS
format_savefile_path = lambda x: 'sav{}.pickle'.format(x)
auto_save_on_level_end = False

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

class Scene():
    def load():
        pass
    def update():
        pass

class MenuScene(Scene):
    def load(self, game_state):
        self.game_state = game_state
        
    def update(self):
        print('Levels: ')
        for level_ref in self.game_state.game_progress.available_levels:
            print('Enter {} for the level "{}"'.format(level_ref[0], level_ref[1]))
        cmd = input('MENU (h for help) >> ')
        match cmd:
            case '':
                pass
            case 'reset':
                self.game_state.reset_progress()
            case 'cheat':
                self.game_state.unlock_all()
            case 's':
                self.game_state.save_progress()
            case 'l':
                self.game_state.game_progress.load()
            case 'w':
                ##HARDCODED
                self.game_state.current_level_num = 5
                SceneManager.change_scene(WorkerScene())
            case level_num if level_num.isdigit():
                if self.game_state.is_level_unlocked(int(level_num)):
                    self.game_state.current_level_num = int(level_num)
                    SceneManager.change_scene(LevelScene())
                else:
                    print('{} is not a valid level'.format(cmd))
            case _:
                print('{} is not a valid level'.format(cmd))

class LevelScene(Scene):
    def load(self, game_state):
        self.game_state = game_state
        self.level_num = self.game_state.current_level_num
        self.level = self.game_state.get_level_by_num(self.level_num)
        self.level_progress = self.game_state.game_progress.level_progress_dict[self.level_num]
        self.score = 0
        self.step = 1
        self.needs_sample = True

    def update(self):
        if self.needs_sample:
            self.observed, self.target = self.level.get_next_sample()
        print('Round: {}'.format(self.step))
        if self.observed:
            print('Observation: {}'.format(self.observed))
        self.needs_sample = False
        cmd = input('Playing: {} >> '.format(self.level.name))
        match cmd:
            case '':
                pass
            case 's':
                self.game_state.save_progress()
            case 'l':
                confirm = input('This will abandon current level, press y to continue >>')
                if confirm == "y":
                    self.game_state.game_progress.load()
                    SceneManager.change_scene(MenuScene())
            case 'end':
                self.game_state.current_level_num = None
                if auto_save_on_level_end:
                    self.game_state.save_progress()
                SceneManager.change_scene(MenuScene())
            case response:
                self.needs_sample = True
                print('Evaluating Response: {} against Target: {}'.format(response, self.target))
                self.score = self.level.evaluate(self.level.response_type(response), self.target, self.score)
                print('Score: {}'.format(self.score))
                self.level_progress.update(score=self.score, step=self.step)
                if self.score > 5 and self.game_state.is_level_unlockable(self.level_num + 1):
                    self.game_state.game_progress.unlock_level_by_num(self.level_num + 1)
                    print('Unlocked Level: {}'.format(self.level_num + 1))
                print('---------------------')
                self.step += 1

class WorkerScene(Scene):
    def load(self, game_state):
        self.game_state = game_state
        self.level_num = self.game_state.current_level_num
        self.level = self.game_state.get_level_by_num(self.level_num)
        self.level_progress = self.game_state.game_progress.level_progress_dict[self.level_num]
        self.score = 0
        self.step = 1
        self.needs_sample = True
        self.worker = get_preset_worker()

    def update(self):
        if self.needs_sample:
            self.observed, self.target = self.level.get_next_sample()
            self.worker.input_nodes[0].evaluation = self.observed
        print('Round: {}'.format(self.step))
        if self.observed:
            print('Observation: {}'.format(self.observed))
        self.needs_sample = False
        time_start = time.time()
        print('WORKER THINKING')
        response = next(self.worker.work_tree.evaluate_work_tree())[1]['response']/2
        while time.time() < time_start + 2:
            time.sleep(0.5)
        self.needs_sample = True
        print('Evaluating Response: {} against Target: {}'.format(response, self.target))
        self.score = self.level.evaluate(self.level.response_type(response), self.target, self.score)
        print('Score: {}'.format(self.score))
        self.level_progress.update(score=self.score, step=self.step)
        # if self.score > 5 and self.game_state.is_level_unlockable(self.level_num + 1):
        #     self.game_state.game_progress.unlock_level_by_num(self.level_num + 1)
        #     print('Unlocked Level: {}'.format(self.level_num + 1))
        print('---------------------')
        self.step += 1

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

    @property
    def initial_scene(self):
        return MenuScene()

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

