"""StateId machine stepper module.

This module provides the base `Stepper` and `StateMachine` classes for traversing state machines during parsing
and generation. Steppers track state transitions and maintain parsing history, while StateMachines manage the
constraints and transitions within the state machine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Self, TypeVar, overload

from pse_core import Edge, StateGraph, StateId

Logits = TypeVar("Logits")

class Engine(ABC):
    """
    The core engine class that manages the state machine and steppers.
    """

    def __init__(self, reverse_vocabulary: dict[int, str]) -> None: ...
    """Initialize the engine with a reverse vocabulary (a map of token ids to tokens). The token ids are the ids used by the model. The token string representation is the decoded string of the token id."""

    def __call__(self, scores: Logits) -> Logits: ...
    """Process logits scores and return the corrected logits."""

    @property
    def vocabulary(self) -> dict[str, int]: ...
    """The vocabulary (a map of tokens to token ids). The token string representation is the decoded string of the token id."""
    @property
    def reverse_vocabulary(self) -> dict[int, str]: ...
    """The reverse vocabulary (a map of token ids to tokens). The token string representation is the decoded string of the token id."""
    @property
    def multi_token_mapping(self) -> dict[int, list[int]]: ...
    """The multi token mapping (a map of token ids to lists of token ids). The token string representation is the decoded string of the token id."""
    @multi_token_mapping.setter
    def multi_token_mapping(self, value: dict[int, list[int]]) -> None: ...
    @property
    def has_reached_accept_state(self) -> bool: ...
    @property
    def within_json_value(self) -> bool: ...
    @property
    def is_encapsulated(self) -> bool: ...
    @is_encapsulated.setter
    def is_encapsulated(self, value: bool) -> None: ...
    @property
    def steppers(self) -> list[Stepper]: ...
    @steppers.setter
    def steppers(self, value: list[Stepper]) -> None: ...
    @abstractmethod
    def encode_token(self, token: str) -> list[int]: ...
    def process_logits(self, scores: Logits) -> Logits: ...
    """Process logits for a given input and scores"""

    def sample(
        self,
        log_probs: object,
        sampler: Callable[[object, dict[str, Any]], object],
        kwargs: dict[str, Any] | None = None,
    ) -> list[int]: ...
    """Sample a token from the given log probabilities using the provided sampler."""

    @overload
    def consume_tokens(self, token_ids: list[int]) -> list[int]: ...
    """
    Consume a list of tokens. Returns the advanced tokens, or an empty list if the tokens are not valid.

    If only some of the tokens are valid, only the valid tokens are consumed and returned.
    The invalid tokens are discarded.

    Args:
        token_ids: The list of token ids to consume.

    Returns:
        The list of advanced token ids, or an empty list if the tokens are not valid.
    """

    @overload
    def consume_tokens(self, token_id: int) -> list[int]: ...
    """
    Consume a single token. Returns the advanced tokens, or an empty list if the token is not valid.

    Args:
        token_id: The token id to consume.

    Returns:
        The list of advanced token ids, or an empty list if the token is not valid.
    """

    def consume_text(self, input: str) -> None: ...
    """
    Consume raw input and advance the engine.

    Args:
        input: The raw input to consume.
    """

    def get_trie(self) -> TrieSet: ...
    """
    Get the trie constructed from the vocabulary.

    Returns:
        The trie constructed from the vocabulary.
    """

class StateMachine:
    """
    A state machine that manages multiple steppers representing
    different valid states, enabling efficient traversal and minimizing backtracking.
    """

    def __init__(
        self,
        state_graph: StateGraph | None = None,
        start_state: StateId = 0,
        end_states: list[StateId] | None = None,
        is_optional: bool = False,
        is_case_sensitive: bool = True,
    ) -> None: ...
    @property
    def is_optional(self) -> bool:
        """Check if the state machine is optional."""
        ...

    @property
    def is_case_sensitive(self) -> bool:
        """Check if the state machine is case sensitive."""
        ...

    def get_new_stepper(self, state: StateId | None = None) -> Stepper:
        """Get a new stepper for this state machine."""
        ...

    def get_steppers(self, state: StateId | None = None) -> list[Stepper]:
        """Get steppers to traverse the state machine.

        Args:
            state: Optional starting state.

        Returns:
            A list of stepper instances.
        """
        ...

    def get_transitions(self, stepper: Stepper) -> list[tuple[Stepper, StateId]]:
        """Get transitions from the given stepper.

        Args:
            stepper: Stepper to get transitions from.

        Returns:
            A list of tuples containing a stepper, start state, and target state.
        """
        ...

    def get_edges(self, state: StateId) -> list[Edge]:
        """Get edges from the given state."""
        ...

    def branch_stepper(
        self, stepper: Stepper, token: str | None = None
    ) -> list[Stepper]:
        """Branch the stepper into multiple paths.

        Args:
            stepper: Stepper to branch.
            token: Optional token to consider.

        Returns:
            A list of branched steppers.
        """
        ...

    def advance_stepper(self, stepper: Stepper, token: str) -> list[Stepper]:
        """Advance the stepper with the given input token.

        Args:
            stepper: The stepper to advance.
            token: The input token to process.

        Returns:
            A list of updated steppers after advancement.
        """
        ...

    @staticmethod
    def advance_all_basic(steppers: list[Stepper], token: str) -> list[Stepper]:
        """Advance multiple steppers with a token."""
        ...

    @staticmethod
    def advance_all(
        steppers: list[Stepper],
        token: str,
        vocab: TrieSet | None = None,
        token_healing: bool = True,
        parallel: bool = False,
    ) -> list[tuple[Stepper, str, bool]]:
        """Advance multiple steppers with a token, supports token healing and parallel processing."""
        ...

    def __eq__(self, other: object) -> bool:
        """Check equality based on the state machine's state graph.

        Args:
            other: The object to compare with.

        Returns:
            True if both state machines are equal; False otherwise.
        """
        ...

    def __str__(self) -> str:
        """Return the string representation of the state machine."""
        ...

    def __repr__(self) -> str:
        """Return a detailed string representation of the state machine."""
        ...

    @property
    def start_state(self) -> StateId:
        """The start state of the state machine."""
        ...

    @start_state.setter
    def start_state(self, value: StateId) -> None: ...
    @property
    def end_states(self) -> list[StateId]:
        """The end states of the state machine."""
        ...

    @end_states.setter
    def end_states(self, value: list[StateId]) -> None: ...
    @property
    def state_graph(self) -> StateGraph:
        """The state transition graph."""
        ...

    @state_graph.setter
    def state_graph(self, value: StateGraph) -> None: ...

class Stepper:
    """
    Base class for state machine steppers.

    A `Stepper` represents a position in a state machine graph and manages transitions
    between states as input is consumed.

    It tracks the current state, transition history, and accumulated values during parsing or generation.
    """

    def __init__(self, state_machine: StateMachine, current_state: StateId | None = None) -> None:
        """Initialize the stepper.

        Args:
            state_machine: The state machine to associate with the stepper.
            current_state: The current state of the stepper.
        """
        ...
    def clone(self) -> Self:
        """Create a clone of the stepper.

        Returns:
            A new instance of the stepper with the same state.
        """
        ...

    def consume(self, token: str) -> list[Stepper]:
        """Advance the stepper with the given input token.

        Args:
            token: The token to process.

        Returns:
            A list of updated stepper instances after advancement.
        """
        ...

    def can_accept_more_input(self) -> bool:
        """Indicate whether the stepper can accept more input for the current state.

        Returns:
            True if the stepper can accept more input; False otherwise.
        """
        ...

    def is_within_value(self) -> bool:
        """Determine if the stepper is currently within a value.

        Returns:
            True if in a value; False otherwise.
        """
        ...

    def is_optional(self) -> bool:
        """Check if the stepper is optional."""
        ...

    def should_start_step(self, token: str) -> bool:
        """Determine if a stepper should start with the given input token.

        Args:
            token: The token to process.

        Returns:
            True if the stepper should start; False otherwise.
        """
        ...

    def should_complete_step(self) -> bool:
        """Determine if the stepper should complete.

        Returns:
            True if the stepper should complete; False otherwise.
        """
        ...

    def accepts_any_token(self) -> bool:
        """Check if the state machine accepts any token (i.e., free text).

        Returns:
            True if all tokens are accepted; False otherwise.
        """
        ...

    def get_valid_continuations(self, depth: int = 0) -> list[str]:
        """Return the set of strings that allow valid continuation from current state.

        Args:
            depth: The current depth in the state machine traversal.

        Returns:
            A list of strings that represent valid continuations from current state.
        """
        ...

    def has_reached_accept_state(self) -> bool:
        """Check if the stepper has reached an accepted (final) state.

        Returns:
            True if in an accepted state; False otherwise.
        """
        ...

    def add_to_history(self, stepper: Stepper) -> None:
        """Add the stepper to the accepted history."""
        ...

    def parse_value(self, value: str | None) -> Any:
        """Parse the accumulated value into an appropriate type.

        Args:
            value: The value to parse.

        Returns:
            The parsed value.
        """
        ...

    def start_step(
        self,
        sub_stepper: Stepper,
        target_state: StateId,
        token: str | None = None,
    ) -> Stepper | None:
        """Start a new transition with the given token.

        Args:
            sub_stepper: The stepper handling the current transition.
            target_state: The target state.
            token: Optional token to consider.

        Returns:
            A new stepper instance after starting the transition or None if not possible.
        """
        ...

    def complete_step(
        self,
        sub_stepper: Stepper,
    ) -> list[Stepper]:
        """Complete the current transition.

        Args:
            sub_stepper: The stepper handling the current transition.

        Returns:
            A list of new stepper instances.
        """
        ...

    def step(
        self,
        new_value: str | None = None,
        remaining_input: str | None = None,
    ) -> Stepper:
        """
        Step the stepper with the given input token.

        Args:
            new_value: The new value to set.
            remaining_input: The remaining input to set.
        """
        ...

    def should_branch(self) -> bool:
        """Check if the stepper should branch."""
        ...

    def branch(self, token: str | None = None) -> list[Stepper]:
        """Branch the current stepper into multiple paths.

        Args:
            token: Optional token to consider.

        Returns:
            A list of branched stepper instances.
        """
        ...

    def get_current_value(self) -> Any:
        """Retrieve the accumulated stepper value.

        Returns:
            The current value from transition or history, parsed into appropriate type.
            Returns None if no value is accumulated.
        """
        ...

    def get_raw_value(self) -> str:
        """Retrieve the raw accumulated value as a string.

        Returns:
            The concatenated raw values from history and transitions.
        """
        ...

    # Core properties
    @property
    def state_machine(self) -> StateMachine:
        """The state machine associated with this stepper."""
        ...
    @state_machine.setter
    def state_machine(self, value: StateMachine) -> None: ...

    @property
    def current_state(self) -> StateId:
        """The current state."""
        ...
    @current_state.setter
    def current_state(self, value: StateId) -> None: ...

    @property
    def target_state(self) -> StateId | None:
        """The target state."""
        ...
    @target_state.setter
    def target_state(self, value: StateId | None) -> None: ...

    # Sub-stepper and history
    @property
    def sub_stepper(self) -> Stepper | None:
        """The transition stepper."""
        ...
    @sub_stepper.setter
    def sub_stepper(self, value: Stepper | None) -> None: ...

    @property
    def accepted_history(self) -> list[Stepper]:
        """The history of accepted steppers."""
        ...
    @accepted_history.setter
    def accepted_history(self, value: list[Stepper]) -> None: ...

    # Input tracking
    @property
    def consumed_character_count(self) -> int:
        """The number of consumed characters."""
        ...
    @consumed_character_count.setter
    def consumed_character_count(self, value: int) -> None: ...

    @property
    def remaining_input(self) -> str | None:
        """The remaining input string."""
        ...
    @remaining_input.setter
    def remaining_input(self, value: str | None) -> None: ...

    # Value handling
    @property
    def _raw_value(self) -> str | None:
        """The raw accumulated value as a string."""
        ...
    @_raw_value.setter
    def _raw_value(self, value: str | None) -> None: ...

    # Magic methods
    def __eq__(self, other: object) -> bool:
        """Check equality based on the stepper's state and accumulated value.

        Args:
            other: The object to compare with.

        Returns:
            True if both steppers are equal; False otherwise.
        """
        ...

    def __str__(self) -> str:
        """Return the string representation of the stepper."""
        ...

    def __repr__(self) -> str:
        """Return a detailed string representation of the stepper."""
        ...

class TrieSet:
    """A HAT-trie based set implementation for efficient string storage and lookup.

    This class provides an efficient implementation of a set data structure
    specifically optimized for string keys using a HAT-trie structure.
    """

    def __init__(self, burst_threshold: int = 1024) -> None: ...
    """Initialize a new TrieSet.

    Args:
        burst_threshold: Optional threshold for the trie's burst operation.
    """

    def insert(self, key: str) -> None: ...
    """Insert a string into the set.

    Args:
        key: The string to insert.
    """

    def insert_all(self, keys: list[str]) -> TrieSet: ...
    """Insert multiple strings into the set.

    Args:
        keys: List of strings to insert.

    Returns:
        Self for method chaining.
    """

    def erase(self, key: str) -> int: ...
    """Remove a string from the set.

    Args:
        key: The string to remove.

    Returns:
        Number of elements removed (0 or 1).
    """

    def find(self, key: str) -> bool: ...
    """Check if a string exists in the set.

    Args:
        key: The string to look for.

    Returns:
        True if the string exists in the set, False otherwise.
    """

    @property
    def empty(self) -> bool: ...
    """Check if the set is empty.

    Returns:
        True if the set contains no elements, False otherwise.
    """

    @property
    def size(self) -> int: ...
    """Get the number of elements in the set.

    Returns:
        The number of strings stored in the set.
    """

    def clear(self) -> None: ...
    """Remove all elements from the set."""
