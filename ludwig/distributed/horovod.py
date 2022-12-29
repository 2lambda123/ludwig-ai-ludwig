import contextlib
from typing import Any, Callable, Optional

import torch
from torch import nn
from torch.optim import Optimizer

import horovod.torch as hvd
from horovod.torch.optimizer import _DistributedOptimizer

from ludwig.distributed.base import DistributedStrategy
from ludwig.utils.horovod_utils import gather_all_tensors, is_distributed_available


class HorovodStrategy(DistributedStrategy):
    def __init__(self):
        hvd.init()

    def wrap_model(self, model: nn.Module) -> nn.Module:
        return model

    def wrap_optimizer(self, optimizer: Optimizer, model: nn.Module) -> Optimizer:
        return hvd.DistributedOptimizer(
            optimizer,
            named_parameters=model.named_parameters(),
        )

    def size(self) -> int:
        return hvd.size()

    def rank(self) -> int:
        return hvd.rank()

    def local_size(self) -> int:
        return hvd.local_size()

    def local_rank(self) -> int:
        return hvd.local_rank()

    def barrier(self):
        return hvd.allreduce(torch.as_tensor([0], dtype=torch.int))

    def allreduce(self, t: torch.Tensor) -> torch.Tensor:
        return hvd.allreduce(t)

    def broadcast(self, t: torch.Tensor) -> torch.Tensor:
        return hvd.broadcast(t, root_rank=0)

    def sync_model(self, model: nn.Module):
        hvd.broadcast_parameters(model.state_dict(), root_rank=0)

    def sync_optimizer(self, optimizer: Optimizer):
        hvd.broadcast_optimizer_state(optimizer, root_rank=0)

    def broadcast_object(self, v: Any) -> Any:
        return hvd.broadcast_object(v)

    def wait_optimizer_synced(self, optimizer: _DistributedOptimizer):
        optimizer.synchronize()

    @contextlib.contextmanager
    def prepare_optimizer_update(self, optimizer: _DistributedOptimizer):
        with optimizer.skip_synchronize():
            yield

    @classmethod
    def is_available(cls) -> bool:
        return is_distributed_available()

    @classmethod
    def gather_all_tensors_fn(cls) -> Optional[Callable]:
        return gather_all_tensors

    @classmethod
    def get_ray_trainer_name(cls) -> Optional[str]:
        return "horovod"

    def shutdown(self):
        hvd.shutdown()
