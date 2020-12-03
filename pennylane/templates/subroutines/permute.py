# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""
Contains the ``permute`` template.
"""
import numpy as np

import pennylane as qml

# pylint: disable-msg=too-many-branches,too-many-arguments,protected-access
from pennylane.templates.decorator import template
from pennylane.wires import Wires


@template
def Permute(permutation, wires):
    r"""Permutes a set of wires into a new order.

    Args:
        permutation (list): A list of wire labels that represents the new ordering of wires
            after the permutation. The list may consist of integers or strings, so long as
            they match the labels of the wires.
        wires (Iterable or Wires): Wires that the template acts on. Accepts an iterable of numbers
            or strings, or a Wires object.

    Raises:
        ValueError: if inputs do not have the correct format

    .. UsageDetails::

        As a simple example, suppose we have a 5-qubit tape with wires labeled
        by the integers `[0, 1, 2, 3, 4]`. We apply a permutation to shuffle the
        order to `[4, 2, 0, 1, 3]` (i.e., the qubit state that was previously on
        wire 4 is now on wire 0, the one from 2 is on wire 1, etc.).


        .. code-block:: python

            import pennylane as qml
            from pennylane.templates import Permute

            with qml.tape.QuantumTape() as tape:
                # RZs added to ensure numerical ordering in drawing
                for wire in range(5):
                    qml.RZ(0, wires=wire)
                Permute([4, 2, 0, 1, 3], wires=[0, 1, 2, 3, 4])


        produces the following circuit:

        .. code-block:: python

           0: ──RZ(0)─────────╭SWAP────────────────┤
           1: ──RZ(0)──╭SWAP──│────────────────────┤
           2: ──RZ(0)──╰SWAP──│──────╭SWAP─────────┤
           3: ──RZ(0)─────────│──────│──────╭SWAP──┤
           4: ──RZ(0)─────────╰SWAP──╰SWAP──╰SWAP──┤


        `Permute` can also be applied to wires with arbitrary labels, like so:

        .. code-block:: python

            wire_labels = [3, 2, "a", 0, "c"]

            with qml.tape.QuantumTape() as tape:
                # RZs added to ensure numerical ordering in drawing
                for wire in range(5):
                    qml.RZ(0, wires=wire)
                Permute(["c", 3, "a", 2, 0], wires=wire_labels)

        The permuted circuit is:

        .. code-block:: python

            3: ──RZ(0)──╭SWAP────────────────┤
            2: ──RZ(0)──│──────╭SWAP─────────┤
            a: ──RZ(0)──│──────│─────────────┤
            0: ──RZ(0)──│──────│──────╭SWAP──┤
            c: ──RZ(0)──╰SWAP──╰SWAP──╰SWAP──┤

        Finally, it is also possible to permute a subset of wires by
        specifying a subset of labels. For example,

        .. code-block:: python

           wire_labels = [3, 2, "a", 0, "c"]

            with qml.tape.QuantumTape() as tape:
                # Create 5 wires
                for wire in range(num_wires):
                    qml.RZ(0, wires=wire)

                # Only permute the order of 3 of them
                Permute(["c", 2, 0], wires=[2, 0, "c"])

        will permute only the second, third, and fifth wires as follows:

        .. code-block:: python

            3: ──RZ(0)────────────────┤
            2: ──RZ(0)──╭SWAP─────────┤
            a: ──RZ(0)──│─────────────┤
            0: ──RZ(0)──│──────╭SWAP──┤
            c: ──RZ(0)──╰SWAP──╰SWAP──┤



    """

    wires = Wires(wires)

    if len(wires) <= 1:
        raise ValueError(f"Permutations must involve at least 2 qubits.")

    # Make sure the length of the things are the same
    if len(permutation) != len(wires):
        raise ValueError("Permutation must specify outcome of all wires.")

    # Make sure everything in the permutation has an associated label in wires
    for label in permutation:
        if label not in wires.labels:
            raise ValueError(f"Cannot permute wire {label} not present in wire set.")

    # Temporary storage to keep track as we permute
    working_order = list(wires.labels)

    # Go through the new order and shuffle things one by one
    for idx_here, here in enumerate(permutation):
        if working_order[idx_here] != here:
            # Where do we need to send the qubit at this location?
            idx_there = working_order.index(permutation[idx_here])

            # SWAP based on the labels of the wires
            qml.SWAP(wires=[wires.labels[idx_here], wires.labels[idx_there]])

            # Update the working order to account for the SWAP
            working_order[idx_here], working_order[idx_there] = (
                working_order[idx_there],
                working_order[idx_here],
            )
