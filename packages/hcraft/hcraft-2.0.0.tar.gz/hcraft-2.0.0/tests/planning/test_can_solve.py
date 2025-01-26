from typing import TYPE_CHECKING, Type

import pytest
import pytest_check as check

import os


from hcraft.examples import EXAMPLE_ENVS
from hcraft.examples.minecraft import MineHcraftEnv
from hcraft.examples.minicraft import (
    MiniHCraftBlockedUnlockPickup,
)
from hcraft.env import HcraftEnv
from hcraft.examples.recursive import RecursiveHcraftEnv

if TYPE_CHECKING:
    from unified_planning.io import PDDLWriter


KNOWN_TO_FAIL_FOR_PLANNER = {
    "enhsp": [MiniHCraftBlockedUnlockPickup],
    "aries": [MiniHCraftBlockedUnlockPickup, RecursiveHcraftEnv],
}


@pytest.mark.slow
@pytest.mark.parametrize(
    "env_class", [env for env in EXAMPLE_ENVS if env != MineHcraftEnv]
)
@pytest.mark.parametrize("planner_name", ["enhsp", "aries"])
def test_solve_flat(env_class: Type[HcraftEnv], planner_name: str):
    up = pytest.importorskip("unified_planning")
    write = False
    env = env_class(max_step=200)
    problem = env.planning_problem(timeout=5, planner_name=planner_name)

    if write:
        writer: "PDDLWriter" = up.io.PDDLWriter(problem.upf_problem)
        pddl_dir = os.path.join("planning", "pddl", env.name)
        os.makedirs(pddl_dir, exist_ok=True)
        writer.write_domain(os.path.join(pddl_dir, "domain.pddl"))
        writer.write_problem(os.path.join(pddl_dir, "problem.pddl"))

    optional_requirements = {"enhsp": "up_enhsp", "aries": "up_aries"}
    pytest.importorskip(optional_requirements[planner_name])

    if env_class in KNOWN_TO_FAIL_FOR_PLANNER[planner_name]:
        pytest.xfail(f"{planner_name} planner is known to fail on {env.name}")

    done = False
    _observation, _info = env.reset()
    while not done:
        action = problem.action_from_plan(env.state)
        _observation, _reward, terminated, truncated, _info = env.step(action)
        done = terminated or truncated
    check.is_true(
        env.purpose.terminated, msg=f"Plans failed they were :{problem.plans}"
    )
