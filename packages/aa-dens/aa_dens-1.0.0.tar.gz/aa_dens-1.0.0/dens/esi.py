"""Esi related functions"""

from esi.clients import EsiClientProvider

from allianceauth.services.hooks import get_extension_logger

from . import __version__
from .models import DenOwner

MERCENARY_DENS_TYPE_IDS = [
    85230,
    85980,
]
TEMPERATE_PLANET_TYPE_ID = 11

esi = EsiClientProvider(app_info_text=f"aa-dens v{__version__}")
logger = get_extension_logger(__name__)


def get_owner_assets_from_esi(owner: DenOwner) -> list[dict]:
    """Returns all character assets from the ESI"""

    logger.debug("Fetching esi asset for user id %s", owner.id)

    assets = esi.client.Assets.get_characters_character_id_assets(
        character_id=owner.character_id,
        token=owner.fetch_token().valid_access_token(),
    ).results()

    logger.debug("Returned %s", assets)

    return assets


def get_owner_anchored_dens_from_esi(owner: DenOwner) -> list[dict]:
    """Return all dens locations from the ESI"""

    den_assets = [
        asset
        for asset in get_owner_assets_from_esi(owner)
        if asset["type_id"] in MERCENARY_DENS_TYPE_IDS
        and asset["location_type"] == "solar_system"
    ]

    return den_assets


def get_esi_asset_location(owner: DenOwner, item_id: int) -> (int, int, int):
    """Returns the position of an item"""

    logger.debug("Fetching item id %s location from esi", item_id)

    position = esi.client.Assets.post_characters_character_id_assets_locations(
        character_id=owner.character_id,
        item_ids=[item_id],
        token=owner.fetch_token().valid_access_token(),
    ).result()[0]["position"]

    logger.debug(position)

    return position["x"], position["y"], position["z"]


def get_owner_notifications(owner: DenOwner) -> list[dict]:
    """Returns notifications from an owner"""
    logger.debug("Fetching notifications for den owner id %s", owner.id)

    notifications = esi.client.Character.get_characters_character_id_notifications(
        character_id=owner.character_id,
        token=owner.fetch_token().valid_access_token(),
    ).results()

    logger.debug(notifications)

    return notifications


def get_owner_mercenarydenreinforced_notifications(owner: DenOwner) -> list[dict]:
    """Returns only the `MercenaryDenReinforced` notifications from this owner"""

    return [
        notification
        for notification in get_owner_notifications(owner)
        if notification["type"] == "MercenaryDenReinforced"
    ]
