# pylint: disable=singleton-comparison
"""
    Gift repository.
"""

from secrets import token_urlsafe
from app.database.models.gift import Gift, GiftRewardType
from app.database.repositories.base import BaseRepository


class GiftsRepository(BaseRepository):
    """
    Gift database CRUD repository.
    TODO: get_by_reward_type
    TODO: get_inactive, get_active
    TODO: get_used_max_times
    """

    @staticmethod
    def generate_promocode() -> str:
        """Returns generated promocode for gift."""
        return token_urlsafe(nbytes=32)

    def get_by_promocode(self, promocode: str) -> Gift | None:
        """Returns gift by promocode."""
        return self.db.query(Gift).filter(Gift.promocode == promocode).first()

    def get_by_id(self, gift_id: int) -> Gift | None:
        """Returns gift by id."""
        return self.db.query(Gift).filter(Gift.id == gift_id).first()

    def create(
        self, reward_type: GiftRewardType, created_by: int, max_uses: int
    ) -> Gift:
        """Creates new Gift object that is committed in the database already and have all required stuff (as promocode) generated."""

        promocode = self.generate_promocode(32)
        gift = Gift(
            promocode=promocode,
            created_by=created_by,
            max_uses=max_uses,
            reward=reward_type.value,
        )
        self.db.add(gift)
        self.db.commit()
        self.db.refresh(gift)
        return gift
