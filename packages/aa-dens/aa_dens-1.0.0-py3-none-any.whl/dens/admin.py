"""Admin site."""

from django.contrib import admin

from dens.models import DenOwner, MercenaryDen, MercenaryDenReinforcedNotification


@admin.register(DenOwner)
class DenOwnerAdmin(admin.ModelAdmin):
    list_display = ["character_name", "dens_count", "is_enabled"]
    readonly_fields = ["character_ownership"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="#Dens anchored under this owner")
    def dens_count(self, owner: DenOwner):
        return len(MercenaryDen.get_owner_dens_ids_set(owner))


@admin.register(MercenaryDen)
class MercenaryDenAdmin(admin.ModelAdmin):
    list_display = ["location", "owner", "is_reinforced", "reinforcement_time"]
    list_filter = ["owner"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(MercenaryDenReinforcedNotification)
class MercenaryDenReinforcedNotificationAdmin(admin.ModelAdmin):
    list_display = ["den", "reinforced_by", "enter_reinforcement", "exit_reinforcement"]
