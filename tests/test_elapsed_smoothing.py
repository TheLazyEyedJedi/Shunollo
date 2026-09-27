import math
import random
import pytest
from shunollo_core.physics.mechanics import VestibularDynamics
from shunollo_core.perception.count_image import encode_counts, decode_counts
from shunollo_core.perception.encoding import Codon, Trait

def test_legacy_recurrence_unchanged():
    engine=VestibularDynamics(damping=.85,time_constant=9)
    expected=0.
    for x in [1.,0.,-2.,.3]*30:
        expected=.85*expected+.15*x
        assert engine.integrate_acceleration(x)==pytest.approx(expected,abs=1e-14)

@pytest.mark.parametrize('rate',[1,20,100])
def test_elapsed_cadence_and_reference(rate):
    engine=VestibularDynamics(time_constant=.7)
    for _ in range(rate): value=engine.integrate_elapsed(1.,dt=1/rate)
    assert value==pytest.approx(1-math.exp(-1/.7),abs=1e-13)
    assert engine.damping==.85
    engine.reset()
    assert engine.integrate_elapsed(0.,dt=.1)==0

def test_irregular_partition_and_small_dt():
    engine=VestibularDynamics(time_constant=2)
    for dt in [.01,.07,.32,.6]: value=engine.integrate_elapsed(3.,dt=dt)
    assert value==pytest.approx(3*(1-math.exp(-.5)))
    fresh=VestibularDynamics(time_constant=1)
    assert fresh.integrate_elapsed(1.,dt=1e-20)>0

@pytest.mark.parametrize('x,dt,tau',[(float('nan'),1,1),(1,0,1),(1,-1,1),(1,float('inf'),1),(1,1,0),(True,1,1),(1,True,1)])
def test_invalid_does_not_mutate(x,dt,tau):
    engine=VestibularDynamics(time_constant=tau)
    before=(engine._velocity,list(engine._history))
    with pytest.raises(ValueError):engine.integrate_elapsed(x,dt=dt)
    assert (engine._velocity,engine._history)==before

def test_seeded_count_and_named_trait_roundtrips():
    rng=random.Random(1782)
    for n in [1,2,17,6000]:
        values=[rng.randrange(65536) for _ in range(n)]
        assert decode_counts(encode_counts(values),expected_bins=n)==values
    for v in [None,0.,-1.,1e-20,1e20,'unknown']:
        c=Codon(modality='generic',mapping_version='test-v1',traits=(Trait(name='x',unit='custom-unit',value=v),))
        assert Codon.model_validate_json(c.token())==c
