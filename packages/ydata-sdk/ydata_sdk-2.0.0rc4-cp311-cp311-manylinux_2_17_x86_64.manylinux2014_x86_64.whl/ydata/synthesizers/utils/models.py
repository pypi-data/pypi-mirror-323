"""Synthesizer models enum definition."""
from enum import Enum

from ydata.__models._synthpop import SeqSynthpop, Synthpop


class RegularSynthesizerModel(Enum):
    SYNTHPOP = Synthpop

    def __call__(self, *args, **kwargs):
        return self.value(*args)


class TimeSeriesSynthesizerModel(Enum):
    SYNTHPOP = SeqSynthpop

    def __call__(self, *args, **kwargs):
        return self.value(*args)
