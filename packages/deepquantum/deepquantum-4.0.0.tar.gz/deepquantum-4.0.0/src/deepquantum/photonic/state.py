"""
Quantum states
"""

from typing import Any, List, Optional, Union

import torch
from torch import nn

import deepquantum.photonic as dqp
from .qmath import dirac_ket


class FockState(nn.Module):
    """A Fock state of n modes, including Fock basis states and Fock state tensors.

    Args:
        state (Any): The Fock state. It can be a vacuum state with ``'vac'`` or ``'zeros'``.
            It can be a Fock basis state, e.g., ``[1,0,0]``, or a Fock state tensor,
            e.g., ``[(1/2**0.5, [1,0]), (1/2**0.5, [0,1])]``. Alternatively, it can be a tensor representation.
        nmode (int or None, optional): The number of modes in the state. Default: ``None``
        cutoff (int or None, optional): The Fock space truncation. Default: ``None``
        basis (bool, optional): Whether the state is a Fock basis state or not. Default: ``True``
        den_mat (bool, optional): Whether to use density matrix representation. Only valid for Fock state tensor.
            Default: ``False``
    """
    def __init__(
        self,
        state: Any,
        nmode: Optional[int] = None,
        cutoff: Optional[int] = None,
        basis: bool = True,
        den_mat: bool = False
    ) -> None:
        super().__init__()
        self.basis = basis
        self.den_mat = den_mat
        if self.basis:
            if state in ('vac', 'zeros'):
                state = [0] * nmode
            # Process Fock basis state
            if not isinstance(state, torch.Tensor):
                state = torch.tensor(state, dtype=torch.long)
            else:
                state = state.long()
            if state.ndim == 1:
                state = state.unsqueeze(0)
            assert state.ndim == 2
            if nmode is None:
                nmode = state.shape[-1]
            if cutoff is None:
                cutoff = torch.max(torch.sum(state, dim=-1)).item() + 1
            self.nmode = nmode
            self.cutoff = cutoff
            batch, size = state.shape
            state_ts = torch.zeros([batch, nmode], dtype=torch.long, device=state.device)
            if nmode > size:
                state_ts[:, :size] = state[:, :]
            else:
                state_ts[:, :] = state[:, :nmode]
            state_ts = state_ts.squeeze(0)
            assert state_ts.max() < self.cutoff
        else:
            if state in ('vac', 'zeros'):
                state = [(1, [0] * nmode)]
            # Process Fock state tensor
            if isinstance(state, torch.Tensor):  # with the dimension of batch size
                if nmode is None:
                    if den_mat:
                        nmode = (state.ndim - 1) // 2
                    else:
                        nmode = state.ndim - 1
                if cutoff is None:
                    cutoff = state.shape[-1]
                self.nmode = nmode
                self.cutoff = cutoff
                state_ts = state
            else:
                # Process Fock state tensor from Fock basis states
                assert isinstance(state, list) and all(isinstance(i, tuple) for i in state)
                nphoton = 0
                # Determine the number of photons and modes
                for s in state:
                    nphoton = max(nphoton, sum(s[1]))
                    if nmode is None:
                        nmode = len(s[1])
                if cutoff is None:
                    cutoff = nphoton + 1
                self.nmode = nmode
                self.cutoff = cutoff
                state_ts = torch.zeros([self.cutoff] * self.nmode, dtype=torch.cfloat)
                # Populate Fock state tensor with the input Fock basis states
                for s in state:
                    amp = s[0]
                    fock_basis = tuple(s[1])
                    state_ts[fock_basis] = amp
                state_ts = state_ts.unsqueeze(0)  # add additional batch size
                if den_mat:
                    state_ts = state_ts.reshape([self.cutoff ** self.nmode, 1])
                    state_ts = (state_ts @ state_ts.mH).reshape([-1] + [self.cutoff] * 2 * self.nmode)
            if den_mat:
                assert state_ts.ndim == 2 * self.nmode + 1
            else:
                assert state_ts.ndim == self.nmode + 1
            assert all(i == self.cutoff for i in state_ts.shape[1:])
        self.register_buffer('state', state_ts)

    def __repr__(self) -> str:
        """Return a string representation of the ``FockState``."""
        if self.basis:
            # Represent Fock basis state as a string
            if self.state.ndim == 1:
                state_str = ''.join(map(str, self.state.tolist()))
                return f'|{state_str}>'
            else:
                temp = ''
                for i in range(self.state.shape[0]):
                    state_str = ''.join(map(str, self.state[i].tolist()))
                    temp += f'state_{i}: |{state_str}>\n'
                return temp
        else:
            # Represent Fock state tensor using Dirac notation
            ket_dict = dirac_ket(self.state)
            temp = ''
            for key, value in ket_dict.items():
                temp += f'{key}: {value}\n'
            return temp

    def __eq__(self, other: 'FockState') -> bool:
        """Check if two ``FockState`` instances are equal."""
        return all([self.nmode == other.nmode, self.state.equal(other.state)])

    def __hash__(self) -> int:
        """Compute the hash value for the ``FockState``."""
        if self.basis:
            # Hash Fock basis state as a string
            state_str = ''.join(map(str, self.state.tolist()))
            return hash(state_str)
        else:
            # Hash Fock state tensor using Dirac notation
            ket_dict = dirac_ket(self.state)
            temp = ''
            for key, value in ket_dict.items():
                temp += f'{key}: {value}\n'
            return hash(temp)

    def __lt__(self, other: 'FockState') -> bool:
        tuple_self = tuple(self.state.tolist())
        tuple_other = tuple(other.state.tolist())
        return tuple_self < tuple_other


class GaussianState(nn.Module):
    r"""A Gaussian state of n modes, representing by covariance matrix and displacement vector.

    Args:
        state (str or List): The Gaussian state. It can be a vacuum state with ``'vac'``, or arbitrary Gaussian states
            with [``cov``, ``mean``]. ``cov`` and ``mean`` are the covariance matrix and the displacement vector
            of the Gaussian state, respectively. Use ``xxpp`` convention and :math:`\hbar=2` by default.
            Default: ``'vac'``
        nmode (int or None, optional): The number of modes in the state. Default: ``None``
        cutoff (int, optional): The Fock space truncation. Default: 5
    """
    def __init__(
        self,
        state: Union[str, List] = 'vac',
        nmode: Optional[int] = None,
        cutoff: int = 5
    ) -> None:
        super().__init__()
        if state == 'vac':
            cov = torch.eye(2 * nmode) * dqp.hbar / (4 * dqp.kappa ** 2)
            mean = torch.zeros(2 * nmode, 1)
        elif isinstance(state, list):
            cov = state[0]
            mean = state[1]
            if not isinstance(cov, torch.Tensor):
                cov = torch.tensor(cov)
            if not isinstance(mean, torch.Tensor):
                mean = torch.tensor(mean)
            if nmode is None:
                nmode = cov.shape[-1] // 2
        cov = cov.reshape(-1, 2 * nmode, 2 * nmode)
        mean = mean.reshape(-1, 2 * nmode, 1)
        assert cov.ndim == mean.ndim == 3
        assert cov.shape[-2] == cov.shape[-1] == 2 * nmode, (
            'The shape of the covariance matrix should be (2*nmode, 2*nmode)')
        assert mean.shape[-2] == 2 * nmode, 'The length of the mean vector should be 2*nmode'
        self.register_buffer('cov', cov)
        self.register_buffer('mean', mean)
        self.nmode = nmode
        self.cutoff = cutoff
        self.is_pure = self.check_purity()

    def check_purity(self, rtol = 1e-5, atol = 1e-8):
        """Check if the Gaussian state is pure state

        See https://arxiv.org/pdf/quant-ph/0503237.pdf Eq.(2.5)
        """
        purity = 1 / torch.sqrt(torch.det(4 * dqp.kappa ** 2 / dqp.hbar * self.cov))
        unity = torch.tensor(1.0, dtype=purity.dtype, device=purity.device)
        return torch.allclose(purity, unity, rtol=rtol, atol=atol)
