"""Tasks."""

from celery import chain, shared_task

from django.shortcuts import get_object_or_404
from eveuniverse.constants import EveGroupId
from eveuniverse.core.evesdeapi import nearest_celestial
from eveuniverse.models import EvePlanet

from allianceauth.services.hooks import get_extension_logger
from app_utils.django import app_labels

from dens.esi import (
    TEMPERATE_PLANET_TYPE_ID,
    get_esi_asset_location,
    get_owner_anchored_dens_from_esi,
    get_owner_mercenarydenreinforced_notifications,
)
from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification

logger = get_extension_logger(__name__)


@shared_task
def update_all_den_owners():
    """Initiates an update of all enabled den owners"""
    enabled_den_owners = DenOwner.objects.filter(is_enabled=True)
    logger.info("Updating %s den owners", enabled_den_owners.count())

    task_list = []
    for owner in enabled_den_owners:
        task_list.append(update_owner_dens.si(owner.id))

    chain(task_list).delay()


@shared_task
def update_owner_dens(owner_id: int):
    """Updates the mercenary dens anchored by this owner"""
    logger.info("Updating mercenary dens for owner id %s", owner_id)
    owner = DenOwner.objects.get(id=owner_id)

    dens_assets = get_owner_anchored_dens_from_esi(owner)
    current_ids_set = {den["item_id"] for den in dens_assets}

    stored_ids_set = MercenaryDen.get_owner_dens_ids_set(owner)

    disappeared_dens_ids = stored_ids_set - current_ids_set
    disappeared_dens = MercenaryDen.objects.filter(id__in=disappeared_dens_ids)
    logger.debug("Deleting %d dens", disappeared_dens.count())
    disappeared_dens.delete()

    new_dens_ids = current_ids_set - stored_ids_set
    logger.debug("Creating %d new dens", len(new_dens_ids))
    new_dens_tasks = []
    for dens_asset in dens_assets:
        if dens_asset["item_id"] in new_dens_ids:
            create_den_tasks = create_mercenary_den.si(owner_id, dens_asset)
            new_dens_tasks.append(create_den_tasks)

    chain(new_dens_tasks).delay()


@shared_task
def create_mercenary_den(owner_id: int, den_asset_dict: dict):
    """Creates a new mercenary den associated with this owner from the asset dictionnary"""
    den_item_id = den_asset_dict["item_id"]
    logger.info("Creating den id %s for owner id %d", den_item_id, owner_id)
    logger.debug(den_asset_dict)
    owner = DenOwner.objects.get(id=owner_id)

    x, y, z = get_esi_asset_location(owner, den_item_id)
    nearest_planet = nearest_celestial(
        den_asset_dict["location_id"], x, y, z, EveGroupId.PLANET
    )

    if not nearest_planet or nearest_planet.type_id != TEMPERATE_PLANET_TYPE_ID:
        raise RuntimeError(
            f"Couldn't find planet corresponding to den id {den_item_id}"
        )

    planet, _ = EvePlanet.objects.get_or_create_esi(id=nearest_planet.id)

    MercenaryDen.create(owner, den_item_id, planet)


@shared_task
def update_all_owners_notifications():
    """Starts an owner update job for every owner"""
    owners = DenOwner.objects.all()
    logger.info("Starting notifications update for %s owners", owners.count())
    jobs = []
    for owner in owners:
        jobs.append(update_owner_notifications.si(owner.id))

    chain(jobs).delay()


@shared_task
def update_owner_notifications(owner_id: int):
    """Checks all notifications related to an owner and update new den reinforcement notifications"""
    logger.info("Updating notifications for owner id %s", owner_id)

    owner = get_object_or_404(DenOwner, id=owner_id)
    notifications = get_owner_mercenarydenreinforced_notifications(owner)

    for notification in notifications:
        if not MercenaryDenReinforcedNotification.is_notification_id_known(
            notification["notification_id"]
        ):
            create_reinforce_notification.delay(notification)


@shared_task
def create_reinforce_notification(notification_json: dict):
    """Saves a reinforce notification from the ESI information"""
    logger.info("Creating a den reinforced notification from %s", notification_json)

    reinforce_notification = (
        MercenaryDenReinforcedNotification.create_from_notification(notification_json)
    )

    if reinforce_notification.is_in_future():
        logger.info("Trying to add the timer to timerboards")

        if "timerboard" in app_labels():
            logger.debug("Timerboard detected")
            reinforce_notification.create_timerboard_timer()
            logger.info("Timer added to timerboard")

        if "structuretimers" in app_labels():
            logger.debug("Structruetimer detected")
            reinforce_notification.create_structuretimer_timer()
            logger.info("Timer added to structuretimers")
