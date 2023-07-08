# pylint: disable=singleton-comparison
"""
    Gift repository.
"""

from secrets import token_urlsafe

from app.database.repositories.base import BaseRepository
from app.database.models.gift import GiftRewardType, Gift


class GiftsRepository(BaseRepository):
    """
    Gift database CRUD repository.
    """

    @staticmethod
    def generate_promocode() -> str:
        """
        Generate standartized promocode for the new gift.
        """
        return token_urlsafe(nbytes=32)

    def get_by_promocode(self, promocode: str) -> Gift | None:
        """
        Get one gift by given promocode.
        """
        return self.db.query(Gift).filter(Gift.promocode == promocode).first()

    def get_by_id(self, gift_id: int) -> Gift | None:
        """
        Get one gift by given id.
        """
        return self.db.query(Gift).filter(Gift.id == gift_id).first()

    def create(
        self, reward_type: GiftRewardType, created_by: int, max_uses: int
    ) -> Gift:
        """
        Creates new Gift object that ready to use and have all required stuff (as promocode) generated.
        """
        gift = Gift(
            promocode=self.generate_promocode(32),
            created_by=created_by,
            max_uses=max_uses,
            reward=reward_type.value,
        )
        self.finish(gift)
        return gift
