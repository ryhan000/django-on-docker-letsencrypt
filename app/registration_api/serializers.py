from rest_framework import serializers
from registration.models import *


class IdentityProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = IdentityProvider
        fields = ('id', 'name', 'app_id', 'authorization_uri', 'access_token_uri', 'permission_scope', 'client_id', 'client_secret', 'authorization_response_type', 'access_grant_type', 'return_uri', 'provider_branding', 'oauth_provider_tag', 'slug')


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ('id', 'course_provider_code', 'name', 'url_slug')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        identity_provider_ids = [item.identity_provider.id for item in StoreIdentityProvider.objects.filter(store__id=data['id'])]
        data['identity_providers'] = IdentityProviderSerializer(IdentityProvider.objects.filter(id__in=identity_provider_ids), many=True).data
        return data


class StoreIdentityProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreIdentityProvider
        fields = ('id', 'identity_provider', 'store')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['store'] = StoreSerializer(Store.objects.get(id=data['store'])).data
        data['identity_provider'] = IdentityProviderSerializer(IdentityProvider.objects.get(id=data['identity_provider'])).data
        return data


class ProfileLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileLink
        fields = ('id', 'identity_provider')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['identity_provider'] = IdentityProviderSerializer(IdentityProvider.objects.get(id=data['identity_provider'])).data
        data['is_linked'] = True
        return data


class ProfilePreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfilePreference
        fields = ('id', 'preference_type', 'preference_value')


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'profile_picture_uri', 'primary_email', 'primary_contact_number', 'terms_accepted')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['profile_preferences'] = ProfilePreferenceSerializer(ProfilePreference.objects.filter(profile__id=data['id']), many=True).data
        return data


class CheckValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'first_name', 'last_name', 'profile_picture_uri', 'primary_contact_number', 'terms_accepted')
