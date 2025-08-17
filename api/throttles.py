from rest_framework.throttling import UserRateThrottle, SimpleRateThrottle


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

    @staticmethod
    def wait_message(self, wait):
        return f" تعداد تلاش ناموفق بالا!{int(round(wait))}ثانبه صبر کنید "


class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'

    @staticmethod
    def wait_message(self, wait):
        return f" تعداد تلاش ناموفق بالا!{int(round(wait))}ثانبه صبر کنید "


class PhoneNumberRateThrottle(SimpleRateThrottle):
    scope = 'phone'

    def get_cache_key(self, request, view):
        phone = request.data.get('phone_number')
        if not phone:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': phone,
        }
