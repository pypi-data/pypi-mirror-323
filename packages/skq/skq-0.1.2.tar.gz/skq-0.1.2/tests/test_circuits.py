import numpy as np

from skq.circuits.circuit import Circuit, Concat
from skq.circuits.entangled_states import BellStates
from skq.gates.qubit import H, I


def test_circuit_basic_operation():
    """Test that a Circuit can execute a simple sequence of gates"""
    circuit = Circuit([H()])
    initial_state = np.array([1, 0])  # |0⟩ state
    result = circuit(initial_state)
    expected = np.array([1, 1]) / np.sqrt(2)  # |+⟩ state
    np.testing.assert_array_almost_equal(result, expected)


def test_concat_two_gates():
    """Test that Concat correctly combines two single-qubit gates"""
    concat = Concat([I(), I()])
    initial_state = np.array([1, 0, 0, 0])  # |00⟩ state
    result = concat.encodes(initial_state)
    expected = initial_state  # Should remain unchanged for identity gates
    np.testing.assert_array_almost_equal(result, expected)


def test_bell_state_omega_plus():
    """Test creation of the first Bell state (Φ+)"""
    bell = BellStates()
    circuit = bell.get_bell_state(1)
    initial_state = np.array([1, 0, 0, 0])  # |00⟩ state
    result = circuit(initial_state)
    expected = np.array([1, 0, 0, 1]) / np.sqrt(2)  # (|00⟩ + |11⟩)/√2
    np.testing.assert_array_almost_equal(result, expected)
