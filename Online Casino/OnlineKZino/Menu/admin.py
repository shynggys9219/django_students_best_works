from django.contrib import admin

from Menu.models import CustomUser, Cards, PTslides, RouletteSlides, Slots

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Cards)
admin.site.register(PTslides)
admin.site.register(RouletteSlides)
admin.site.register(Slots)