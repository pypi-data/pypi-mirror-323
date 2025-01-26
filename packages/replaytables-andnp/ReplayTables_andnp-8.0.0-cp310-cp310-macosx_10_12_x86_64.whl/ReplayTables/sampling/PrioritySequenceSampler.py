import numpy as np

from dataclasses import dataclass
from typing import Any, Set

from discrete_dists.distribution import Support
from discrete_dists.mixture import MixtureDistribution, SubDistribution
from discrete_dists.proportional import Proportional
from discrete_dists.uniform import Uniform
from discrete_dists.utils.SumTree import SumTree

from ReplayTables.sampling.IndexSampler import IndexSampler
from ReplayTables.storage.Storage import Storage
from ReplayTables.ingress.IndexMapper import IndexMapper
from ReplayTables.interface import Batch, LaggedTimestep, StorageIdx, StorageIdxs, TransIds
from ReplayTables._utils.jit import try2jit
from ReplayTables.sampling.tools import back_sequence

class PrioritySequenceSampler(IndexSampler):
    def __init__(
        self,
        rng: np.random.Generator,
        max_size: int,
        uniform_probability: float,
        trace_decay: float,
        trace_depth: int,
        combinator: str,
    ) -> None:
        super().__init__(rng, max_size)

        self._target.update_support(self._max_size)

        self._terminal = set[int]()
        # numba needs help with type inference
        # so add a dummy value to the set
        self._terminal.add(-1)

        self._uniform_prob = uniform_probability
        self._c = PSDistributionConfig(
            trace_decay=trace_decay,
            trace_depth=trace_depth,
            combinator=combinator,
        )

    def deferred_init(self, storage: Storage, mapper: IndexMapper):
        super().deferred_init(storage, mapper)

        self._ps_dist = PrioritizedSequenceDistribution(self._max_size, self._c, self._storage, self._mapper)

        self._uniform = Uniform(0)
        self._dist = MixtureDistribution(dists=[
            SubDistribution(d=self._ps_dist, p=1 - self._uniform_prob),
            SubDistribution(d=self._uniform, p=self._uniform_prob)
        ])

    def replace(self, idx: StorageIdx, transition: LaggedTimestep, /, **kwargs: Any) -> None:
        self._terminal.discard(int(idx))
        if transition.terminal:
            self._terminal.add(int(idx))

        priority: float = kwargs['priority']
        self._uniform.update_single(idx)
        self._ps_dist.update_single(idx, priority)

    def update(self, idxs: StorageIdxs, batch: Batch, /, **kwargs: Any) -> None:
        priorities = kwargs['priorities']
        self._uniform.update(idxs)
        self._ps_dist.update_seq(batch.trans_id, idxs, priorities, terminal=self._terminal)

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

        self._ps_dist.update(idxs, zero)

    def total_priority(self):
        return self._ps_dist.tree.total()

@dataclass
class PSDistributionConfig:
    trace_decay: float
    trace_depth: int
    combinator: str

class PrioritizedSequenceDistribution(Proportional):
    def __init__(
        self,
        support: Support | int,
        config: PSDistributionConfig,
        storage: Storage,
        mapper: IndexMapper,
    ):
        super().__init__(support)

        self._c: PSDistributionConfig = config
        assert self._c.combinator in ['max', 'sum']

        self._storage = storage
        self._mapper = mapper

        # pre-compute and cache this
        self._trace = np.cumprod(np.ones(self._c.trace_depth) * self._c.trace_decay)

    def update_seq(self, tids: TransIds, idxs: StorageIdxs, priorities: np.ndarray, terminal: Set[int]):
        b_eids: Any = back_sequence(tids, self._c.trace_depth)

        b_idxs = self._mapper.get_storage_idxs(b_eids)
        idx_mask = _term_sequence(b_idxs, terminal) | (~self._mapper.has_transitions(b_eids))

        u_idx, u_priorities = _get_priorities(
            self.tree,
            b_idxs,
            idx_mask,
            self._trace,
            priorities,
            comb=self._c.combinator,
        )

        u_idx = np.concatenate((idxs, u_idx), axis=0, dtype=np.int64)
        u_priorities = np.concatenate((priorities, u_priorities), axis=0)

        self.tree.update(u_idx, u_priorities)


@try2jit()
def _term_sequence(idxs: np.ndarray, term: Set[int]):
    assert len(idxs.shape) == 2

    out = np.empty(idxs.shape, dtype=np.bool_)
    for i in range(idxs.shape[0]):
        has_term = False
        for j in range(idxs.shape[1]):
            has_term = has_term or (idxs[i, j] in term)
            out[i, j] = has_term

    return out

def _get_priorities(tree: SumTree, idxs: np.ndarray, masks: np.ndarray, traces: np.ndarray, priorities: np.ndarray, comb: str):
    depth = len(traces)
    out_idxs = np.empty(depth * len(idxs), dtype=np.int64)
    out = np.empty(depth * len(idxs), dtype=np.float64)

    def c(a: float, b: float):
        if comb == 'sum':
            return a + b
        return max(a, b)

    k = 0
    for i in range(idxs.shape[0]):
        for j in range(depth):
            if masks[i, j]: continue

            idx = idxs[i, j]
            prior = tree.get_value(idx)
            new = c(prior, traces[j] * priorities[i])

            out_idxs[k] = idx
            out[k] = new
            k += 1

    return out_idxs[:k], out[:k]
