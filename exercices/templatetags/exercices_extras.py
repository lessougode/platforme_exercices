from django import template

register = template.Library()


@register.filter
def pourcentage(valeur, total):
    """Renvoie un pourcentage entier (0-100), sans planter si total est nul/vide."""
    try:
        valeur = float(valeur)
        total = float(total)
        if total <= 0:
            return 0
        return max(0, min(100, round(valeur / total * 100)))
    except (TypeError, ValueError):
        return 0
