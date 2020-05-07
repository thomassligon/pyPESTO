"""
This is for testing the pypesto.model_selection.
"""
import tempfile
import numpy as np
from pypesto.model_selection import (
    ModelSelector,
    ModelSelectionProblem,
    unpack_file
)

import petab

from typing import Dict, Set

# TODO move to constants file
INITIAL_VIRTUAL_MODEL = 'PYPESTO_INITIAL_MODEL'

# def test_model_selection():
#    # model_selection.tsv
#    petab_problem = None
#    model_selection = ModelSelection(petab_problem, 'model_selection.tsv')
#    # sm = model_selection.get_smallest_order_problem()
#    res = model_selection.forward_selection()

# def test_select_model():
#    petab_problem = None
#    model_specification_file = 'model_selection.tsv'
#    selector = ModelSelector(petab_problem, model_specification_file)
#    result = selector.select('forward', 'AIC')


ms_file_text = '''ModelId\tSBML\tp1\tp2\tp3
m0\tsbml1.xml\t0;5;-\t0;-\t-
m1\tsbml1.xml\t0\t-\t-
m2\tsbml2.xml\t3;-\t-\t-
m3\tsbml2.xml\t-\t0;2\t-
'''

ms_file_unpacked_text_expected = '''ModelId\tSBML\tp1\tp2\tp3
m0_0\tsbml1.xml\t0\t0\tnan
m0_1\tsbml1.xml\t0\tnan\tnan
m0_2\tsbml1.xml\t5\t0\tnan
m0_3\tsbml1.xml\t5\tnan\tnan
m0_4\tsbml1.xml\tnan\t0\tnan
m0_5\tsbml1.xml\tnan\tnan\tnan
m1_0\tsbml1.xml\t0\tnan\tnan
m2_0\tsbml2.xml\t3\tnan\tnan
m2_1\tsbml2.xml\tnan\tnan\tnan
m3_0\tsbml2.xml\tnan\t0\tnan
m3_1\tsbml2.xml\tnan\t2\tnan
'''


#def test_ms_file_unpacking():
#    ms_file = tempfile.NamedTemporaryFile(mode='r+', delete=False)
#    with open(ms_file.name, 'w') as f:
#        f.write(ms_file_text)
#    ms_file_unpacked = unpack_file(ms_file.name)
#    print(ms_file_unpacked.read())
#    print(ms_file_text_unpacked)
#    # assert str(ms_file_unpacked.read()) == ms_file_text_unpacked
#    selector = ModelSelector(None, ms_file_unpacked.name)
#    # assert False, selector.header


#def test_get_next_step_candidates():
#    ms_file = tempfile.NamedTemporaryFile(mode='r+', delete=False)
#    with open(ms_file.name, 'w') as f:
#        f.write(ms_file_text)
#    selector = ModelSelector(None, ms_file.name)
#    model_list = [model for model in selector.model_generator()]
#    result, selection_history = selector.select('forward', 'AIC')
#    print(selection_history)

#def test_get_next_step_candidates():
#    ms_file = tempfile.NamedTemporaryFile(mode='r+', delete=False)
#    with open(ms_file.name, 'w') as f:
#        f.write(ms_file_text)
#    print('YES')
#    ms_file_unpacked = unpack_file(ms_file.name)
#    # may need to ms_file_unpacked.seek(0) after this
#    print('YES2')
#    assert ms_file_unpacked.read() == ms_file_unpacked_text_expected
#    selector = ModelSelector(None, ms_file_unpacked.name)
#    selector.select('forward', 'AIC')
#    #assert False, selector.header

def models_compared_with(model_id0: str,
                         selection_history: Dict[str, Dict])-> Set[str]:
    model_ids = set()
    for model_id, model_info in selection_history.items():
        print('Checking if {model_id0} compared with {model_id}')
        if model_info['compared_model_id'] == model_id0:
            model_ids.add(model_id)
    return model_ids


def test_pipeline_forward():
    petab_problem_yaml = \
        'doc/example/model_selection/example_modelSelection.yaml'
    model_specifications_file = (
        'doc/example/model_selection/'
        'modelSelectionSpecification_example_modelSelection.tsv')
    petab_problem = petab.Problem.from_yaml(petab_problem_yaml)
    selector = ModelSelector(petab_problem, model_specifications_file)
    model_list = [model for model in selector.model_generator()]
    result, selection_history = selector.select('forward', 'AIC')
    for model in selection_history:
        print(f'{model}: {selection_history[model]}')
    print(models_compared_with(INITIAL_VIRTUAL_MODEL, selection_history))
    assert models_compared_with(INITIAL_VIRTUAL_MODEL, selection_history) == \
        {'M5_0', 'M6_0', 'M7_0'}
    # M5_0 is selected after PYPESTO_INITIAL_MODEL by virtue of being the first
    # in the specifications file (M5_0, M6_0, and M7_0 all have the same AIC)
    print(models_compared_with('M5_0', selection_history))
    assert models_compared_with('M5_0', selection_history) == \
        {'M2_0', 'M4_0'}

def test_pipeline_backward():
    petab_problem_yaml = \
        'doc/example/model_selection/example_modelSelection.yaml'
    model_specifications_file = (
        'doc/example/model_selection/'
        'modelSelectionSpecification_example_modelSelection.tsv')
    petab_problem = petab.Problem.from_yaml(petab_problem_yaml)
    selector = ModelSelector(petab_problem, model_specifications_file)
    model_list = [model for model in selector.model_generator()]
    result, selection_history = selector.select('backward', 'AIC')
    for model in selection_history:
        print(f'{model}: {selection_history[model]}')
    print(models_compared_with(INITIAL_VIRTUAL_MODEL, selection_history))
    # TODO currently skips the actual first model `M1_0` as the first model
    # matches the virtual model PYPESTO_INITIAL_MODEL. Will be fixed when
    # `self.initial_model` is implemented.
    assert models_compared_with(INITIAL_VIRTUAL_MODEL, selection_history) == \
        {'M2_0', 'M3_0', 'M4_0'}
    print(models_compared_with('M3_0', selection_history))
    assert models_compared_with('M3_0', selection_history) == \
        {'M6_0', 'M7_0'}
