from django.db.models.signals import pre_save
from django.dispatch import receiver
from models import Job

@receiver(post_save, sender=Job)
def my_handler(sender, instance, created, **kwargs):
	print("Request finished!")
	print instance.job_name

