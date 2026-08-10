from .models import ConfigurationSite


def configuration_site(request):
    return {
        "configuration_site": ConfigurationSite.charger()
    }