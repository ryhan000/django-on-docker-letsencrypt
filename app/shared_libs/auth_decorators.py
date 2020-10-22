from rest_framework import viewsets
from rest_framework.status import *
from registration.models import *
from shared_libs.exceptions import *
from rest_framework import permissions
from decouple import config
import jwt

import logging
logger = logging.getLogger("campus_identity_provider")


class IsAuthenticated(viewsets.ViewSet):

    def has_permission(self, request, view):
        if 'access_token' in request.COOKIES:
            access_token = request.COOKIES['access_token']
            return self.decorated_function(request, access_token)
        logger.error('Profile credentials were not found in the headers or body!')
        raise ProfileCredentialsRequiredException()

    def decorated_function(self, request, access_token):
        try:
            self.decode_access_token(access_token)
        except jwt.ExpiredSignatureError:
            logger.error('The access token provided has expired!')
            raise ExpiredAccessTokenException()
        except:
            logger.error('Invalid profile credentials!')
            raise InvalidProfileCredentialsException()

        data = self.decode_access_token(access_token)
        profile = self.get_profile(data['id'], access_token)

        if not profile:
            logger.error('Invalid profile credentials!')
            raise InvalidProfileCredentialsException()
        else:
            request.profile = profile
            return True

    def get_profile(self, id, access_token):
        return Profile.objects.filter(id=id).first()

    def decode_access_token(self, token):
        return jwt.decode(str(token), config('ACCESS_TOKEN_SECRET'), algorithms=config('JWT_ALGORITHM'))

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.profile


class ProfileSetMixin(object):

    def set_profile(self, request):
        if 'access_token' in request.COOKIES:
            access_token = request.COOKIES['access_token']
            return self.decorated_function(request, access_token)
        logger.error('Invalid profile credentials!')
        raise InvalidProfileCredentialsException()

    def decorated_function(self, request, access_token):
        try:
            self.decode_access_token(access_token)
        except jwt.ExpiredSignatureError:
            logger.error('The access token provided has expired!')
            raise ExpiredAccessTokenException()
        except:
            logger.error('Invalid profile credentials!')
            raise InvalidProfileCredentialsException()

        data = self.decode_access_token(access_token)
        profile = self.get_profile(data['id'], access_token)

        if not profile:
            logger.error('Invalid profile credentials!')
            raise InvalidProfileCredentialsException()
        else:
            request.profile = profile
            return True

    def get_profile(self, id, access_token):
        return Profile.objects.filter(id=id).first()

    def decode_access_token(self, token):
        return jwt.decode(str(token), config('ACCESS_TOKEN_SECRET'), algorithms=config('JWT_ALGORITHM'))
