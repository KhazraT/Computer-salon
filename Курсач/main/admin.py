from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .models import User

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_time')
    list_display_links = ('id', 'user')

admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(Returns)
