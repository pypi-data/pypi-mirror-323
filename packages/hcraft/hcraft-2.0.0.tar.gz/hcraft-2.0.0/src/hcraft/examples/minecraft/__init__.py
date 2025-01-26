"""# MineHcraft: Inspired from the popular game Minecraft.

<img src="https://raw.githubusercontent.com/IRLL/HierarchyCraft/master/docs/images/minehcraft_human_demo.gif" width=100%/>

A rather large and complex requirements graph:
<div class="graph">
.. include:: ../../../../docs/images/requirements_graphs/MineHcraft.html
</div>
"""

from typing import Optional

import hcraft.examples.minecraft.items as items
from hcraft.examples.minecraft.env import ALL_ITEMS, MineHcraftEnv

from hcraft.purpose import Purpose, RewardShaping
from hcraft.task import GetItemTask

MINEHCRAFT_GYM_ENVS = []
__all__ = ["MineHcraftEnv"]


# gym is an optional dependency
try:
    import gymnasium as gym

    ENV_PATH = "hcraft.examples.minecraft.env:MineHcraftEnv"

    # Simple MineHcraft with no reward, only penalty on illegal actions
    gym.register(
        id="MineHcraft-NoReward-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": None},
    )
    MINEHCRAFT_GYM_ENVS.append("MineHcraft-NoReward-v1")

    # Get all items, place all zones_items and go everywhere
    gym.register(
        id="MineHcraft-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": "all"},
    )
    MINEHCRAFT_GYM_ENVS.append("MineHcraft-v1")

    def _to_camel_case(name: str):
        return "".join([subname.capitalize() for subname in name.split("_")])

    def _register_minehcraft_single_item(
        item: items.Item,
        name: Optional[str] = None,
        success_reward: float = 10.0,
        timestep_reward: float = -0.1,
        reward_shaping: RewardShaping = RewardShaping.REQUIREMENTS_ACHIVEMENTS,
        version: int = 1,
    ):
        purpose = Purpose(timestep_reward=timestep_reward)
        purpose.add_task(
            GetItemTask(item, reward=success_reward),
            reward_shaping=reward_shaping,
        )
        if name is None:
            name = _to_camel_case(item.name)
        gym_name = f"MineHcraft-{name}-v{version}"
        gym.register(
            id=gym_name,
            entry_point=ENV_PATH,
            kwargs={"purpose": purpose},
        )
        MINEHCRAFT_GYM_ENVS.append(gym_name)

    replacement_names = {
        items.COBBLESTONE: "Stone",
        items.IRON_INGOT: "Iron",
        items.GOLD_INGOT: "Gold",
        items.ENDER_DRAGON_HEAD: "Dragon",
    }

    for item in ALL_ITEMS:
        cap_item_name = "".join([part.capitalize() for part in item.name.split("_")])
        item_id = replacement_names.get(item, cap_item_name)
        _register_minehcraft_single_item(item, name=item_id)


except ImportError:
    pass
