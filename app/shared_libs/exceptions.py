from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _
from rest_framework import status


class ProfileCredentialsRequiredException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'invalid_client'
    default_detail = _(u'Profile credentials were not found in the headers or body')


class InvalidProfileCredentialsException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'invalid_user'
    default_detail = _(u'Invalid profile credentials')


class InvalidClientCredentialsException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'invalid_client'
    default_detail = _(u'Invalid client credentials')


class ExpiredAuthorizationCodeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'access_denied'
    default_detail = _(u'Authorization code has expired')


class ExpiredRefreshTokenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'expired_token'
    default_detail = _(u'Refresh token has expired')


class GrantTypeRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The grant type was not specified in the request')


class InvalidGrantTypeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'Invalid grant type')


class CodeRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The code parameter is required')


class UsernameRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The username parameter is required')


class PasswordRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The password parameter is required')


class RefreshTokenRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The refresh token parameter is required')


class AccessTokenRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'The access token is required')


class InvalidAccessTokenException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'invalid_token'
    default_detail = u'The access token provided is invalid'


class ExpiredAccessTokenException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'expired_token'
    default_detail = u'The access token provided has expired'


class ExpiredSectionException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'expired_section'
    default_detail = u'Section has expired'


class ExpiredReservationException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_error = u'expired_section'
    default_detail = u'Reservation has expired'


class InsufficientScopeException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_error = u'insufficient_scope'
    default_detail = u'The request requires higher privileges than provided by the access token'


class AuthorizationCodeNotFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'Authorization code not found')


class RefreshTokenNotFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_error = u'invalid_request'
    default_detail = _(u'Refresh token not found')


class IdentityProviderNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Identity provider not found')


class OAuthStateNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'OAuth state not found')


class ContentNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Content not found')


class ParametersNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Provide valid url parameters')


class SectionNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Section not found')


class CourseFeeNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Provide a valid provider and course name')


class SectionSeatNotAvailableException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Section seat not available')


class ReservationNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Reservation not found')


class OrderNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Order not found')


class PaymentGatewayNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Payment Gateway not found')


class ProfileNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_error = u'invalid_request'
    default_detail = _(u'Params not found')


class UnlinkException(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_error = u'invalid_request'
    default_detail = _(u'You can not unlink this account')


class SectionCourseFeeNotMatchException(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_error = u'invalid_request'
    default_detail = _(u'Section course fee not match with your reserved section fee')
