from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect

from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.status import *

from registration.models import *

from shared_libs.auth_decorators import IsAuthenticated, ProfileSetMixin
from shared_libs.exceptions import *

from registration_api.jwt_auth.token_creators import JWTMixin
from registration_api.shared_function import SharedMixin
from registration_api.serializers import *

from requests_oauthlib import OAuth2Session
from decouple import config

import json
import logging

logger = logging.getLogger("campus_identity_provider")


class LoginViewSet(JWTMixin, viewsets.ViewSet):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):

        try:
            del request.session['linking']
            logger.info('Delete linking  from request session successfully!')
        except KeyError:
            logger.error('Find Key error when try to Delete linking  from request session!')

        client = self.request.query_params.get('client', None)

        request.session['querystring'] = request.GET.urlencode()

        try:
            identity_provider = IdentityProvider.objects.get(slug=client)
        except IdentityProvider.DoesNotExist:
            logger.error(f'No identity provider exist with name {client}!')
            raise IdentityProviderNotFoundException()

        logger.info(f'Trying to login with {client}!')

        client_id = identity_provider.client_id
        redirect_uri = identity_provider.return_uri
        authorization_base_url = identity_provider.authorization_uri

        if identity_provider.slug == 'google':
            scope = [
                'https://www.googleregistration_apis.com/auth/userinfo.email',
                'https://www.googleregistration_apis.com/auth/userinfo.profile'
            ]

        else:
            scope = ['r_liteprofile', 'r_emailaddress']

        client = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        authorization_url, state = client.authorization_url(authorization_base_url)

        request.session['oauth_state'] = state
        return redirect(authorization_url)


class CallBackViewSet(JWTMixin, viewsets.ViewSet, ProfileSetMixin, SharedMixin):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        client = request.path.split('/')[1]
        user_info = {}

        try:
            extra_params = request.session['querystring'] or ''
            logger.info('querystring  key found from request session!')
        except KeyError:
            extra_params = ''
            logger.error('Find Key error when try to get  querystring from request session!')

        try:
            request.session['oauth_state']
        except KeyError:
            raise OAuthStateNotFoundException()

        if 'user_cancelled_login' in str(request.get_full_path()):
            logger.info(f'Login canceled!')
            return redirect(config('FRONTEND_REGISTRATION_BASE_URL'))

        try:
            identity_provider = IdentityProvider.objects.get(slug=client)
        except IdentityProvider.DoesNotExist:
            logger.error(f'No identity provider exist with name {client}!')
            raise IdentityProviderNotFoundException()

        client_id = identity_provider.client_id
        client_secret = identity_provider.client_secret
        redirect_uri = identity_provider.return_uri
        token_url = identity_provider.access_token_uri

        temp_var = request.build_absolute_uri()
        if 'http:' in temp_var:
            temp_var = 'https:' + temp_var[5:]

        client = OAuth2Session(client_id, state=request.session['oauth_state'], redirect_uri=redirect_uri)

        try:
            del request.session['oauth_state']
            logger.info('Delete oauth_state  from request session successfully!')
        except KeyError:
            logger.error('Find Key error when try to Delete oauth state from request session!')

        if identity_provider.slug == 'google':
            profile_url = 'https://www.googleregistration_apis.com/oauth2/v1/userinfo'
            token = client.fetch_token(token_url, client_secret=client_secret, include_client_id=True, authorization_response=temp_var)

            user_info = client.get(profile_url).json()

            user = {
                'first_name': user_info['given_name'],
                'last_name': user_info['family_name'],
                'primary_email': user_info['email'],
            }

        else:
            profile_url = 'https://registration_api.linkedin.com/v2/me'
            email_url = 'https://registration_api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
            token = client.fetch_token(token_url, client_secret=client_secret, authorization_response=temp_var)
            user_info = client.get(profile_url).json()
            email = client.get(email_url).json()

            user = {
                'first_name': user_info['localizedFirstName'],
                'last_name': user_info['localizedLastName'],
                'primary_email': email['elements'][0]['handle~']['emailAddress'],
            }

        try:
            linking = request.session['linking']
            logger.info('linking  key found from request session!')
        except KeyError:
            linking = None
            logger.error('Find Key error when try to get linking from request session!')

        if not linking == 'linking':
            tokens_dict = self.create_user_token(user, identity_provider)

            if tokens_dict is False:
                logger.info('Identity Provider not matched for login!')
                return redirect(config('FRONTEND_REGISTRATION_BASE_URL')+'/?matched_identity_provider=' + self.get_profile_identity_provider_name(user) + '&' + extra_params)

            response = HttpResponseRedirect(config('FRONTEND_REGISTRATION_BASE_URL') + '?' + extra_params)
            self.set_cookies(response, tokens_dict)
            logger.info('loged in successfully!')
            return response
        else:
            try:
                del request.session['linking']
                logger.info('Delete linking  from request session successfully!')
            except KeyError:
                logger.error('Find Key error when try to Delete linking  from request session!')

            self.set_profile(request)

            link = self.profile_link(user, identity_provider, request)

            if link is False:
                logger.info('Profile Communication Medium not found!')
                return redirect(config('FRONTEND_REGISTRATION_BASE_URL') + '/?matched_identity_provider=' + self.get_profile_identity_provider_name(user) + '&' + extra_params)

            logger.info('Identity Provide successfully linked!')

            return redirect(config('FRONTEND_REGISTRATION_BASE_URL') + '/settings/account/?has_linked=' + self.get_profile_identity_provider_name(user) + '&' + extra_params)


class ProfileLinkingViewSet(JWTMixin, viewsets.ViewSet):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        client = self.request.query_params.get('client', None)

        try:
            identity_provider = IdentityProvider.objects.get(slug=client)
        except IdentityProvider.DoesNotExist:
            logger.info(f'No identity provider exist with name {client}!')
            raise IdentityProviderNotFoundException()

        client_id = identity_provider.client_id
        redirect_uri = identity_provider.return_uri
        authorization_base_url = identity_provider.authorization_uri

        logger.info(f'Trying to linking  with {client}!')

        if identity_provider.slug == 'google':
            scope = [
                'https://www.googleregistration_apis.com/auth/userinfo.email',
                'https://www.googleregistration_apis.com/auth/userinfo.profile'
            ]
        else:
            scope = ['r_liteprofile', 'r_emailaddress']

        client = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
        authorization_url, state = client.authorization_url(authorization_base_url)

        request.session['oauth_state'] = state
        request.session['linking'] = 'linking'
        return redirect(authorization_url)


class ProfileUnlinkingViewSet(viewsets.ViewSet, SharedMixin):
    http_method_names = ['get', ]
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        client = self.request.query_params.get('client', None)

        profile_link = ProfileLink.objects.filter(profile=request.profile)

        if profile_link.count() > 1:
            profile_link.filter(identity_provider__slug=client).delete()
            logger.info(f'{client} profile unlinked successfully!')
            return Response(self.get_identity_providers(request.profile), status=HTTP_200_OK)
        else:
            logger.warning(f'You can not unlink your last account!')
            raise UnlinkException()


class LogoutViewSet(JWTMixin, viewsets.ViewSet):
    http_method_names = ['get', ]
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to logout!')
        response = Response('Succesfully Logout!', status=HTTP_200_OK)
        self.delete_cookies(response)
        logger.info(f'Logout successfully!')
        return response


class RefreshTokenViewSet(JWTMixin, viewsets.ViewSet):
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        if 'refresh_token' in request.COOKIES:
            logger.info(f'Trying to refresh token!')
            refresh_token = request.COOKIES['refresh_token']
            new_tokens = self.get_new_access_token(refresh_token)
            response = Response('Token refresh succesful!', status=HTTP_200_OK)
            self.set_cookies(response, new_tokens)
            logger.info(f'Token refresh succesful!')
            return response
        logger.error(f'Profile credentials were not found in the headers or body!')
        raise ProfileCredentialsRequiredException()


class ProfileLinksViewSet(viewsets.ModelViewSet, SharedMixin):
    queryset = ProfileLink.objects.all()
    serializer_class = ProfileLinkSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', ]

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get profile links!')
        return Response(self.get_identity_providers(request.profile), status=HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet, SharedMixin):
    queryset = Profile.objects.all()
    serializer_class = CheckValidationSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'head', 'patch', 'update', 'post']

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get profile!')
        serializer = ProfileSerializer(request.profile, context={'request': request})
        logger.info(f'Profile got successfully!')
        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        kwargs = {}

        logger.info(f'Trying to create profile!')

        if 'first_name' in data:
            kwargs['first_name'] = data['first_name'][0]

        if 'last_name' in data:
            kwargs['last_name'] = data['last_name'][0]

        if 'profile_picture_uri' in data:
            kwargs['profile_picture_uri'] = data['profile_picture_uri'][0] if data['profile_picture_uri'][0] else None

        if 'terms_accepted' in data:
            kwargs['terms_accepted'] = data['terms_accepted'][0]

        if 'date_of_birth' in data:
            kwargs['date_of_birth'] = data['date_of_birth'][0] if data['date_of_birth'][0] else None

        print(kwargs)

        profile_preferences = [val[0] for key, val in data.items() if 'profile_preferences' in key]

        serializer = CheckValidationSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)

        if profile_preferences:
            self.update_or_create_profile_preferences(request.profile, profile_preferences)

        profile, created = Profile.objects.update_or_create(id=request.profile.id, defaults=kwargs)

        serializer = ProfileSerializer(profile, context={'request': request})
        logger.info(f'Profile created successfully!')
        return Response(serializer.data, status=HTTP_200_OK)


class ProfileDeleteViewSet(JWTMixin, viewsets.ViewSet):
    http_method_names = ['get', ]
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        ProfileCommunicationMedium.objects.filter(profile=request.profile).delete()
        logger.info(f'Profile communication medium deleted successfully!')
        ProfileLink.objects.filter(profile=request.profile).delete()
        logger.info(f'Profile Link deleted successfully!')
        ProfilePreference.objects.filter(profile=request.profile).delete()
        logger.info(f'Profile preference deleted successfully!')
        profile = Profile.objects.get(id=request.profile.id)
        profile.date_of_birth = None
        profile.profile_picture_uri = None
        profile.primary_contact_number = None
        profile.terms_accepted = False
        profile.save()
        logger.info(f'Profile info removed successfully!')
        response = Response({'detail': 'Successfully profile deleted'}, status=HTTP_200_OK)
        self.delete_cookies(response)
        return response


class IdentityProviderViewSet(viewsets.ModelViewSet):
    queryset = IdentityProvider.objects.all()
    serializer_class = IdentityProviderSerializer

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get Identity Provider list!')
        queryset = IdentityProvider.objects.all()
        serializer = IdentityProviderSerializer(queryset, many=True, context={'request': request})
        logger.info(f'{queryset.count()} Identity Provider list got successfully!')
        return Response(serializer.data, status=HTTP_200_OK)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def retrieve(self, request, *args, pk=None, **kwargs):
        logger.info(f'Trying to get store  for {pk} !')

        try:
            queryset = Store.objects.get(course_provider_code=pk)
        except Store.DoesNotExist:
            raise ContentNotFoundException()

        serializer = StoreSerializer(queryset)
        logger.info(f'Store for {queryset.name}  got successfully!')
        return Response(serializer.data, status=HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get store list!')
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, many=True, context={'request': request})
        logger.info(f'Store list got successfully!')
        return Response(serializer.data, status=HTTP_200_OK)


class StoreIdentityProviderViewSet(viewsets.ModelViewSet):
    queryset = StoreIdentityProvider.objects.all()
    serializer_class = StoreIdentityProviderSerializer

    def list(self, request, *args, **kwargs):
        logger.info(f'Trying to get store identity provider list!')
        queryset = StoreIdentityProvider.objects.all()
        serializer = StoreIdentityProviderSerializer(queryset, many=True, context={'request': request})
        logger.info(f'Store identity provider list got successfully!')
        return Response(serializer.data, status=HTTP_200_OK)
