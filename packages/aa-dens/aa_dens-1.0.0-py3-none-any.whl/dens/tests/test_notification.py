from datetime import timedelta

from structuretimers.models import Timer as StructureTimer

from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EveType

from allianceauth.eveonline.models import EveCharacter
from allianceauth.timerboard.models import Timer as TimerboardTimer

from dens.models import MercenaryDenReinforcedNotification
from dens.tests.utils import (
    REINFORCE_NOTIFICATION,
    create_fake_den,
    create_fake_den_owner,
    create_fake_notification,
)

from ..tasks import create_reinforce_notification
from .testdata.load_eveuniverse import load_eveuniverse


class TestNotification(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

    def test_parsing(self):

        res = MercenaryDenReinforcedNotification.parse_information_from_notification(
            REINFORCE_NOTIFICATION
        )

        self.assertIsNotNone(res)

        self.assertEqual(res.group("alliance_id"), "99003214")
        self.assertEqual(res.group("alliance_name"), "Brave Collective")
        self.assertEqual(res.group("corporation_id"), "98169165")
        self.assertEqual(res.group("corporation_name"), "Brave Newbies Inc.")
        self.assertEqual(res.group("character_id"), "96914524")
        self.assertEqual(res.group("planet_id"), "40255101")
        self.assertEqual(res.group("solarsystem_id"), "30004028")
        self.assertEqual(res.group("timestamp_entered"), "133761583913385305")
        self.assertEqual(res.group("timestamp_exited"), "133762405913385305")

    def test_create_from_notification(self):

        owner = create_fake_den_owner()
        create_fake_den(owner)

        create_reinforce_notification(REINFORCE_NOTIFICATION)

        stored_reinforce_notification = (
            MercenaryDenReinforcedNotification.objects.all()[0]
        )

        self.assertIsNotNone(stored_reinforce_notification)

        self.assertEqual(stored_reinforce_notification.id, 2064665856)
        self.assertEqual(
            stored_reinforce_notification.reinforced_by,
            EveCharacter.objects.get_character_by_id(96914524),
        )

        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.enter_reinforcement)
        )
        self.assertTrue(
            timezone.is_aware(stored_reinforce_notification.exit_reinforcement)
        )

    def test_in_future(self):
        reinforce_notification = create_fake_notification()

        self.assertFalse(reinforce_notification.is_in_future())

        reinforce_notification.exit_reinforcement = timezone.now() + timedelta(days=1)
        reinforce_notification.save()

        self.assertTrue(reinforce_notification.is_in_future())

    def test_add_timerboard(self):
        reinforce_notification = create_fake_notification()

        self.assertEqual(TimerboardTimer.objects.count(), 0)

        reinforce_notification.create_timerboard_timer()

        self.assertEqual(TimerboardTimer.objects.count(), 1)

        timer = TimerboardTimer.objects.all()[0]

        self.assertEqual(timer.details, "Mercenary den reinforced by Butt Chili")
        self.assertEqual(timer.system, "E-VKJV")
        self.assertEqual(timer.planet_moon, "E-VKJV VI")
        self.assertEqual(timer.structure, TimerboardTimer.Structure.MERCDEN)
        self.assertEqual(timer.timer_type, TimerboardTimer.TimerType.FINAL)
        self.assertEqual(timer.objective, TimerboardTimer.Objective.FRIENDLY)
        self.assertEqual(timer.eve_time, reinforce_notification.exit_reinforcement)
        self.assertFalse(timer.important)
        self.assertIsNone(timer.eve_character)
        self.assertEqual(
            timer.eve_corp,
            reinforce_notification.den.owner.character_ownership.character.corporation,
        )
        self.assertFalse(timer.corp_timer)
        self.assertIsNone(timer.user)

    def test_add_structuretimer(self):
        reinforce_notification = create_fake_notification()

        self.assertEqual(StructureTimer.objects.count(), 0)

        reinforce_notification.create_structuretimer_timer()

        self.assertEqual(StructureTimer.objects.count(), 1)

        timer = StructureTimer.objects.all()[0]

        structure_type, _ = EveType.objects.get_or_create_esi(id=85230)

        self.assertEqual(timer.date, reinforce_notification.exit_reinforcement)
        self.assertIsNone(timer.details_image_url)
        self.assertEqual(timer.details_notes, "Reinforced by Butt Chili")
        # self.assertEqual(timer.eve_alliance, 99011247)
        self.assertEqual(
            timer.eve_character,
            reinforce_notification.den.owner.character_ownership.character,
        )
        self.assertEqual(
            timer.eve_corporation,
            reinforce_notification.den.owner.character_ownership.character.corporation,
        )
        self.assertEqual(
            timer.eve_solar_system, reinforce_notification.den.location.eve_solar_system
        )
        self.assertFalse(timer.is_important)
        self.assertFalse(timer.is_opsec)
        self.assertEqual(timer.location_details, "E-VKJV VI")
        self.assertEqual(timer.objective, StructureTimer.Objective.FRIENDLY)
        self.assertEqual(timer.owner_name, "Ji'had Rokym")
        self.assertEqual(timer.structure_type, structure_type)
        self.assertEqual(timer.structure_name, "VI")
        self.assertEqual(timer.timer_type, StructureTimer.Type.FINAL)
        self.assertIsNone(timer.user)
        self.assertEqual(timer.visibility, StructureTimer.Visibility.UNRESTRICTED)
