from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AnonymousThrottle(AnonRateThrottle):
    scope = "anon"


class UserThrottle(UserRateThrottle):
    scope = "user"
