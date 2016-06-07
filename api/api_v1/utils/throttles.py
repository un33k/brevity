from rest_framework.throttling import UserRateThrottle


class ProfileCreateRateThrottle(UserRateThrottle):
    scope = 'profile_create'


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'
