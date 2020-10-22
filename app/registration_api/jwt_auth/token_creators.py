from registration.models import *

from rest_framework.status import *

from shared_libs.exceptions import *

from decouple import config
import jwt
import datetime
import uuid

import logging
logger = logging.getLogger("campus_identity_provider")


class JWTMixin(object):

    def set_cookies(self, response, tokens_dict):
        response.set_cookie(key='access_token', value=tokens_dict.get('access_token'), httponly=True, samesite='Strict', domain=config('FRONTEND_TLD'))
        response.set_cookie(key='refresh_token', value=tokens_dict.get('refresh_token'), httponly=True, samesite='Strict', domain=config('FRONTEND_TLD'))
        response.set_cookie(key='expires_in', value=str(tokens_dict.get('expires_in')), httponly=True, samesite='Strict', domain=config('FRONTEND_TLD'))
        logger.info('Cookies set Succesfully!')

    def delete_cookies(self, response):
        response.delete_cookie('access_token', domain=config('FRONTEND_TLD'))
        response.delete_cookie('refresh_token', domain=config('FRONTEND_TLD'))
        response.delete_cookie('expires_in', domain=config('FRONTEND_TLD'))
        logger.info('Cookies delete Succesfully!')

    def create_user_token(self, user, identity_provider):
        is_signup = True
        profile_comm = ProfileCommunicationMedium.objects.filter(medium_type='email', medium_value=user['primary_email'])
        if profile_comm.exists():
            profile_comm = profile_comm.first()
            profile = profile_comm.profile
            if profile_comm.identity_provider.slug == identity_provider.slug:
                is_signup = False
            else:
                return False
        else:
            profile = Profile.objects.create(**user)
        tokens_dict = self.access_token_generator(profile)
        if is_signup:
            profile_comm = ProfileCommunicationMedium.objects.filter(profile=profile, medium_type='email', medium_value=user['primary_email'], identity_provider=identity_provider)
            if not profile_comm.exists():
                self.create_profile_communication_medium(profile, user, identity_provider)
            self.create_profile_link(profile, identity_provider)

        return tokens_dict

    def profile_link(self, user, identity_provider, request):
        profile_comm = ProfileCommunicationMedium.objects.filter(medium_type='email', medium_value=user['primary_email'])

        if not profile_comm.exists():
            self.create_profile_communication_medium(request.profile, user, identity_provider)
        self.create_profile_link(request.profile, identity_provider)
        return True

    def access_token_generator(self, profile):
        auth_response = {'access_token': self.create_access_token(profile),'refresh_token': self.create_refresh_token(profile), 'expires_in': int(config('TOKEN_EXP_TIME'))}
        return auth_response

    def get_new_access_token(self, refresh_token):
        try:
            data = self.decode_refresh_token(refresh_token)
            logger.info('Succesfully refresh token decoded!')
            profile = Profile.objects.filter(id=data['id']).first()
            auth_response = {
                    'access_token': self.create_access_token(profile),
                    'refresh_token': self.create_refresh_token(profile),
                    'expires_in': int(config('TOKEN_EXP_TIME')),
            }
            return auth_response
        except Exception:
            logger.error('Invalid profile credentials!')
            raise InvalidProfileCredentialsException()

    def create_access_token(self, profile):
        return jwt.encode(
            {'id': str(profile.id),
             'uuid': str(uuid.uuid4()),
             'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=int(config('TOKEN_EXP_TIME')))},
            config('ACCESS_TOKEN_SECRET'),
            algorithm=config('JWT_ALGORITHM')).decode('utf-8')

    def create_refresh_token(self, profile):
        return jwt.encode({
            'id': str(profile.id),
            'uuid': str(uuid.uuid4())},
            config('REFRESH_TOKEN_SECRET'),
            algorithm=config('JWT_ALGORITHM')).decode('utf-8')

    def decode_refresh_token(self, token):
        return jwt.decode(str(token), config('REFRESH_TOKEN_SECRET'), algorithms=config('JWT_ALGORITHM'))

    def create_profile_communication_medium(self, profile, user, identity_provider):
        ProfileCommunicationMedium.objects.create(profile=profile, medium_type='email', medium_value=user['primary_email'], identity_provider=identity_provider)

    def create_profile_link(self, profile, identity_provider):
        ProfileLink.objects.create(
            identity_provider=identity_provider,
            profile=profile,
            provider_profile_identity='provider_profile_identity',
            authorization_code='authorization_code',
            authorization_code_expiration=datetime.datetime.now(),
            access_token='access_token',
            access_token_expiration=datetime.datetime.now(),
            refresh_token='refresh_token',
            refresh_token_expiration=datetime.datetime.now(),
            CSRF_token='CSRF_token',
        )
