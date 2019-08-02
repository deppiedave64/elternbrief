"""E-Mail funcionality for the letters app of the elternbrief project."""

import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Letter


@receiver(post_save, sender=Letter)
def send_mail_on_new_letter(sender, instance, created, **kwargs):
    """Send mail to parents of all students a letter concerns.

    Called automatically every time a new letter is created.
    """

    if created:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f'{base_dir}/mail_templates/new_letter.txt', 'r') as f:
            template = f.read()

        for student in instance.students:
            msg = template
            msg = msg.replace('[student]', str(student))
            msg = msg.replace('[domain]', settings.HOSTNAME)
            msg = msg.replace('[student_id]', str(student.id))
            msg = msg.replace('[letter_id]', str(instance.id))

            for parent in student.parents:
                parent.email_user(f"Neuer Brief für {student}", msg,
                                  settings.EMAIL_HOST_USER)
