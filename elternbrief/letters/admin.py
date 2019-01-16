from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Group, ClassGroup, Letter, Student, Parent

admin.site.register(Group)
admin.site.register(ClassGroup)
admin.site.register(Letter)
admin.site.register(Student)


class ParentInline(admin.StackedInline):
    model = Parent
    can_delete = False
    verbose_name = "Elternteil"


class UserAdmin(BaseUserAdmin):
    inlines = (ParentInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
