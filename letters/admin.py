"""
Admin settings for the letters app of the elternbrief project.

It registers all necessary models to allow staff members to
1. create and edit letters,
2. Create and edit users,
3. Create and edit student's profiles,
4. Create and edit groups that students can be assigned to.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Group, ClassGroup, Letter, Student, Profile, \
    ResponseTextField, ResponseBoolField, \
    ResponseSelectionField


class ParentInline(admin.StackedInline):
    """Inline for the Profile model.

    Extends Django's StackedInline class.
    The Profile model serves a proxy model to save additional information
    about a user.
    The ParentInline class lets a staff member edit data stored in a user's
    Profile object in the User model's admin interface.
    """

    model = Profile
    can_delete = False
    verbose_name = "Elternteil"


# Add ParentInline to the admin interface for the user model:
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface definition for the User model.

    Extends the default UserAdmin class but adds the ParentInline in order to
    edit a user's Profile object in place.
    The PartentInline is hidden when adding a new user, because that user does
    not have a profile yet.
    """

    inlines = (ParentInline,)

    # Only show ParentInline when editing an existing user:
    def get_inline_instances(self, request, obj=None):
        if obj:
            return [ParentInline(self.model, self.admin_site)]
        else:
            return []


class ResponseTextFieldInline(admin.StackedInline):
    """Inline for response text fields.

    Extends Django's StackedInline class.
    Lets a staff member add one optional ResponseTextField to a letter.
    """

    model = ResponseTextField
    can_delete = True
    verbose_name = "Textfeld"
    extra = 0
    max_num = 1


class ResponseBoolFieldInline(admin.StackedInline):
    """Inline for response bool fields.

    Extends Django's StackedInline class.
    Lets a staff member add any number of ResponseBoolFields to a letter.
    """

    model = ResponseBoolField
    can_delete = True
    verbose_name = "Ja/Nein-Feld"
    extra = 0


class ResponseSelectionFieldInline(admin.StackedInline):
    """Inline for response selection fields

    Extends Django's StackedInline class.
    Lets a staff member add any number of ResponseSelectionFields to a letter.
    """

    model = ResponseSelectionField
    can_delete = True
    verbose_name = "Auswahlfeld"
    extra = 0


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    """Custom admin interface for Letter model.

    Extends Django's default ModelAdmin class but adds inlines for
    ResponseBoolFields as well as ResponseSelectionFields.
    """

    inlines = (ResponseBoolFieldInline, ResponseSelectionFieldInline)

    def save_model(self, request, obj, form, change):
        """Save this model to the database.

        Set the object's created_by attribute to the current user, if it hasn't
        been set before (e.g. the objects was just created).
        Then call the default ModelAdmin's save_model method.

        This method is called automatically when someone hits 'save' in the
        admin interface.
        """

        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Register models with the default ModelAdmin:
admin.site.register(Group)
admin.site.register(ClassGroup)
admin.site.register(Student)
