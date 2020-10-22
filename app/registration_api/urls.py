from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from registration_api.views import *

identity_providers = ['google', 'linkedin']

router = routers.DefaultRouter()
schema_view = get_swagger_view(title='Campus Identity API')

router.register(r'login', LoginViewSet, 'login')
router.register(r'logout', LogoutViewSet, 'logout')
router.register(r'refresh_token', RefreshTokenViewSet, 'refresh_token')

router.register(r'identity_provider', IdentityProviderViewSet, 'identity_provider')
router.register(r'store', StoreViewSet, 'store')
router.register(r'store_identity_provider', StoreIdentityProviderViewSet, 'store_identity_provider')

router.register(r'profile_links', ProfileLinksViewSet, 'profile_links')
router.register(r'profile', ProfileViewSet, 'profile')
router.register(r'profile_link', ProfileLinkingViewSet, 'profile_link')
router.register(r'profile_unlink', ProfileUnlinkingViewSet, 'profile_unlink')
router.register(r'profile_delete', ProfileDeleteViewSet, 'profile_delete')

for provider in identity_providers:
    router.register(provider + '/callback', CallBackViewSet, provider + '_callback')

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view),
    path('docs/', include_docs_urls(title='API Documentation'))
]
