from .DataTypes import Unit, Bit
from scipy.stats import bernoulli, uniform, multivariate_normal
import numpy as np

class Level:
    def __init__(self, num=0, name='No Name', response_type=Unit, data_inst=None, get_data_params=None, get_data=None, evaluation=lambda r, t, s: s, description=""):
        self.num=num
        self.name = name
        self.response_type = response_type
        self.data_inst = data_inst
        if self.data_inst and get_data_params:
            self.get_data_params = get_data_params(*self.data_inst)
        else:
            self.get_data_params = None
        self.get_data = get_data
        self.evaluation = evaluation
        self.description = description

    def get_next_sample(self):
        if self.get_data_params is not None:
            data = self.get_data(*self.get_data_params())
        else:
            data = self.get_data()
        return data['observed'], data['target']

    def evaluate(self, response, target, score):
        # target = self.get_target()
        # print('Evaluating {} against the target: {}'.format(response, target))
        return self.evaluation(response, target, score)

    def __str__(self):
        return self.name

all_levels = [
    Level(num=0
        , name='Unit Identity'
        , response_type=Unit
        , data_inst=None
        , get_data_params=None
        , get_data=lambda: {'observed': None, 'target': Unit(1)}
        , evaluation=lambda r, t, s: s + (1 if r == t else -1)
        )
    , Level(num=1
        , name='Biased Coin'
        , response_type=Bit
        , data_inst=(bernoulli(0.7),)
        , get_data_params=lambda dist: lambda: (dist.rvs(),)
        , get_data=lambda sample: {'observed': None, 'target': Bit(sample)}
        , evaluation=lambda r, t, s: s + (1 if r == t else -1)
        )
    , Level(num=2
        , name='Bit Identity'
        , response_type=Bit
        , data_inst=(bernoulli(0.5),)
        , get_data_params=lambda dist: lambda: (dist.rvs(),)
        , get_data=lambda sample: {'observed': Bit(sample), 'target': Bit(sample)}
        , evaluation=lambda r, t, s: s + (1 if r == t else -1)
        )
    , Level(num=3
        , name='Bit Flip'
        , response_type=Bit
        , data_inst=(bernoulli(0.5),)
        , get_data_params=lambda dist: lambda: (dist.rvs(),)
        , get_data=lambda sample: {'observed': Bit(sample), 'target': Bit(abs(1-sample))}
        , evaluation=lambda r, t, s: s + (1 if r == t else -1)
        )
    , Level(num=4
        , name='Bit Ops Blended'
        , response_type=Bit
        , data_inst=(uniform(), bernoulli(0.5))
        , get_data_params=lambda uni, bit: lambda: (uni.rvs(), uni.rvs(), bit.rvs())
        , get_data=lambda obs1, hidden, obs2: {'observed': (float(obs1), Bit(obs2)), 'target': Bit(obs2 if hidden > obs1 else abs(1-obs2))}
        , evaluation=lambda r, t, s: s + (1 if r == t else -1)
        )
    , Level(num=5
        , name='Correlated Normals'
        , response_type=float
        , data_inst=(multivariate_normal(mean=[0, 0], cov=[[1, .5], [.5, 1]]),)
        , get_data_params=lambda multi_n: lambda: tuple(multi_n.rvs())
        , get_data=lambda observed, target: {'observed': float(observed), 'target': float(target)}
        , evaluation=lambda r, t, s: s + (1 - (r - t)**2)
        )
    ]
all_levels_hash_name = {level.name: level for level in all_levels}
all_levels_hash_num = {level.num: level for level in all_levels}
all_level_refs = {level.num: level.name for level in all_levels}

class LevelRefSet:
    def __init__(self, level_refs=dict()):
        self.level_refs = level_refs
        self.level_names = self.level_refs.values()
        self.level_nums = self.level_refs.keys()

    def __iter__(self):
        yield from self.level_refs.items()

    def get_level_by_name(self, name: str):
        if name in self.level_names:
            return all_levels_hash_name[name]

    def get_level_by_num(self, num: int):
        if num in self.level_nums:
            return all_levels_hash_num[num]

    def contains_num(self, num: int):
        return True if num in self.level_nums else False

    def add_level_by_num(self, num: int, warn=True):
        if num in self.level_nums and warn:
            print('(WARNING: Level with that num already exists, try update_level_by_num)')
        self.level_refs.update({num: all_level_refs[num]})

all_level_refs_set = LevelRefSet({level.num: level.name for level in all_levels})

class LevelProgress:
    def __init__(self, level_num):
        self.level_num = level_num
        self.max_score = 0
        self.max_round = 0

    def update(self, score=0, step=0):
        self.max_score = max(self.max_score, score)
        self.max_round = max(self.max_round, step)


