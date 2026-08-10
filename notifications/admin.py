from django.contrib import admin

from .models import Notification
from .services import envoyer_notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('objet', 'canal', 'statut', 'date_creation', 'date_envoi')
    list_filter = ('canal', 'statut')
    filter_horizontal = ('destinataires',)
    readonly_fields = ('envoye_par', 'date_envoi', 'statut', 'rapport_envoi')
    fields = ('objet', 'message', 'canal', 'destinataires', 'groupe_cible', 'statut', 'date_envoi', 'rapport_envoi')
    actions = ['envoyer_les_notifications']

    def save_model(self, request, obj, form, change):
        if not obj.envoye_par_id:
            obj.envoye_par = request.user
        super().save_model(request, obj, form, change)

    def envoyer_les_notifications(self, request, queryset):
        for notification in queryset:
            envoyer_notification(notification)
        self.message_user(request, f"{queryset.count()} notification(s) traitee(s). Consulte le rapport d'envoi de chacune.")
    envoyer_les_notifications.short_description = "Envoyer les notifications selectionnees"
