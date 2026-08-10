"""Envoi effectif des notifications : email (Django), SMS et WhatsApp (Twilio)."""
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def envoyer_email(destinataire_email, sujet, message):
    send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [destinataire_email], fail_silently=False)


def _client_twilio():
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise RuntimeError(
            "Identifiants Twilio non configures. Renseigne TWILIO_ACCOUNT_SID et "
            "TWILIO_AUTH_TOKEN dans settings.py (voir le README)."
        )
    from twilio.rest import Client
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def envoyer_sms(numero, message):
    if not settings.TWILIO_SMS_FROM:
        raise RuntimeError("TWILIO_SMS_FROM non configure dans settings.py.")
    client = _client_twilio()
    client.messages.create(body=message, from_=settings.TWILIO_SMS_FROM, to=numero)


def envoyer_whatsapp(numero, message):
    if not settings.TWILIO_WHATSAPP_FROM:
        raise RuntimeError("TWILIO_WHATSAPP_FROM non configure dans settings.py.")
    client = _client_twilio()
    client.messages.create(
        body=message,
        from_=f'whatsapp:{settings.TWILIO_WHATSAPP_FROM}',
        to=f'whatsapp:{numero}',
    )


def envoyer_notification(notification):
    """Envoie la notification a tous ses destinataires effectifs et enregistre le rapport."""
    destinataires = notification.liste_destinataires()

    reussites, echecs = [], []
    for utilisateur in destinataires:
        nom = utilisateur.get_full_name() or utilisateur.username
        try:
            if notification.canal == notification.EMAIL:
                if not utilisateur.email:
                    raise ValueError("aucune adresse email enregistree")
                envoyer_email(utilisateur.email, notification.objet, notification.message)

            elif notification.canal == notification.SMS:
                numero = getattr(getattr(utilisateur, 'profil', None), 'numero_telephone', '')
                if not numero:
                    raise ValueError("aucun numero de telephone enregistre")
                envoyer_sms(numero, notification.message)

            elif notification.canal == notification.WHATSAPP:
                numero = getattr(getattr(utilisateur, 'profil', None), 'numero_telephone', '')
                if not numero:
                    raise ValueError("aucun numero de telephone enregistre")
                envoyer_whatsapp(numero, notification.message)

            reussites.append(nom)
        except Exception as exc:
            echecs.append(f"{nom} : {exc}")

    if not destinataires:
        notification.statut = notification.ERREUR
        notification.rapport_envoi = "Aucun destinataire (verifie la selection ou le groupe cible)."
    elif not echecs:
        notification.statut = notification.ENVOYE
        notification.rapport_envoi = f"Envoye avec succes a : {', '.join(reussites)}"
    elif not reussites:
        notification.statut = notification.ERREUR
        notification.rapport_envoi = "Echecs :\n" + "\n".join(echecs)
    else:
        notification.statut = notification.ENVOYE_PARTIEL
        notification.rapport_envoi = (
            f"Reussis ({len(reussites)}) : {', '.join(reussites)}\n\n"
            f"Echecs ({len(echecs)}) :\n" + "\n".join(echecs)
        )

    notification.date_envoi = timezone.now()
    notification.save(update_fields=['statut', 'rapport_envoi', 'date_envoi'])
    return notification
