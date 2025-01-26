from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv

MINICRAFT_NAME = "MultiRoom"
__doc__ = MiniCraftEnv.description(MINICRAFT_NAME, for_module_header=True)


class MiniHCraftMultiRoom(MiniCraftEnv):
    MINICRAFT_NAME = MINICRAFT_NAME
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, n_rooms: int = 6, **kwargs) -> None:
        self.rooms = [Zone(f"Room {i + 1}") for i in range(n_rooms)]
        self.task = GetItemTask(self.GOAL)
        super().__init__(
            self.MINICRAFT_NAME,
            purpose=self.task,
            start_zone=self.rooms[0],
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []
        find_goal = Transformation(
            "Find goal",
            inventory_changes=[Yield(CURRENT_ZONE, self.GOAL, max=0)],
            zone=self.rooms[-1],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            "Reach goal",
            inventory_changes=[
                Use(CURRENT_ZONE, self.GOAL, consume=1),
                Yield(PLAYER, self.GOAL),
            ],
        )
        transformations.append(reach_goal)

        for i, room in enumerate(self.rooms):
            connected_rooms: List[Zone] = []
            if i > 0:
                connected_rooms.append(self.rooms[i - 1])
            if i < len(self.rooms) - 1:
                connected_rooms.append(self.rooms[i + 1])
            for connected_room in connected_rooms:
                transformations.append(
                    Transformation(
                        f"Go to {room.name} from {connected_room.name}",
                        destination=room,
                        zone=connected_room,
                    )
                )

        return transformations
