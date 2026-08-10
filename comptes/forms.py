from django import forms
from django.contrib.auth.models import User

from .models import Profil


class ModifierProfilForm(forms.ModelForm):
    """Formulaire de modification du profil de l'utilisateur connecté :
    email (sur le User), téléphone et photo (sur le Profil).

    Pour la photo : si l'utilisateur n'envoie pas de nouveau fichier, le
    ImageField conserve automatiquement la valeur déjà enregistrée (comportement
    natif de Django) — donc l'avatar existant reste inchangé tant qu'aucune
    nouvelle photo n'est choisie."""

    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = Profil
        fields = ['avatar', 'numero_telephone']
        labels = {
            'avatar': "Photo de profil",
            'numero_telephone': "Numéro de téléphone",
        }
        widgets = {
            'numero_telephone': forms.TextInput(attrs={'placeholder': '+2250700000000'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profil = super().save(commit=commit)
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save(update_fields=['email'])
        return profil
