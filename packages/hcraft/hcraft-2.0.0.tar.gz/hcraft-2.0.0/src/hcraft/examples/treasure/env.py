from pathlib import Path
from typing import List

from hcraft.elements import Item, Zone
from hcraft.env import HcraftEnv
from hcraft.purpose import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE
from hcraft.world import world_from_transformations


class TreasureEnv(HcraftEnv):
    """A simple environment used in for the env building tutorial."""

    TREASURE_ROOM = Zone("treasure_room")
    """Room containing the treasure."""
    KEY_ROOM = Zone("key_room")
    """Where all the keys are stored."""
    START_ROOM = Zone("start_room")
    """Where the player starts."""

    CHEST = Item("treasure_chest")
    """Treasure chest containing gold."""
    LOCKED_CHEST = Item("locked_chest")
    """Treasure chest containing gold ... but it's locked."""
    GOLD = Item("gold")
    """Gold! well the pixel version at least."""
    KEY = Item("key")
    """A key ... it can probably unlock things."""

    def __init__(self, **kwargs) -> None:
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=self.START_ROOM,
            start_zones_items={self.TREASURE_ROOM: [self.LOCKED_CHEST]},
        )
        world.resources_path = Path(__file__).parent / "resources"
        super().__init__(
            world, purpose=GetItemTask(self.GOLD), name="TreasureHcraft", **kwargs
        )

    def _build_transformations(self) -> List[Transformation]:
        TAKE_GOLD_FROM_CHEST = Transformation(
            "take-gold-from-chest",
            inventory_changes=[
                Use(CURRENT_ZONE, self.CHEST, consume=1),
                Yield(PLAYER, self.GOLD),
            ],
        )

        SEARCH_KEY = Transformation(
            "search-key",
            inventory_changes=[
                Yield(PLAYER, self.KEY, max=1),
            ],
            zone=self.KEY_ROOM,
        )

        UNLOCK_CHEST = Transformation(
            "unlock-chest",
            inventory_changes=[
                Use(PLAYER, self.KEY, 2),
                Use(CURRENT_ZONE, self.LOCKED_CHEST, consume=1),
                Yield(CURRENT_ZONE, self.CHEST),
            ],
        )

        MOVE_TO_KEY_ROOM = Transformation(
            "move-to-key_room",
            destination=self.KEY_ROOM,
            zone=self.START_ROOM,
        )
        MOVE_TO_TREASURE_ROOM = Transformation(
            "move-to-treasure_room",
            destination=self.TREASURE_ROOM,
            zone=self.START_ROOM,
        )
        MOVE_TO_START_ROOM = Transformation(
            "move-to-start_room",
            destination=self.START_ROOM,
        )

        return [
            TAKE_GOLD_FROM_CHEST,
            SEARCH_KEY,
            UNLOCK_CHEST,
            MOVE_TO_KEY_ROOM,
            MOVE_TO_TREASURE_ROOM,
            MOVE_TO_START_ROOM,
        ]
