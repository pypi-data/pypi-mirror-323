import numpy as np

from ..base import Operator


class Circuit(list):
    """Run multiple gates in sequence."""
    def encodes(self, x):
        for gate in self:
            x = gate.encodes(x)
        return x

    def decodes(self, x):
        for gate in reversed(self):
            x = gate.decodes(x)
        return x
    
    def __call__(self, x):
        return self.encodes(x)


class Concat:
    """
    Combine multiple gates into a single gate.
    :param gates: List of gates to concatenate.
    """

    def __init__(self, gates: list[Operator]):
        assert len(gates) > 1, "Concat must have at least 2 gates."
        assert all(isinstance(g, Operator) for g in gates), "All gates must be instances of Operator."
        self.gates = gates
        self.encoding_matrix = np.kron(*[g for g in gates])

    def encodes(self, x: np.ndarray) -> np.ndarray:
        """
        Concatenate 2 or more gates.

        :param x: Quantum state to encode.
        :return: Quantum state after encoding.
        """
        return x @ self.encoding_matrix

    def decodes(self, x: np.ndarray) -> np.ndarray:
        """
        Reverse propagation for all gates.

        :param x: Quantum state to decode.
        :return: Quantum state after decoding.
        """
        for g in reversed(self.gates):
            x = x @ np.kron(g.conj().T, np.eye(len(x) // g.shape[0]))
        return x

    def __call__(self, x):
        return self.encodes(x)
