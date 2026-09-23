"""Versioned domain-independent symbolic features. No implicit persistence."""
import json
import math
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Trait(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    name: str = Field(min_length=1, max_length=128)
    value: str | float | None
    unit: str = Field(default='category', max_length=64)

    @field_validator('value')
    @classmethod
    def finite_value(cls, value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Trait values must be finite; use None for unknown')
        return value


class Codon(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    schema_version: Literal['codon-v2'] = 'codon-v2'
    modality: Literal['traffic', 'sound', 'light', 'physics', 'generic']
    mapping_version: str = Field(min_length=1, max_length=128)
    traits: tuple[Trait, ...] = Field(min_length=1, max_length=64)

    @field_validator('traits')
    @classmethod
    def unique_traits(cls, traits):
        if len({t.name for t in traits}) != len(traits):
            raise ValueError('Duplicate trait names')
        return tuple(sorted(traits, key=lambda t: t.name))

    def token(self):
        return json.dumps(self.model_dump(mode='json'), sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode_legacy(token: str, modality='generic') -> Codon:
    """Preserve ambiguous legacy tokens without inventing trait boundaries."""
    if not isinstance(token, str) or not token or len(token) > 4096:
        raise ValueError('Invalid legacy codon')
    return Codon(modality=modality, mapping_version='legacy-opaque-v1', traits=(Trait(name='legacy_token', value=token),))


def validate_vector(vector, dimensions=18):
    values = list(vector)
    if len(values) != dimensions or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError(f'Expected {dimensions} finite numeric dimensions')
    return values
