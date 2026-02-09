# app_custom_zentlib/signals/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from app_custom_zenith.models import CustomUser, UserProfile, DevlogPost
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Signal para criar perfil do usuário e enviar email de boas-vindas
    quando um novo usuário é registrado.
    """
    if created:
        try:
            # Cria perfil associado
            UserProfile.objects.create(user=instance)
            
            # Envia email de boas-vindas
            if not settings.DEBUG:  # Só envia em produção
                subject = 'Bem-vindo ao ZentlibPixels!'
                message = render_to_string('emails/welcome_email.html', {
                    'user': instance,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=False,
                    html_message=message
                )
                
            logger.info(f'Novo usuário criado: {instance.email}')
            
        except Exception as e:
            logger.error(f'Erro ao criar perfil para {instance.email}: {str(e)}')

@receiver(pre_save, sender=DevlogPost)
def generate_post_slug(sender, instance, **kwargs):
    """
    Gera slug automaticamente para posts do Devlog se não fornecido
    """
    if not instance.slug and instance.title:
        from django.utils.text import slugify
        instance.slug = slugify(instance.title)
        logger.debug(f'Slug gerado para post: {instance.slug}')

@receiver(post_delete, sender=DevlogPost)
def cleanup_post_images(sender, instance, **kwargs):
    """
    Remove imagens associadas quando um post é deletado
    """
    if instance.featured_image:
        try:
            instance.featured_image.delete(save=False)
            logger.info(f'Imagem removida para post {instance.pk}')
        except Exception as e:
            logger.error(f'Erro ao deletar imagem do post {instance.pk}: {str(e)}')

# Importante para conectar os signals
default_app_config = 'app_custom_zentlib.apps.AppCustomZentlihConfig'