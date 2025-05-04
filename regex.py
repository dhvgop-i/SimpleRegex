from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass
    
    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")

    def __bool__(self):
        return True


class StartState(State):

    def __init__(self):
        self.next_states: list[State] = []

    def check_self(self, char):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return super().check_self(char)

    def __bool__(self):
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        self.next_states: list[State] = []
        self.stared = False

    def check_self(self, char: str):
        return char.isascii()

    def __str__(self):
        return 'DotState'


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        self.next_states: list[State] = []
        self.symbol = symbol
        self.stared = False

    def check_self(self, char: str) -> State | Exception:
        return char == self.symbol

    def __str__(self):
        return f'AsciiState: {self.symbol}'

class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state: State = StartState()
        prev_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state)
            if tmp_next_state:
                prev_state.next_states.append(tmp_next_state)
                prev_state = tmp_next_state
        prev_state.next_states.append(TerminationState())
        if prev_state.stared:
            prev_state.next_states.append(prev_state)

        prev_state = self.curr_state
        while prev_state:
            n = prev_state.next_states[0]
            if n and n is n.next_states[0]:
                prev_state = n.next_states[1]
                continue
            if not n:
                break
            prev_state.next_states.extend(self.find_next(prev_state))
            try:
                if prev_state.stared:
                    prev_state.next_states.append(prev_state)
            except AttributeError:
                pass
            prev_state = n

    def find_next(self, state, d = False):
        next_ = state.next_states[0]
        r = [] if not d else [next_]
        if not next_:
            return [next_]
        if not next_.stared:
            return r
        if next_.stared and not next_.next_states[0]:
            return [next_.next_states[0]] if not d else [next_, next_.next_states[0]]
        return r + self.find_next(next_, d=True)

    def __init_next_state(
        self, next_token: str, prev_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                prev_state.stared = True
                # here you have to think, how to do it.

            case next_token if next_token == "+":
                new_state = prev_state

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def print_automata(self):
        curr = self.curr_state
        while curr:
            print(curr, curr.next_states)
            curr = curr.next_states[0] if curr is not curr.next_states[0] else curr.next_states[1]

    def check_string(self, s):
        def dfs(index: int, state: State) -> bool:
            if index == len(s):
                return any(not next_state for next_state in state.next_states)

            char = s[index]
            results = []

            for next_state in state.next_states:
                if next_state.check_self(char):
                    results.append(dfs(index + 1, next_state))

                try:
                    if next_state.stared and next_state.check_self(char):
                        results.append(dfs(index + 1, next_state))
                        for after_star in next_state.next_states:
                            if after_star.check_self(s[index + 1]) if index + 1 < len(s) else False:
                                results.append(dfs(index + 2, after_star))
                except (IndexError, AttributeError):
                    pass

            return any(results)

        return dfs(0, self.curr_state)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
