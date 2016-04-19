from __future__ import unicode_literals
import pika
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.conf import settings
from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


def _send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.AMQP_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.AMQP_QUEUE)
    channel.basic_publish(exchange='',
                      routing_key=settings.AMQP_QUEUE,
                      body=message)


@receiver(post_delete)
def delete_model_handler(sender, instance, **kwargs):
    _send_message("The {} has been deleted" .format(instance))


@receiver(post_save)
def save_model_handler(sender, instance, created, **kwargs):
   _send_message("The {} has been {}".format(instance, 'created' if created else 'updated'))