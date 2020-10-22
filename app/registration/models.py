from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from utils.file_utils import *
from shared_libs.exceptions import *
import uuid

from django.conf import settings


def file_size(value):
    if value.size > settings.MAX_IMAGE_SIZE:
        raise ValidationError(
            'ImageField is too large. Size should not exceed 4MB')


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UpdatedAt', auto_now=True)
    active_status = models.BooleanField(db_column='ActiveStatus', default=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    id = models.UUIDField(db_column='ProfileID', primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(db_column='FirstName', max_length=64)
    last_name = models.CharField(db_column='LastName', max_length=64)
    date_of_birth = models.DateField(db_column='DateOfBirth', null=True, blank=True)
    profile_picture_uri = models.ImageField(db_column='ProfilePictureURI', null=True, blank=True, upload_to=get_file_path, validators=[file_size])
    primary_email = models.CharField(db_column='PrimaryEmail', max_length=256)
    primary_contact_number = models.CharField(db_column='PrimaryContactNumber', max_length=16, null=True, blank=True)
    terms_accepted = models.BooleanField(db_column='TermsAccepted', default=False)

    def __str__(self):
        return f'{self.first_name}'


class IdentityProvider(BaseModel):
    id = models.UUIDField(db_column='IdentityProviderID', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(db_column='Name', max_length=64)
    app_id = models.CharField(db_column='AppId', max_length=256)
    authorization_uri = models.URLField(db_column='AuthorizationURI')
    access_token_uri = models.URLField(db_column='AccesstokenURI')
    permission_scope = models.CharField(db_column='PermissionScope', max_length=400)
    client_id = models.CharField(db_column='ClientID', max_length=256)
    client_secret = models.CharField(db_column='ClientSecret', max_length=400)
    authorization_response_type = models.CharField(db_column='AuthorizationResponseType', max_length=256)
    access_grant_type = models.CharField(db_column='AccessGrantType', max_length=64)
    return_uri = models.URLField(db_column='ReturnURI')
    provider_branding = JSONField(db_column='ProviderBranding')
    oauth_provider_tag = models.CharField(db_column='OauthProviderTag', max_length=64)
    slug = models.SlugField(db_column='Slug')
    social_linkable = models.BooleanField(db_column='SocialLinkable', default=False)

    def __str__(self):
        return f'{self.name}'


class ProfileLink(BaseModel):
    id = models.UUIDField(db_column='ProfileLinkID', primary_key=True, default=uuid.uuid4, editable=False)
    identity_provider = models.ForeignKey('registration.IdentityProvider', db_column='IdentityProviderID', on_delete=models.CASCADE, related_name='profile_links')
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='profile_links')
    provider_profile_identity = models.CharField(db_column='ProviderProfileIdentity', max_length=128)
    authorization_code = models.CharField(db_column='AuthorizationCode', max_length=400)
    authorization_code_expiration = models.DateTimeField(db_column='AuthorizationCodeExpiration')
    access_token = models.CharField(db_column='AccessToken', max_length=400)
    access_token_expiration = models.DateTimeField(db_column='AccessTokenExpiration')
    refresh_token = models.CharField(db_column='RefreshToken', max_length=400)
    refresh_token_expiration = models.DateTimeField(db_column='RefreshTokenExpiration')
    CSRF_token = models.CharField(db_column='CSRFToken', max_length=400)
    auth_account_id = models.CharField(db_column='OauthAccountID', max_length=400)

    def __str__(self):
        return f'{self.identity_provider_id.name}'


class ProfileCommunicationMedium(BaseModel):
    id = models.UUIDField(db_column='ProfileCommunicationMediumID', primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='profile_communication_mediums')
    medium_type = models.CharField(db_column='MediumType', max_length=32)
    medium_value = models.CharField(db_column='MediumValue', max_length=256)
    identity_provider = models.ForeignKey('registration.IdentityProvider', db_column='IdentityProvider', on_delete=models.CASCADE, related_name='profile_communication_mediums')

    def __str__(self):
        return f'{self.identity_provider.name}'


class ProfilePreference(BaseModel):
    id = models.UUIDField(db_column='ProfilePreferenceID', primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey('registration.Profile', db_column='ProfileID', on_delete=models.CASCADE, related_name='profile_preferences')
    preference_type = models.CharField(db_column='PreferenceType', max_length=32)
    preference_value = models.CharField(db_column='PreferenceValue', max_length=256)

    def __str__(self):
        return f'{self.profile_id.first_name}'


class Store(BaseModel):
    id = models.UUIDField(db_column='StoreID', primary_key=True, default=uuid.uuid4, editable=False)
    course_provider_code = models.CharField(db_column='CourseProviderCode', max_length=64)
    name = models.CharField(db_column='Name', max_length=64)
    url_slug = models.SlugField(db_column='URLSlug')

    def __str__(self):
        return f'{self.course_provider_code}'


class StoreIdentityProvider(BaseModel):
    id = models.UUIDField(db_column='StoreIdentityProviderID', primary_key=True, default=uuid.uuid4, editable=False)
    identity_provider = models.ForeignKey('registration.IdentityProvider', db_column='IdentityProviderID', on_delete=models.CASCADE, related_name='store_identity_providers')
    store = models.ForeignKey('registration.Store', db_column='StoreID', on_delete=models.CASCADE, related_name='store_identity_providers')

    def __str__(self):
        return f'{self.identity_provider_id}'
