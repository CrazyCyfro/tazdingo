from django.contrib import admin
from wswrath.models import UserProfile, URL, URLComparison, Rating, CustomComparison

admin.site.register(UserProfile)
admin.site.register(URL)
admin.site.register(URLComparison)
admin.site.register(Rating)
admin.site.register(CustomComparison)