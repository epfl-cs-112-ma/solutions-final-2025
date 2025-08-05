from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import auto, Enum
from typing import Callable, Final

import re

# Question 1

class ResourceKind(Enum):
    MONEY = auto()
    PLANTS = auto()
    ENERGY = auto()
    HEAT = auto()

# Certaines copies ont voulu utiliser un tuple[int, int] à la place d'une
# classe Resource dédiée. Cela ne fonctionnait pas, car il faut pouvoir
# modifier individuellement la quanité et la production.
# (1 ou 2 copies ont fait cela mais ont malgré tout bien géré le remplacement
# du tuple complet à chaque fois ; c'était correct, mais fastidieux.)
@dataclass
class Resource:
    amount: int
    production: int

class Corporation:
    resources: Final[dict[ResourceKind, Resource]]
    forests: int

    # __init__ n'était normalement pas évaluée
    def __init__(self) -> None:
        self.resources = {kind:Resource(0, 0) for kind in ResourceKind}
        self.forests = 0

    # Question 2
    def start_turn(self) -> None:
        # 1. Transfer energy to heat
        self.resources[ResourceKind.HEAT].amount += self.resources[ResourceKind.ENERGY].amount
        self.resources[ResourceKind.ENERGY].amount = 0

        # 2. Apply productions
        # Dans cette version, on peut élégamment itérer sur les Resource's.
        for resource in self.resources.values():
            resource.amount += resource.production

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

class ResourceAction(Action):
    # Remarquez qu'il n'était pas correct d'utiliser une __resource: Resource ici.
    # En effet, une même Action doit pouvoir être appliquée à n'importe quelle
    # Corporation. Or, on ne connaît la bonne Corporation que dans `apply`.
    __resource_kind: Final[ResourceKind]
    __is_amount: Final[bool]
    __change: Final[int]

    # __init__ standard
    def __init__(self, resource_kind: ResourceKind, is_amount: bool, change: int) -> None:
        super().__init__()
        self.__resource_kind = resource_kind
        self.__is_amount = is_amount
        self.__change = change

    # Question 4
    def apply(self, corporation: Corporation) -> None:
        resource = corporation.resources[self.__resource_kind]
        if self.__is_amount:
            resource.amount += self.__change
        else:
            resource.production += self.__change

# Question 4

def apply_actions(corporation: Corporation, actions: Iterable[Action]) -> None:
    for action in actions:
        action.apply(corporation)

# Question 5

RESOURCE_STR_TO_KIND: Final[Mapping[str, ResourceKind]] = {
    kind.name.lower():kind for kind in ResourceKind
}

# L'usage d'une expression régulière suffisamment détaillée permettait de gérer
# les cas d'erreur entièrement en un seul matching.
# On n'a pas été très regardant sur la syntaxe exacte des expressions régulières
# (notamment le \ dans [+\-], qui est nécessaire pour que - ne soit pas
# considéré comme un marqueur d'intervalle).
AMOUNT_PROD_ACTION_RE = re.compile(r"(money|plants|energy|heat) (amount|production) ([+\-][0-9]+)")

def load_actions(action_strs: list[str]) -> list[Action]:
    return [load_action(action_str) for action_str in action_strs]

def load_action(action_str: str) -> Action:
    if action_str == "build forest":
        return BuildForestAction()
    elif result := AMOUNT_PROD_ACTION_RE.fullmatch(action_str):
        resource_kind = RESOURCE_STR_TO_KIND[result.group(1)]
        is_amount = result.group(2) == "amount"
        change = int(result.group(3))
        return ResourceAction(resource_kind, is_amount, change)
    else:
        raise ValueError("not a valid action")

# Question 6

# Dans cette variante, il y a malheureusement plus à écrire.
# C'est attendu, puisque les questions étaient conçues pour diriger le design
# vers un ADT.

class Requirement:
    pass

    @abstractmethod
    def test(self, corporation: Corporation, global_params: GlobalParams) -> bool:
        ...

class OKReq(Requirement):
    def test(self, corporation: Corporation, global_params: GlobalParams) -> bool:
        return True

class GlobalParamReq(Requirement):
    parameter: Final[GlobalParam]
    is_max: Final[bool]
    threshold: Final[int]

    # __init__ standard
    def __init__(self, parameter: GlobalParam, is_max: bool, threshold: int) -> None:
        super().__init__()
        self.parameter = parameter
        self.is_max = is_max
        self.threshold = threshold

    def test(self, corporation: Corporation, global_params: GlobalParams) -> bool:
        param_value = global_params[self.parameter]
        if self.is_max:
            return param_value <= self.threshold
        else:
            return param_value >= self.threshold

class ForestReq(Requirement):
    is_max: Final[bool]
    threshold: Final[int]

    # __init__ standard
    def __init__(self, is_max: bool, threshold: int) -> None:
        super().__init__()
        self.is_max = is_max
        self.threshold = threshold

    def test(self, corporation: Corporation, global_params: GlobalParams) -> bool:
        if self.is_max:
            return corporation.forests <= self.threshold
        else:
            return corporation.forests >= self.threshold

class AndOrReq(Requirement):
    is_and: Final[bool]
    left: Final[Requirement]
    right: Final[Requirement]

    # __init__ standard
    def __init__(self, is_and: bool, left: Requirement, right: Requirement) -> None:
        super().__init__()
        self.is_and = is_and
        self.left = left
        self.right = right

    def test(self, corporation: Corporation, global_params: GlobalParams) -> bool:
        left_test = self.left.test(corporation, global_params)
        right_test = self.right.test(corporation, global_params)
        if self.is_and:
            return left_test and right_test
        else:
            return left_test or right_test # copier-coller

# Question 7

def test_requirement(
    requirement: Requirement,
    corporation: Corporation,
    global_params: GlobalParams
) -> bool:
    return requirement.test(corporation, global_params)

# Question 8

def relax_requirement(requirement: Requirement) -> Requirement:
    match requirement:
        case OKReq() | ForestReq():
            return requirement
        case GlobalParamReq():
            new_threshold = requirement.threshold + 2 if requirement.is_max else requirement.threshold - 2
            return GlobalParamReq(requirement.parameter, requirement.is_max, new_threshold)
        case AndOrReq():
            new_left = relax_requirement(requirement.left)
            new_right = relax_requirement(requirement.right)
            return AndOrReq(requirement.is_and, new_left, new_right)

        # Ici nous avons un problème, puisqu'on ne peut pas garantir l'exhaustivité
        case _:
            raise AssertionError(f"Unknown requirement: {repr(requirement)}")

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
    param.name.lower():param for param in GlobalParam
}

def parse_requirement(text: str) -> Requirement:
    def make_comparison(left: str, cmp_str: str, right: str) -> Requirement:
        # On n'a pas été très regardant sur l'implémentation de cette fonction
        is_max = cmp_str == "<="
        threshold = int(right)
        if left == "player_forests":
            return ForestReq(is_max, threshold)
        else:
            return GlobalParamReq(STR_TO_GLOBAL_PARAM[left], is_max, threshold)

    # Sur papier, on s'attendait à quelque chose comme :
    #return parse(
    #    text,
    #    OKReq(),
    #    make_comparison,
    #    make_and=lambda left, right: AndOrReq(True, left, right),
    #    make_or=lambda left, right: AndOrReq(False, left, right), # copier-coller
    #)

    # En pratique, mypy est un peu trop rigide avec le code ci-dessus, et donc
    # sur machine il faut en fait écrire :
    ok: Requirement = OKReq()
    return parse(
        text,
        ok,
        make_comparison,
        make_and=lambda left, right: AndOrReq(True, left, right),
        make_or=lambda left, right: AndOrReq(False, left, right), # copier-coller
    )
