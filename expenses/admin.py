from django.contrib import admin
from .models import Expense
from .models import Category

# Register your models here.
admin.site.register(Expense)
admin.site.register(Category)