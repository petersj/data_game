import json
from itertools import tee
import numpy as np


## WorkTreeNode Classes
class WorkTreeNode:
    def __init__(self, name, evaluation=None):
        self.name = name
        self.evaluation = evaluation
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def add_children(self, children_nodes):
        for child_node in children_nodes:
            self.children.append(child_node)

    def to_dict(self):
        node_dict = {"name": self.name}
        if self.children:
            node_dict["children"] = [child.to_dict() for child in self.children]
        return node_dict

    def evaluate_work_tree(self):
        children=self.children
        if not children:
            yield self.name, self.evaluation
        else:
            yield self.name, self.evaluation(*zip(*(child.evaluate_work_tree() for child in children)))

class WorkTreeNodeAgg(WorkTreeNode):
    def __init__(self, name, agg_func, evaluation=(lambda agg_func: lambda results: agg_func([r[1] for r in results]))):
        super().__init__(name, evaluation)
        self.evaluation = evaluation(agg_func)
class WorkTreeNodeSum(WorkTreeNodeAgg):
    def __init__(self, name, agg_func=sum, evaluation=(lambda agg_func: lambda results: agg_func([r[1] for r in results]))):
        super().__init__(name, agg_func, evaluation)
class WorkTreeNodeMax(WorkTreeNodeAgg):
    def __init__(self, name, agg_func=max, evaluation=(lambda agg_func: lambda results: agg_func([r[1] for r in results]))):
        super().__init__(name, agg_func, evaluation)
class WorkTreeNodeMin(WorkTreeNodeAgg):
    def __init__(self, name, agg_func=min, evaluation=(lambda agg_func: lambda results: agg_func([r[1] for r in results]))):
        super().__init__(name, agg_func, evaluation)
class WorkTreeNodeMean(WorkTreeNodeAgg):
    def __init__(self, name, agg_func=lambda x: float(np.mean(x)), evaluation=(lambda agg_func: lambda results: agg_func([r[1] for r in results]))):
        super().__init__(name, agg_func, evaluation)


class Worker:
    def __init__(self, name):
        self.work_tree = WorkTreeNode(name='response_structured', evaluation=(lambda results: {name: evaluation for (name, evaluation) in results}))
        self.level = None
        self.input_nodes = None
        self.output_nodes = None
    
    def set_IO_for_level(self):
        self.response_output = WorkTreeNode(name='response')
        self.work_tree.add_child(self.response_output)
        self.output_nodes = [self.response_output]
        self.observed_input = WorkTreeNode(name='observed')
        self.input_nodes = [self.observed_input]

def get_preset_worker():
    PresetWorker = Worker('preset')
    PresetWorker.set_IO_for_level()
    PresetWorker.response_output.add_child(PresetWorker.observed_input)
    PresetWorker.response_output.evaluation = (lambda results: [r[1] for r in results][0])
    return PresetWorker


case_worker = Worker(name='case_worker')
const1 = WorkTreeNode(name='const1', evaluation=1)
const2 = WorkTreeNode(name='const2', evaluation=2)
const3 = WorkTreeNode(name='const3', evaluation=3)
adder = WorkTreeNodeMean(name='adder')


adder.add_children([const1, const2])
case_worker.work_tree.add_child(const3)
case_worker.work_tree.add_child(adder)

result = case_worker.work_tree.evaluate_work_tree()
print(next(result)[1])
print(case_worker.work_tree.to_dict())
json_output = json.dumps(case_worker.work_tree.to_dict(), indent=4)
print(json_output)
