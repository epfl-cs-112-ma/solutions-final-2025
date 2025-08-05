from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import auto, Enum
from typing import Callable, Final

# Question 1

class ResourceKind(Enum):
    MONEY = auto()
    PLANTS = auto()
    ENERGY = auto()
    HEAT = auto()

class Corporation:
    amounts: Final[dict[ResourceKind, int]]
    productions: Final[dict[ResourceKind, int]]
    forests: int

    # __init__ n'était normalement pas évaluée
    def __init__(self) -> None:
        self.amounts = {kind:0 for kind in ResourceKind}
        self.productions = {kind:0 for kind in ResourceKind}
        self.forests = 0

    # Question 2
    def start_turn(self) -> None:
        # 1. Transfer energy to heat
        self.amounts[ResourceKind.HEAT] += self.amounts[ResourceKind.ENERGY]
        self.amounts[ResourceKind.ENERGY] = 0

        # 2. Apply productions
        # Astuce : on peut directement itérer sur un Enum.
        # Si on ne le sait pas, on aurait aussi pu avoir une liste globale des
        # ResourceKind, qui se définit en une ligne.
        for kind in ResourceKind:
            self.amounts[kind] += self.productions[kind]

class GlobalParam(Enum):
    OXYGEN = auto()
    TEMPERATURE = auto()
    OCEANS = auto()

type GlobalParams = dict[GlobalParam, int]

# Question 3

class Action:
    # Question 4
    @abstractmethod
    def apply(self, corporation: Corporation) -> None:
        ...

class BuildForestAction(Action):
    # Question 4
    def apply(self, corporation: Corporation) -> None:
        corporation.forests += 1

# L'autre solution combine les deux classes ci-dessous en une seule,
# avec un __is_amount: bool. Sur un examen papier, cela fait moins à écrire.

class ResourceAmountAction(Action):
    __resource_kind: Final[ResourceKind]
    __change: Final[int]

    # __init__ standard
    def __init__(self, resource_kind: ResourceKind, change: int) -> None:
        super().__init__()
        self.__resource_kind = resource_kind
        self.__change = change

    # Question 4
    def apply(self, corporation: Corporation) -> None:
        corporation.amounts[self.__resource_kind] += self.__change

class ResourceProductionAction(Action):
    __resource_kind: Final[ResourceKind]
    __change: Final[int]

    # __init__ standard
    def __init__(self, resource_kind: ResourceKind, change: int) -> None:
        super().__init__()
        self.__resource_kind = resource_kind
        self.__change = change

    # Question 4
    def apply(self, corporation: Corporation) -> None:
        corporation.productions[self.__resource_kind] += self.__change

# Question 4

def apply_actions(corporation: Corporation, actions: Iterable[Action]) -> None:
    for action in actions:
        action.apply(corporation)

# Question 5

RESOURCE_STR_TO_KIND: Final[Mapping[str, ResourceKind]] = {
    "money": ResourceKind.MONEY,
    "plants": ResourceKind.PLANTS,
    "energy": ResourceKind.ENERGY,
    "heat": ResourceKind.HEAT,
}

def load_actions(action_strs: list[str]) -> list[Action]:
    return [load_action(action_str) for action_str in action_strs]

def load_action(action_str: str) -> Action:
    match action_str.split():
        case ["build", "forest"]:
            return BuildForestAction()

        case [resource_str, "amount", change_str]:
            resource_kind = RESOURCE_STR_TO_KIND[resource_str] # KeyError if not a valid resource
            change = int(change_str) # ValueError if not a valid integer
            # Cette variante accepte "3" autant que "+3", ce qui est un peu plus
            # permissif que ce que spécifie l'énoncé. Cela était cependant accepté.
            return ResourceAmountAction(resource_kind, change)

        case [resource_str, "production", change_str]:
            # La même chose que ci-dessus, mais condensé en une ligne
            return ResourceProductionAction(RESOURCE_STR_TO_KIND[resource_str], int(change_str))

        case _:
            # ValueError explicite dans tous les autres cas
            raise ValueError("not a valid action")

# Question 6

# Un booléen était acceptable aussi, à la place de Comparator
class Comparator(Enum):
    LE = auto() # <=
    GE = auto() # >=

type Requirement = OKReq | GlobalParamReq | ForestReq | AndReq | OrReq

@dataclass(frozen=True)
class OKReq:
    pass

@dataclass(frozen=True)
class GlobalParamReq:
    parameter: GlobalParam
    comparator: Comparator
    threshold: int

@dataclass(frozen=True)
class ForestReq:
    comparator: Comparator
    threshold: int

@dataclass(frozen=True)
class AndReq:
    left: Requirement
    right: Requirement

# copier-coller
@dataclass(frozen=True)
class OrReq:
    left: Requirement
    right: Requirement

# Question 7

def compare(x: int, comparator: Comparator, y: int) -> bool:
    match comparator:
        case Comparator.LE: return x <= y
        case Comparator.GE: return x >= y

def test_requirement(
    requirement: Requirement,
    corporation: Corporation,
    global_params: GlobalParams
) -> bool:
    match requirement:
        case OKReq():
            return True
        case GlobalParamReq(parameter, comparator, threshold):
            return compare(global_params[parameter], comparator, threshold)
        case ForestReq(comparator, threshold):
            return compare(corporation.forests, comparator, threshold)
        case AndReq(left, right):
            return test_requirement(left, corporation, global_params) \
                and test_requirement(right, corporation, global_params)

        # copier-coller
        case OrReq(left, right):
            return test_requirement(left, corporation, global_params) \
                or test_requirement(right, corporation, global_params)

# Question 8

def relax_requirement(requirement: Requirement) -> Requirement:
    match requirement:
        case OKReq() | ForestReq():
            return requirement
        case GlobalParamReq(parameter, Comparator.LE, threshold):
            return GlobalParamReq(parameter, Comparator.LE, threshold + 2)
        case GlobalParamReq(parameter, _, threshold): # ou Comparator.GE
            return GlobalParamReq(parameter, Comparator.GE, threshold - 2)
        case AndReq(left, right):
            return AndReq(relax_requirement(left), relax_requirement(right))

        # copier-coller
        case OrReq(left, right):
            return OrReq(relax_requirement(left), relax_requirement(right))

# Question 9

def parse_not_generic(
    text: str,
    ok: Requirement,
    make_comparison: Callable[[str, str, str], Requirement],
    make_and: Callable[[Requirement, Requirement], Requirement],
    make_or: Callable[[Requirement, Requirement], Requirement], # copier-coller
) -> Requirement:
    raise NotImplementedError() # ...

def parse[T](
    text: str,
    ok: T,
    make_comparison: Callable[[str, str, str], T],
    make_and: Callable[[T, T], T],
    make_or: Callable[[T, T], T], # copier-coller
) -> T:
    raise NotImplementedError() # ...

STR_TO_GLOBAL_PARAM: Final[Mapping[str, GlobalParam]] = {
    "oxygen": GlobalParam.OXYGEN,
    "temperature": GlobalParam.TEMPERATURE,
    "oceans": GlobalParam.OCEANS,
}

def parse_requirement(text: str) -> Requirement:
    def make_comparison(left: str, cmp_str: str, right: str) -> Requirement:
        # On n'a pas été très regardant sur l'implémentation de cette fonction
        comparator = Comparator.LE if cmp_str == "<=" else Comparator.GE
        threshold = int(right)
        if left == "player_forests":
            return ForestReq(comparator, threshold)
        else:
            return GlobalParamReq(STR_TO_GLOBAL_PARAM[left], comparator, threshold)

    # Sur papier, on s'attendait à quelque chose comme :
    #return parse(
    #    text,
    #    OKReq(),
    #    make_comparison,
    #    make_and=lambda left, right: AndReq(left, right),
    #    make_or=lambda left, right: OrReq(left, right), # copier-coller
    #)

    # En pratique, mypy est un peu trop rigide avec le code ci-dessus, et donc
    # sur machine il faut en fait écrire :
    ok: Requirement = OKReq()
    return parse(
        text,
        ok,
        make_comparison,
        make_and=lambda left, right: AndReq(left, right),
        make_or=lambda left, right: OrReq(left, right), # copier-coller
    )
