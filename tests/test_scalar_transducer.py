from datetime import datetime,timezone
import math
import pytest
from shunollo_core.interfaces import BaseTransducer
from shunollo_core.models import ShunolloSignal
from shunollo_core.perception.generic_transducer import ScalarTransducer


def test_public_contract_and_existing_sensory_consumers(tmp_path):
    from shunollo_core.perception.visual_cortex import synthesize_visual_event
    t=ScalarTransducer('sensor',value_scale=10)
    a=t.ingest(-5,1000);b=t.ingest(5,1002)
    assert isinstance(t,BaseTransducer) and isinstance(b,ShunolloSignal)
    assert a.timestamp==datetime.fromtimestamp(1000,timezone.utc)
    assert b.frequency==.5 and b.flux==.5
    assert len(b.to_vector())==18 and all(math.isfinite(x) for x in b.to_vector())
    assert b.metadata['sound']['volume']>=0
    assert b.metadata['light']['hue']==b.hue*360
    assert synthesize_visual_event(b.metadata,output_dir=str(tmp_path))


def test_temporal_order_changes_metrics():
    a,b=ScalarTransducer('a'),ScalarTransducer('a')
    for v,ta,tb in zip([10,10,10,10],[0,2,4,6],[0,.5,4,6]):
        sa,sb=a.ingest(v,ta),b.ingest(v,tb)
    assert sa.energy==sb.energy
    assert sa.metadata['physics']['jitter_seconds']==0
    assert sb.metadata['physics']['jitter_seconds']>0
    assert sa.harmony>sb.harmony


def test_isolation_reset_and_bounded_history():
    a,b=ScalarTransducer('same',2),ScalarTransducer('same',2)
    for i in range(5):a.ingest(i,i)
    assert len(a.value_buffer)==2 and len(b.value_buffer)==0
    a.reset()
    assert a.ingest(2,0)==b.ingest(2,0)


@pytest.mark.parametrize('value,timestamp',[(float('nan'),2),(1,float('inf')),(True,2),(1,0),(1,1e100)])
def test_invalid_observation_does_not_change_state(value,timestamp):
    t=ScalarTransducer('test');t.ingest(0,0)
    with pytest.raises(ValueError):t.ingest(value,timestamp)
    assert list(t.value_buffer)==[0] and list(t.time_buffer)==[0]


def test_normalization_clipping_is_fixed_and_explicit():
    t=ScalarTransducer('s',value_scale=10)
    a=t.ingest(1e200,0);b=t.ingest(-1e200,1)
    assert a.energy==b.energy==1
    assert b.metadata['normalization']['clipped_samples']==2
    assert all(math.isfinite(x) for x in b.to_vector())
    assert not a.metadata['temporal_available']
    with pytest.raises(ValueError):ScalarTransducer('bad',1)
    with pytest.raises(ValueError):ScalarTransducer('bad',value_scale=0)


def test_neural_query_exposes_scalar_classification(monkeypatch):
    from shunollo_core.learning import synaptic_plasticity as learning
    from shunollo_core.brain.neural_net import LinearAssociativeMemory
    from shunollo_core.brain.autoencoder import Autoencoder
    brain=LinearAssociativeMemory(reservoir_size=8)
    imagination=Autoencoder()
    monkeypatch.setattr(learning,'get_brain',lambda:brain)
    monkeypatch.setattr(learning,'get_imagination',lambda:imagination)
    result=learning.query_neural_intuition([.1]*18)
    assert type(result['classification_score']) is float
    assert result['classification_score']==.5
    assert 0<=result['anomaly_score']<=1
