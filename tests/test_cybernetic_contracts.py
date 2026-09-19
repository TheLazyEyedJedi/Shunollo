import pytest
from shunollo_core.perception.encoding import Codon, Trait, decode_legacy
from shunollo_core.perception.meta_gene_layer import TraitMemory
from shunollo_core.feedback.training_loop import apply_feedback
from shunollo_core.memory.hippocampus import Hippocampus
from shunollo_core.perception import percept_genome
from shunollo_core.perception.codon_memory import get_codon_weight


def test_codon_weights_never_leak_between_adapters():
    class Adapter:
        def __init__(self, value):
            self.value=value
        def get_codon_weights(self, agent):
            return {'same':self.value}
    first,second=Adapter(.8),Adapter(1.2)
    assert get_codon_weight('Blue','same',first)==.8
    assert get_codon_weight('Blue','same',second)==1.2
    first.value=.9
    assert get_codon_weight('Blue','same',first)==.9


def test_structured_tokens_and_unknown():
    c = Codon(modality='sound', mapping_version='v1', traits=(Trait(name='a_b', value=None),))
    assert Codon.model_validate_json(c.token()) == c
    assert decode_legacy('high_pitch_loud').traits[0].value == 'high_pitch_loud'
    with pytest.raises(ValueError):
        Trait(name='x', value=float('nan'))


def test_feedback_isolation():
    a, b = TraitMemory(), TraitMemory()
    apply_feedback('Blue', 1, traits=['high_pitch'], memory=a)
    assert a.trait_profile('Blue') == {'high_pitch': 1}
    assert b.trait_profile('Blue') == {}


def test_genome_missing_adapter():
    with pytest.raises(ValueError):
        percept_genome.update_weights('test', ['x'], 1)
    assert percept_genome.get_weight('test', 'x') == 1


@pytest.mark.parametrize('vector', [[], [0]*17, [0]*19, [float('nan')]*18, [True]*18])
def test_recall_rejects_invalid_vectors_before_io(vector):
    hippo = object.__new__(Hippocampus)
    with pytest.raises(ValueError):
        hippo.recall_similar(vector)
