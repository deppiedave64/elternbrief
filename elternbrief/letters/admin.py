from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Group, ClassGroup, Letter, Student, Profile, ResponseTextField, ResponseBoolField, \
    ResponseSelectionField


class ParentInline(admin.StackedInline):
    """Inline for the Profile model."""
    model = Profile
    can_delete = False
    verbose_name = "Elternteil"


# Add ParentInline to the admin interface for the user model:
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ParentInline,)


class ResponseTextFieldInline(admin.StackedInline):
    """Inline for response text fields"""
    model = ResponseTextField
    can_delete = True
    verbose_name = "Textfeld"
    extra = 0
    max_num = 1

class ResponseBoolFieldInline(admin.StackedInline):
    """Inline for response bool fields"""
    model = ResponseBoolField
    can_delete = True
    verbose_name = "Ja/Nein-Feld"
    extra = 0

class ResponseSelectionFieldInline(admin.StackedInline):
    """Inline for response selection fields"""
    model = ResponseSelectionField
    can_delete = True
    verbose_name = "Auswahlfeld"
    extra = 0

# Add inlines for all response fields to the admin interface for the letter model:

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    inlines = (ResponseTextFieldInline, ResponseBoolFieldInline, ResponseSelectionFieldInline)


admin.site.register(Group)
admin.site.register(ClassGroup)
# admin.site.register(Letter)
admin.site.register(Student)
