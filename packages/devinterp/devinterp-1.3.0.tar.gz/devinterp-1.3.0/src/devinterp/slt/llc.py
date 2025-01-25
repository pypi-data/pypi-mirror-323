import os
import warnings
from typing import Union

import torch
from devinterp.slt.callback import SamplerCallback
from devinterp.utils import TPU_TYPE, USE_TPU_BACKEND


class LLCEstimator(SamplerCallback):
    r"""
    Callback for estimating the Local Learning Coefficient (LLC) in a rolling fashion during a sampling process.
    It calculates the LLC based on the average loss across draws for each chain:

    $$LLC = \textrm{n \beta} * (\textrm{avg_loss} - \textrm{init_loss})$$

    For use with :func:`devinterp.slt.sampler.sample`.


    :param num_draws: Number of samples to draw (should be identical to :python:`num_draws` passed to :python:`devinterp.slt.sampler.sample`)
    :type num_draws: int
    :param num_chains: Number of chains to run (should be identical to :python:`num_chains` passed to :python:`devinterp.slt.sampler.sample`)
    :type num_chains: int
    :param nbeta: Effective Inverse Temperature, float (default: 1., set by sample() to utils.default_nbeta(dataloader)=len(batch_size)/np.log(len(batch_size)))
    :type nbeta: int
    :param device: Device to perform computations on, e.g., 'cpu' or 'cuda'. Supports GPUs and TPUs.
    To use TPUs, be sure to pass in torch_xla.core.xla_model.xla_device() as the device and set the USE_TPU_BACKEND environment flag to "1". Default is 'cpu'
    :type device: str | torch.device, optional
    """

    def __init__(
        self,
        num_chains: int,
        num_draws: int,
        init_loss: torch.Tensor,
        device: Union[torch.device, str] = "cpu",
        eval_field: str = "loss",
        nbeta: float = None,
        temperature: float = None,
    ):
        self.num_chains = num_chains
        self.num_draws = num_draws
        self.losses = torch.zeros((num_chains, num_draws), dtype=torch.float32).to(
            device
        )
        self.init_loss = init_loss

        assert (
            nbeta is not None or temperature is not None
        ), "Please provide a value for nbeta."
        if nbeta is None and temperature is not None:
            nbeta = temperature
            warnings.warn("Temperature is deprecated. Please use nbeta instead.")
        self.nbeta = torch.tensor(nbeta, dtype=torch.float32).to(device)
        self.temperature = temperature

        self.device = device
        self.eval_field = eval_field

    def update(self, chain: int, draw: int, loss: torch.tensor):
        if torch.isnan(loss).any():
            raise RuntimeError(f"NaN detected in loss at chain {chain}, draw {draw}")
        self.losses[chain, draw] = loss.to(self.device)

    def finalize(self):
        if os.environ.get("USE_SPMD", "0") == "1" and not str(self.device).startswith(
            "cpu:"
        ):
            # no need to reduce if we're using SPMD
            pass
        elif USE_TPU_BACKEND and str(self.device).startswith("xla:"):
            import torch_xla.core.xla_model as xm

            if TPU_TYPE == "v4":
                self.losses = xm.all_reduce(xm.REDUCE_SUM, self.losses)
            elif TPU_TYPE == "v2/v3":
                self.losses = self.losses.cpu()
                if torch.distributed.is_initialized():
                    torch.distributed.all_reduce(self.losses)
                else:
                    warnings.warn(
                        "torch.distributed has not been initialized. If running on TPU v2/v3, and you want to run chains in parallel, you need to initialize torch.distributed after calling xmp.spawn() as follows:"
                        ">>> import torch_xla.runtime as xr"
                        ">>> store = torch.distributed.TCPStore('127.0.0.1', 12345, 4, xr.global_ordinal() == 0)"
                        ">>> torch.distributed.init_process_group(backend='gloo', store=store, rank=xr.global_ordinal()//2, world_size=xr.world_size()//2)"
                    )

            else:
                raise NotImplementedError(f"TPU type {TPU_TYPE} not supported")
        elif str(self.device).startswith(
            "cuda"
        ):  # if we've ran on multi-GPU, we should do a reduce as well. see above for how this would work
            try:
                torch.distributed.all_reduce(self.losses)
            except ValueError:
                pass
        avg_losses = self.losses.mean(axis=1)
        # bypass automatic bfloat16 issues
        if os.environ.get("XLA_USE_BF16", "0") == "1" and str(self.device).startswith(
            "xla:"
        ):
            self.llc_per_chain = self.nbeta.to(device="cpu", dtype=torch.float32) * (
                avg_losses.to(device="cpu", dtype=torch.float32)
                - self.init_loss.to(device="cpu", dtype=torch.float32)
            )
        else:
            self.llc_per_chain = self.nbeta * (avg_losses - self.init_loss)
        self.llc_mean = self.llc_per_chain.mean()
        self.llc_std = self.llc_per_chain.std()

    def get_results(self):
        """
        :returns: A dict :python:`{"llc/mean": llc_mean, "llc/std": llc_std, "llc-chain/{i}": llc_trace_per_chain, "loss/trace": loss_trace_per_chain}`. (Only after running :python:`devinterp.slt.sampler.sample(..., [llc_estimator_instance], ...)`).
        """
        return {
            "llc/mean": self.llc_mean.cpu().numpy().item(),
            "llc/std": self.llc_std.cpu().numpy().item(),
            **{
                f"llc-chain/{i}": self.llc_per_chain[i].cpu().numpy().item()
                for i in range(self.num_chains)
            },
            "loss/trace": self.losses.cpu().numpy(),
        }

    def __call__(self, chain: int, draw: int, **kwargs):
        self.update(chain, draw, kwargs[self.eval_field])


class OnlineLLCEstimator(SamplerCallback):
    """
    Callback for estimating the Local Learning Coefficient (LLC) in an online fashion during a sampling process.
    It calculates LLCs using the same formula as :func:`devinterp.slt.llc.LLCEstimator`, but continuously and including means and std across draws (as opposed to just across chains).
    For use with :func:`devinterp.slt.sampler.sample`.

    :param num_draws: Number of samples to draw (should be identical to :python:`num_draws` passed to :python:`devinterp.slt.sampler.sample`)
    :type num_draws: int
    :param num_chains: Number of chains to run (should be identical to :python:`num_chains` passed to :python:`devinterp.slt.sampler.sample`)
    :type num_chains: int
    :param nbeta: Effective Inverse Temperature, float (default: 1., set by sample() to utils.default_nbeta(dataloader)=len(batch_size)/np.log(len(batch_size)))
    :type nbeta: int
    :param device: Device to perform computations on, e.g., 'cpu' or 'cuda'. Supports GPUs and TPUs. \
    To use TPUs, be sure to pass in torch_xla.core.xla_model.xla_device() as the device and set the USE_TPU_BACKEND environment flag to "1". Default is 'cpu'
    :type device: str | torch.device, optional
    """

    def __init__(
        self,
        num_chains: int,
        num_draws: int,
        init_loss,
        device="cpu",
        eval_field="loss",
        nbeta: float = None,
        temperature: float = None,  # Temperature is deprecated
    ):
        self.num_chains = num_chains
        self.num_draws = num_draws
        self.init_loss = init_loss

        self.losses = torch.zeros((num_chains, num_draws), dtype=torch.float32).to(
            device
        )
        self.llcs = torch.zeros((num_chains, num_draws), dtype=torch.float32).to(device)

        self.losses = torch.zeros((num_chains, num_draws)).to(device)
        self.llcs = torch.zeros((num_chains, num_draws)).to(device)
        assert (
            nbeta is not None or temperature is not None
        ), "Please provide a value for nbeta."
        if nbeta is None and temperature is not None:
            nbeta = temperature
            warnings.warn("Temperature is deprecated. Please use nbeta instead.")
        self.nbeta = torch.tensor(nbeta, dtype=torch.float32).to(device)
        self.temperature = temperature

        self.device = device
        self.eval_field = eval_field

    def update(self, chain: int, draw: int, loss: torch.tensor):
        if torch.isnan(loss).any():
            raise RuntimeError(f"NaN detected in loss at chain {chain}, draw {draw}")
        loss = loss.to(self.device)
        self.losses[chain, draw] = loss
        self.llcs[chain, draw] = self.nbeta * (loss - self.init_loss)

    def finalize(self):
        # TODO
        self.llc_means = self.llcs.mean(dim=0)
        self.llc_stds = self.llcs.std(dim=0)

    def get_results(self):
        """
        :returns: A dict :python:`{"llc/means": llc_means, "llc/stds": llc_stds, "llc/trace": llc_trace_per_chain, "loss/trace": loss_trace_per_chain}`. (Only after running :python:`devinterp.slt.sampler.sample(..., [llc_estimator_instance], ...)`).
        """
        return {
            "init_loss": self.init_loss,
            "llc/means": self.llc_means.cpu().numpy(),
            "llc/stds": self.llc_stds.cpu().numpy(),
            "llc/trace": self.llcs.cpu().numpy(),
            "loss/trace": self.losses.cpu().numpy(),
        }

    def __call__(self, chain: int, draw: int, **kwargs):
        self.update(chain, draw, kwargs[self.eval_field])
