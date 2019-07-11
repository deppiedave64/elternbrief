from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Group, ClassGroup, Letter, Student, \
    Profile


class ParentInline(admin.StackedInline):
    """Inline for the Profile model."""
    model = Profile
    can_delete = False
    verbose_name = "Elternteil"


# Add ParentInline to the admin interface for the user model:
class UserAdmin(BaseUserAdmin):
    inlines = (ParentInline,)


# Re-register the User model with the new UserAdmin class:
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Group)
admin.site.register(ClassGroup)
admin.site.register(Letter)
admin.site.register(Student)
