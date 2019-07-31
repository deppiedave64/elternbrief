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
    """Custom admin interface for Letter model.
    Allows user to add ResponseBoolFields as well as ResponseSelectionFields."""
    inlines = (ResponseBoolFieldInline, ResponseSelectionFieldInline)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Group)
admin.site.register(ClassGroup)
admin.site.register(Student)
