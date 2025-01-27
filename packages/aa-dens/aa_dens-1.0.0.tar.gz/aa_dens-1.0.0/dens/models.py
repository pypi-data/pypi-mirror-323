"""Models."""

import datetime
import re
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from esi.models import Token
from eveuniverse.models import EvePlanet, EveType

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import (
    EveAllianceInfo,
    EveCharacter,
    EveCorporationInfo,
)
from allianceauth.services.hooks import get_extension_logger

ESI_SCOPES = [
    "esi-assets.read_assets.v1",
    "esi-characters.read_notifications.v1",
]

logger = get_extension_logger(__name__)


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            (
                "corporation_view",
                "Can view all dens anchored by members of their corporation",
            ),
            (
                "alliance_view",
                "Can view all dens anchored by members of their alliance",
            ),
            ("manager", "Can see all user's mercenary dens"),
        )


class DenOwner(models.Model):
    """Represents a character that will drop mercenary dens"""

    character_ownership = models.ForeignKey(
        CharacterOwnership,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Character used to sync mercenary dens",
    )

    is_enabled = models.BooleanField(
        default=True, db_index=True, help_text="Disabled characters won't be synced"
    )

    def __str__(self):
        return self.character_name

    @classmethod
    def get_user_owners(cls, user: User) -> QuerySet["DenOwner"]:
        """Return all den owners"""
        return cls.objects.filter(character_ownership__user=user)

    def fetch_token(self) -> Token:
        """Return valid token for this mining corp or raise exception on any error."""
        if not self.character_ownership:
            raise RuntimeError("This owner has no character configured.")
        token = (
            Token.objects.filter(
                character_id=self.character_ownership.character.character_id
            )
            .require_scopes(ESI_SCOPES)
            .require_valid()
            .first()
        )
        if not token:
            raise Token.DoesNotExist(f"{self}: No valid token found.")
        return token

    @property
    def character_name(self) -> str:
        """Returns the character name"""
        return self.character_ownership.character.character_name

    @property
    def character_id(self) -> int:
        """Returns the character id"""
        return self.character_ownership.character.character_id

    def enable(self):
        """Sets an owner back to activity"""
        self.is_enabled = True
        self.save()


class MercenaryDen(models.Model):
    """Represents anchored mercenary dens"""

    id = models.BigIntegerField(
        primary_key=True, help_text=_("Eve online id of the den")
    )

    owner = models.ForeignKey(
        DenOwner,
        on_delete=models.CASCADE,
        help_text=_("Character that anchored the den"),
    )
    location = models.ForeignKey(
        EvePlanet, on_delete=models.CASCADE, help_text=_("Location of the den")
    )

    def __str__(self) -> str:
        return f"Den {self.location.name}"

    @property
    def is_reinforced(self) -> bool:
        """True if there's an unexited reinforcement notification"""
        now = timezone.now()
        return MercenaryDenReinforcedNotification.objects.filter(
            den=self, exit_reinforcement__gt=now
        ).exists()

    @property
    def reinforcement_time(self) -> Optional[datetime.datetime]:
        """Return the den reinforcement time if it exists"""
        now = timezone.now()
        try:
            notification = MercenaryDenReinforcedNotification.objects.get(
                den=self, exit_reinforcement__gt=now
            )
            return notification.exit_reinforcement
        except MercenaryDenReinforcedNotification.DoesNotExist:
            pass
        return None

    @classmethod
    def get_owner_dens_ids_set(cls, owner: DenOwner) -> set[int]:
        """Returns a set with the id of all dens anchored by this owner"""
        return set(cls.objects.filter(owner=owner).values_list("id", flat=True))

    @classmethod
    def create(
        cls, owner: DenOwner, den_id: int, location: EvePlanet
    ) -> "MercenaryDen":
        """Creates a mercenary den and returns it"""
        den = cls.objects.create(id=den_id, owner=owner, location=location)
        return den

    @classmethod
    def all(cls) -> QuerySet["MercenaryDen"]:
        """Returns all mercenary dens in the  database"""
        return cls.objects.all()

    @classmethod
    def get_alliance_dens(cls, alliance: EveAllianceInfo) -> QuerySet["MercenaryDen"]:
        """Returns all mercenary dens from owners in the given alliance"""
        return cls.objects.filter(
            owner__character_ownership__character__alliance_id=alliance.alliance_id
        )

    @classmethod
    def get_corporation_dens(
        cls, corporation: EveCorporationInfo
    ) -> QuerySet["MercenaryDen"]:
        """Returns all mercenary dens from owners in a given corporation"""
        return cls.objects.filter(
            owner__character_ownership__character__corporation_id=corporation.corporation_id
        )

    @classmethod
    def get_user_dens(cls, user: User) -> QuerySet["MercenaryDen"]:
        """Return all mercenary dens associated with a user"""
        return cls.objects.filter(owner__character_ownership__user=user)


class MercenaryDenReinforcedNotification(models.Model):
    """Represents the notification of an owner den reinforced"""

    id = models.BigIntegerField(primary_key=True)

    den = models.ForeignKey(MercenaryDen, on_delete=models.CASCADE)

    reinforced_by = models.ForeignKey(
        EveCharacter,
        on_delete=models.CASCADE,
        help_text="Character that reinforced the Mercenary Den",
    )
    enter_reinforcement = models.DateTimeField(
        help_text=_("Timer when the den was reinforced")
    )
    exit_reinforcement = models.DateTimeField(
        help_text=_("Timer when the den will leave reinforcement")
    )

    REGEX = (
        r"aggressorAllianceName: <a href=\"showinfo:16159//(?P<alliance_id>.+)\">(?P<alliance_name>.+)</a>\n"
        r"aggressorCharacterID: (?P<character_id>.+)\n"
        r"aggressorCorporationName: <a href=\"showinfo:2//(?P<corporation_id>.+)\">(?P<corporation_name>.+)</a>\n"
        r"itemID: &id001 \d+\nmercenaryDenShowInfoData:\n"
        r"- showinfo\n- \d+\n- \*id001\n"
        r"planetID: (?P<planet_id>\d+)\n"
        r"planetShowInfoData:\n- showinfo\n- 11\n- \d+\n"
        r"solarsystemID: (?P<solarsystem_id>\d+)\n"
        r"timestampEntered: (?P<timestamp_entered>\d+)\n"
        r"timestampExited: (?P<timestamp_exited>\d+)\n"
        r"typeID: \d+\n"
    )

    def __str__(self) -> str:
        return f"Den {self.den.location.name} reinforced by {self.reinforced_by.character_name}"

    def is_in_future(self) -> bool:
        """True if the timer is in the future"""
        return self.exit_reinforcement > timezone.now()

    def create_timerboard_timer(self):
        """
        Creates a timer for this reinforcement in the timerboard app
        """
        from allianceauth.timerboard.models import Timer

        try:
            eve_corp = self.den.owner.character_ownership.character.corporation
        except EveCorporationInfo.DoesNotExist:
            eve_corp = EveCorporationInfo.objects.create_corporation(
                self.den.owner.character_ownership.character.corporation_id
            )

        Timer.objects.create(
            details=f"Mercenary den reinforced by {self.reinforced_by.character_name}",
            system=self.den.location.eve_solar_system.name,
            planet_moon=self.den.location.name,
            structure=Timer.Structure.MERCDEN,
            timer_type=Timer.TimerType.FINAL,
            objective=Timer.Objective.FRIENDLY,
            eve_time=self.exit_reinforcement,
            eve_corp=eve_corp,
        )

    def create_structuretimer_timer(self):
        """
        Creates a timer for this reinforcement in the structruretimer app
        """
        from structuretimers.models import Timer

        eve_character = self.den.owner.character_ownership.character
        try:
            eve_corp = eve_character.corporation
        except EveCorporationInfo.DoesNotExist:
            eve_corp = EveCorporationInfo.objects.create_corporation(
                self.den.owner.character_ownership.character.corporation_id
            )

        try:
            eve_alliance = eve_corp.alliance
        except EveAllianceInfo.DoesNotExist:
            eve_alliance = EveAllianceInfo.objects.create_alliance(eve_corp.alliance_id)

        structure_type, _ = EveType.objects.get_or_create_esi(id=85230)

        Timer.objects.create(
            date=self.exit_reinforcement,
            details_notes=f"Reinforced by {self.reinforced_by.character_name}",
            eve_alliance=eve_alliance,
            eve_character=eve_character,
            eve_corporation=eve_corp,
            eve_solar_system=self.den.location.eve_solar_system,
            location_details=self.den.location.name,
            objective=Timer.Objective.FRIENDLY,
            owner_name=eve_character.character_name,
            structure_type=structure_type,
            structure_name=self.den.location.name.split()[-1],
            timer_type=Timer.Type.FINAL,
        )

    @classmethod
    def parse_information_from_notification(cls, notification_dict: dict):
        """Generates and saves a new notification from the notification dict of the ESI"""

        match = re.match(cls.REGEX, notification_dict["text"])

        return match

    @classmethod
    def is_notification_id_known(cls, notification_id: int) -> bool:
        """Will check if the notification id is in the database"""
        return cls.objects.filter(id=notification_id).exists()

    @classmethod
    def create_from_notification(
        cls, notification: dict
    ) -> Optional["MercenaryDenReinforcedNotification"]:
        """
        Creates a den reinforced notification from an ESI notification.
        """

        match = cls.parse_information_from_notification(notification)

        associated_planet, _ = EvePlanet.objects.get_or_create_esi(
            id=match.group("planet_id")
        )
        try:
            associated_den = MercenaryDen.objects.get(location=associated_planet)
        except MercenaryDen.DoesNotExist:
            logger.error(
                "Trying to parse the notification of a non existing den on planet id %s",
                associated_planet.id,
            )
            return None

        eve_character_id = int(match.group("character_id"))
        reinforced_by = EveCharacter.objects.get_character_by_id(eve_character_id)
        if reinforced_by is None:
            reinforced_by = EveCharacter.objects.create_character(eve_character_id)
        logger.debug("Reinforced by %s", reinforced_by)
        entered_reinforce = get_time_eve(int(match.group("timestamp_entered")))
        exited_reinforce = get_time_eve(int(match.group("timestamp_exited")))

        notification = MercenaryDenReinforcedNotification.objects.create(
            id=notification["notification_id"],
            den=associated_den,
            reinforced_by=reinforced_by,
            enter_reinforcement=entered_reinforce,
            exit_reinforcement=exited_reinforce,
        )

        return notification


def get_time_eve(dt: int) -> datetime.datetime:
    """
    Formula to parse ESI timestamps to datetime
    https://forums.eveonline.com/t/timestamp-format-in-notifications-by-esi/230395
    """
    microseconds = dt / 10
    seconds, microseconds = divmod(microseconds, 1000000)
    days, seconds = divmod(seconds, 86400)
    return datetime.datetime(1601, 1, 1, tzinfo=timezone.utc) + datetime.timedelta(
        days, seconds
    )
