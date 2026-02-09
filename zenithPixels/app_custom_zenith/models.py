from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.utils.text import slugify

class CustomUserManager(BaseUserManager):
    """Gerenciador personalizado para o modelo CustomUser"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O email é obrigatório'))
        if not username:
            raise ValueError(_('O nome de usuário é obrigatório'))
            
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário deve ter is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    """Modelo de usuário personalizado com campos adicionais"""
    
    first_name = models.CharField(
        _('nome'),
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        _('sobrenome'),
        max_length=150,
        blank=False
    )
    email = models.EmailField(
        _('endereço de email'),
        unique=True,
        blank=False,
        error_messages={
            'unique': _("Já existe uma conta com este endereço de email."),
        }
    )
    data_nascimento = models.DateField(
        _('data de nascimento'),
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                limit_value=date(1900, 1, 1),
                message=_('Data de nascimento inválida.')
            )
        ]
    )
    telefone = models.CharField(
        _('telefone'),
        max_length=20,
        unique=True,
        blank=False,
        error_messages={
            'unique': _("Este número de telefone já está em uso."),
        }
    )
    
    date_joined = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    last_login = models.DateTimeField(_('último login'), auto_now=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'telefone', 'data_nascimento']
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['telefone']),
        ]
    
    def clean(self):
        super().clean()
        if hasattr(self, 'telefone'):
            self.telefone = re.sub(r'[^\d]', '', self.telefone)
        
        if self.data_nascimento:
            idade = (date.today() - self.data_nascimento).days // 365
            if idade < 13:
                raise ValidationError(_('Você deve ter pelo menos 13 anos para se cadastrar.'))
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def age(self):
        if self.data_nascimento:
            return (date.today() - self.data_nascimento).days // 365
        return None
    
    @age.setter
    def age(self, value):
        pass
    
    @property
    def formatted_phone(self):
        phone = self.telefone
        if len(phone) == 11:
            return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
        elif len(phone) == 10:
            return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        return phone
    
    @formatted_phone.setter
    def formatted_phone(self, value):
        pass

class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('usuário')
    )
    data_entrada = models.DateField(
        _('data de entrada'),
        auto_now_add=True,
        null=True,
        blank=True
    )
    
    dark_mode = models.BooleanField(
        _('modo escuro'),
        default=False,
        help_text=_('Prefere usar o modo escuro?')
    )
    
    role = models.CharField(
        _('cargo/função'),
        max_length=100,
        blank=True,
        null=True
    )
    
    bio = models.TextField(
        _('biografia'),
        max_length=500,
        blank=True
    )
    
    profile_image = models.ImageField(
        _('foto de perfil'),
        upload_to='profile_images/%Y/%m/',
        null=True,
        blank=True,
        help_text=_('Imagem de perfil do usuário')
    )
    
    twitter = models.CharField(
        _('Twitter'),
        max_length=100,
        blank=True,
        null=True
    )
    
    linkedin = models.CharField(
        _('LinkedIn'),
        max_length=100,
        blank=True,
        null=True
    )
    
    website = models.URLField(
        _('website'),
        blank=True,
        null=True
    )
    
    location = models.CharField(
        _('localização'),
        max_length=100,
        blank=True,
        null=True
    )
    
    birth_date_visibility = models.CharField(
        _('visibilidade da data de nascimento'),
        max_length=10,
        choices=[
            ('public', _('Público')),
            ('friends', _('Apenas amigos')),
            ('private', _('Privado'))
        ],
        default='private'
    )
    
    updated_at = models.DateTimeField(
        _('última atualização'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('perfil de usuário')
        verbose_name_plural = _('perfis de usuários')
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
    
    def get_profile_data(self):
        return {
            'join_date': self.user.date_joined.strftime('%Y-%m-%d'),
            'data_entrada': self.data_entrada.strftime('%Y-%m-%d') if self.data_entrada else self.user.date_joined.strftime('%Y-%m-%d'),
            'role': self.role or '',
            'bio': self.bio or '',
            'twitter': self.twitter or '',
            'linkedin': self.linkedin or '',
            'dark_mode': self.dark_mode
        }
    
    def get_profile_image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/images/default_profile.png'
    
    def get_absolute_url(self):
        return reverse('profile')

class PostCategory(models.Model):
    name = models.CharField(
        max_length=50, 
        verbose_name=_('nome'),
        unique=True
    )
    slug = models.SlugField(
        unique=True, 
        verbose_name=_('slug'),
        max_length=60,
        blank=True
    )
    color = models.CharField(
        max_length=7, 
        default='#6d28d9',
        verbose_name=_('cor'),
        help_text=_('Cor em hexadecimal (ex: #6d28d9)')
    )
    description = models.TextField(
        _('descrição'),
        max_length=200,
        blank=True
    )
    is_active = models.BooleanField(
        _('ativo'),
        default=True
    )
    created_at = models.DateTimeField(
        _('data de criação'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('categoria de post')
        verbose_name_plural = _('categorias de posts')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('devlog') + f'?categoria={self.slug}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        if self.color:
            self.color = self.color.lower()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default_categories(cls):
        defaults = [
            {'name': 'Patches/Updates', 'slug': 'patches', 'color': '#f59e0b'},
            {'name': 'Devlog', 'slug': 'devlog', 'color': '#6d28d9'},
            {'name': 'Notícias', 'slug': 'noticias', 'color': '#2563eb'}
        ]
        
        for cat_data in defaults:
            cls.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'color': cat_data['color']
                }
            )

class DevlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Rascunho')
        PUBLISHED = 'published', _('Publicado')
        ARCHIVED = 'archived', _('Arquivado')
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('título'),
        unique=True,
        help_text=_('Título do post (máximo 200 caracteres)')
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name=_('slug'),
        allow_unicode=True,
        help_text=_('URL amigável para o post (gerado automaticamente se vazio)'),
        blank=True
    )
    content = models.TextField(
        verbose_name=_('conteúdo'),
        help_text=_('Conteúdo principal do post')
    )
    excerpt = models.TextField(
        max_length=300,
        verbose_name=_('resumo'),
        help_text=_('Breve resumo do post (máximo 300 caracteres)'),
        blank=True
    )
    category = models.ForeignKey(
        PostCategory,
        on_delete=models.PROTECT,
        verbose_name=_('categoria'),
        related_name='posts',
        limit_choices_to={'is_active': True}
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name=_('autor'),
        related_name='devlog_posts',
        editable=False
    )
    featured_image = models.ImageField(
        upload_to='devlog_images/%Y/%m/',
        verbose_name=_('imagem destacada'),
        blank=True,
        null=True,
        help_text=_('Imagem principal do post (recomendado 1200x630 pixels)')
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('status'),
        db_index=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('data de criação'),
        editable=False
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('última atualização'),
        editable=False
    )
    published_at = models.DateTimeField(
        verbose_name=_('data de publicação'),
        null=True,
        blank=True,
        editable=False
    )
    view_count = models.PositiveIntegerField(
        verbose_name=_('visualizações'),
        default=0,
        editable=False
    )
    meta_description = models.CharField(
        max_length=160,
        verbose_name=_('meta descrição'),
        blank=True,
        help_text=_('Descrição para SEO (máximo 160 caracteres)')
    )
    
    class Meta:
        verbose_name = _('post do devlog')
        verbose_name_plural = _('posts do devlog')
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['published_at']),
        ]
        permissions = [
            ('can_publish_post', _('Pode publicar posts')),
            ('can_archive_post', _('Pode arquivar posts')),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('devlog_post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED
    
    @is_published.setter
    def is_published(self, value):
        pass
    
    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT
    
    @is_draft.setter
    def is_draft(self, value):
        pass
    
    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED
    
    @is_archived.setter
    def is_archived(self, value):
        pass
    
    @classmethod
    def published(cls):
        return cls.objects.filter(status=cls.Status.PUBLISHED)
    
    @classmethod
    def drafts(cls):
        return cls.objects.filter(status=cls.Status.DRAFT)
    
    @classmethod
    def archived(cls):
        return cls.objects.filter(status=cls.Status.ARCHIVED)
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @likes_count.setter
    def likes_count(self, value):
        pass
    
    @property
    def comments_count(self):
        return self.comments.filter(is_approved=True).count()
    
    @comments_count.setter
    def comments_count(self, value):
        pass
    
    def increment_view_count(self):
        self.view_count = models.F('view_count') + 1
        self.save(update_fields=['view_count'])
        self.refresh_from_db(fields=['view_count'])
    
    def user_has_liked(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    @property
    def status_color(self):
        status_colors = {
            self.Status.DRAFT: 'gray',
            self.Status.PUBLISHED: 'green',
            self.Status.ARCHIVED: 'orange'
        }
        return status_colors.get(self.status, 'gray')
    
    @status_color.setter
    def status_color(self, value):
        pass

class PostLike(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('usuário')
    )
    post = models.ForeignKey(
        DevlogPost,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('post')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('data de criação')
    )
    
    class Meta:
        verbose_name = _('curtida')
        verbose_name_plural = _('curtidas')
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_short_name()} curtiu {self.post.title}"

class PostComment(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('usuário')
    )
    post = models.ForeignKey(
        DevlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('post')
    )
    content = models.TextField(
        max_length=500,
        verbose_name=_('conteúdo')
    )
    is_approved = models.BooleanField(
        _('aprovado?'),
        default=False,
        help_text=_('Comentários aprovados são visíveis publicamente')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('data de création')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('última atualização')
    )
    
    class Meta:
        verbose_name = _('comentário')
        verbose_name_plural = _('comentários')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comentário de {self.user.get_short_name()} em {self.post.title}"
    
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#comment-{self.id}"