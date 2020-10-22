from registration.models import *

import logging
logger = logging.getLogger("campus_identity_provider")


class SharedMixin(object):

    def get_identity_providers(self, profile):
        data = []
        logger.info(f'Getting identity providers!')
        identity_providers = IdentityProvider.objects.filter(social_linkable=True).values()
        linked_profiles = ProfileLink.objects.filter(profile=profile).order_by('-created_at')
        profile_links_id = [item.identity_provider.id for item in linked_profiles]
        for item in identity_providers:
            if item['id'] in profile_links_id:
                item['is_linked'] = True
            else:
                item['is_linked'] = False
            data.append(item)
        logger.info(f'Identity providers got succesfully!')
        return data

    def update_or_create_profile_preferences(self, profile, profile_preferences):
        for item in profile_preferences:
            preference = item.split('__')
            if preference[0]:
                profile_preference = ProfilePreference.objects.get(id=preference[0])
                profile_preference.preference_type = preference[1]
                profile_preference.preference_value = preference[2]
            else:
                ProfilePreference.objects.create(profile=profile, preference_type=preference[1], preference_value=preference[2])
        logger.info(f'Profile preferences Created succesfully!')

    def get_profile_identity_provider_name(self, user):
        profile_communication = ProfileCommunicationMedium.objects.filter(medium_type='email', medium_value=user['primary_email'])

        if profile_communication.exists():
            return profile_communication.first().identity_provider.name
        logger.info(f'Profile communication medium not found!')
        return ''
