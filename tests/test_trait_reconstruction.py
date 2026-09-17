import copy
import pytest
from shunollo_core.perception import meta_gene_layer as traits


def test_default_api_starts_empty_and_can_adapt_without_storage():
    traits.reconstruct_state()
    assert traits.summary('observer')['top_traits'] == []
    traits.adapt('observer', ['steady'])
    assert traits.trait_profile('observer') == {'steady': 1}
    traits.deprecate('observer', ['steady'])
    assert traits.trait_profile('observer') == {'steady': 0}
    traits.reconstruct_state()


def test_explicit_snapshot_is_idempotent_and_not_mutated():
    snapshot = {'observer': {'warm_bright': {'count': 3, 'weight': 0.6}, 'warm_soft': {'count': 2}}}
    before = copy.deepcopy(snapshot)
    memory = traits.TraitMemory()
    memory.reconstruct_state(snapshot)
    assert memory.trait_profile('observer') == {'warm': 5, 'bright': 3, 'soft': 2}
    memory.adapt('observer', ['new'])
    memory.reconstruct_state(snapshot)
    assert memory.summary('observer')['trait_count'] == 3
    assert snapshot == before


def test_separate_hosts_do_not_share_trait_state():
    first, second = traits.TraitMemory(), traits.TraitMemory()
    first.adapt('observer', ['one'])
    second.adapt('observer', ['two'])
    first.reconstruct_state()
    assert first.trait_profile('observer') == {}
    assert second.trait_profile('observer') == {'two': 1}


@pytest.mark.parametrize('stats', [{'weight': 0.9}, {'count': -1}, {'count': True}, {'count': 1.5}])
def test_invalid_reconstruction_preserves_previous_state(stats):
    memory = traits.TraitMemory()
    memory.adapt('observer', ['existing'])
    with pytest.raises(ValueError):
        memory.reconstruct_state({'observer': {'valid': {'count': 3}, 'invalid': stats}})
    assert memory.trait_profile('observer') == {'existing': 1}


def test_invalid_adaptation_is_atomic_and_profiles_are_copies():
    memory = traits.TraitMemory()
    memory.adapt('observer', ['existing'])
    with pytest.raises(ValueError):
        memory.adapt('observer', ['valid', None])
    profile = memory.trait_profile('observer')
    profile['existing'] = 100
    assert memory.trait_profile('observer') == {'existing': 1}
