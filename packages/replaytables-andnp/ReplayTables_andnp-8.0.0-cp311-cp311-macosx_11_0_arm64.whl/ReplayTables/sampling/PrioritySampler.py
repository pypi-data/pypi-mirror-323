import numpy as np
from typing import Any

from discrete_dists.mixture import MixtureDistribution, SubDistribution
from discrete_dists.proportional import Proportional
from discrete_dists.uniform import Uniform

from ReplayTables.interface import LaggedTimestep, Batch, StorageIdx, StorageIdxs
from ReplayTables.sampling.IndexSampler import IndexSampler

class PrioritySampler(IndexSampler):
    def __init__(
        self,
        rng: np.random.Generator,
        max_size: int,
        uniform_probability: float,
    ) -> None:
        super().__init__(rng, max_size)

        self._target.update_support(self._max_size)

        self._uniform = Uniform(0)
        self._p_dist = Proportional(self._max_size)
        self._dist = MixtureDistribution([
            SubDistribution(d=self._p_dist, p=1 - uniform_probability),
            SubDistribution(d=self._uniform, p=uniform_probability)
        ])

    def replace(self, idx: StorageIdx, transition: LaggedTimestep, /, **kwargs: Any) -> None:
        idxs = np.array([idx], dtype=np.int64)

        priority: float = kwargs['priority']
        priorities = np.array([priority])
        self._uniform.update(idxs)
        self._p_dist.update(idxs, priorities)

    def update(self, idxs: StorageIdxs, batch: Batch, /, **kwargs: Any) -> None:
        priorities = kwargs['priorities']
        self._uniform.update(idxs)
        self._p_dist.update(idxs, priorities)

    def isr_weights(self, idxs: StorageIdxs):
        return self._dist.isr(self._target, idxs)

    def sample(self, n: int) -> StorageIdxs:
        idxs: Any = self._dist.sample(self._rng, n)
        return idxs

    def stratified_sample(self, n: int) -> StorageIdxs:
        idxs: Any = self._dist.stratified_sample(self._rng, n)
        return idxs

    def mask_sample(self, idx: StorageIdx):
        idxs = np.array([idx], dtype=np.int64)
        zero = np.zeros(1)

        self._p_dist.update(idxs, zero)

    def total_priority(self):
        return self._p_dist.tree.total()
