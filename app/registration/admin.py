from django.contrib import admin
from .models import *

admin.site.register(Store)
admin.site.register(IdentityProvider)
admin.site.register(StoreIdentityProvider)
admin.site.register(Profile)
admin.site.register(ProfileLink)
admin.site.register(ProfilePreference)
admin.site.register(ProfileCommunicationMedium)
