from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, DevlogPost, PostCategory, PostComment
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from datetime import date
from django.utils import timezone

class Etapa1Form(forms.Form):
    first_name = forms.CharField(
        label=_('Nome'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': _('Seu nome'),
            'class': 'form-control'
        }),
        error_messages={
            'required': _('Por favor, informe seu nome'),
            'max_length': _('O nome deve ter no máximo 150 caracteres')
        }
    )
    
    last_name = forms.CharField(
        label=_('Sobrenome'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': _('Seu sobrenome'),
            'class': 'form-control'
        }),
        error_messages={
            'required': _('Por favor, informe seu sobrenome')
        }
    )
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'placeholder': _('seu@email.com'),
            'class': 'form-control',
            'autocomplete': 'email'
        }),
        error_messages={
            'required': _('Por favor, informe seu email'),
            'invalid': _('Por favor, informe um email válido')
        }
    )
    
    data_nascimento = forms.DateField(
        label=_('Data de Nascimento'),
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': str(date.today().replace(year=date.today().year - 13)),  # 13 anos mínimo
        }),
        help_text=_('Você deve ter pelo menos 13 anos'),
        error_messages={
            'required': _('Por favor, informe sua data de nascimento')
        }
    )
    
    telefone = forms.CharField(
        label=_('Telefone'),
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': _('(XX) XXXXX-XXXX'),
            'class': 'form-control',
            'data-mask': '(00) 00000-0000'
        }),
        help_text=_('Número com DDD'),
        error_messages={
            'required': _('Por favor, informe seu telefone')
        }
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_('Este email já está cadastrado.'))
        return email
    
    def clean_telefone(self):
        telefone = self.cleaned_data['telefone']
        telefone_limpo = re.sub(r'[^\d]', '', telefone)
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValidationError(_('Número de telefone inválido. Digite o DDD + número.'))
        
        if CustomUser.objects.filter(telefone=telefone_limpo).exists():
            raise ValidationError(_('Este telefone já está cadastrado.'))
            
        return telefone_limpo
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data['data_nascimento']
        idade = (date.today() - data_nascimento).days // 365
        
        if idade < 13:
            raise ValidationError(_('Você deve ter pelo menos 13 anos para se cadastrar.'))
            
        return data_nascimento


class Etapa2Form(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': _('Nome de usuário para login'),
                'class': 'form-control',
                'autocomplete': 'username'
            }),
        }
        error_messages = {
            'username': {
                'required': _('Por favor, escolha um nome de usuário'),
                'unique': _('Este nome de usuário já está em uso.'),
                'max_length': _('O nome de usuário deve ter no máximo 150 caracteres.')
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuração dos campos de senha
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('Crie uma senha segura'),
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        self.fields['password1'].help_text = _(
            'Sua senha deve conter pelo menos 8 caracteres, '
            'não ser muito comum e não ser inteiramente numérica.'
        )
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('Repita a mesma senha'),
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].label = _('Confirmação de senha')
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError(_('Este nome de usuário já está em uso. Escolha outro.'))
        return username


class DevlogPostForm(forms.ModelForm):
    is_published = forms.BooleanField(
        required=False,
        label='Publicar agora?',
        help_text='Marque esta opção para publicar o post imediatamente.'
    )
    
    class Meta:
        model = DevlogPost
        fields = [
            'title',
            'slug',
            'content',
            'excerpt',
            'category',
            'featured_image',
            'meta_description',
            'is_published'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 15}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }
        help_texts = {
            'slug': 'URL amigável para o post (gerado automaticamente se vazio)',
            'meta_description': 'Descrição para SEO (máximo 160 caracteres)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuração inicial do campo is_published
        if self.instance and self.instance.pk:
            self.initial['is_published'] = self.instance.status == DevlogPost.Status.PUBLISHED
        
        # Melhorando o queryset da categoria
        self.fields['category'].queryset = PostCategory.objects.filter(is_active=True)
        
        # Se desejar gerar o slug automaticamente
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            # Gera slug automaticamente do título se vazio
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data['title'])
        
        # Verifica se slug já existe (exceto para a instância atual)
        if DevlogPost.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este slug já está em uso. Escolha outro.')
        
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Atualiza o status baseado no campo is_published
        if self.cleaned_data['is_published']:
            instance.status = DevlogPost.Status.PUBLISHED
            if not instance.published_at:
                instance.published_at = timezone.now()
        else:
            instance.status = DevlogPost.Status.DRAFT
        
        if commit:
            instance.save()
            self.save_m2m()
            
        return instance


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Digite seu comentário aqui...'),
                'class': 'form-control',
                'maxlength': '500'
            }),
        }
        labels = {
            'content': _('Comentário')
        }
        help_texts = {
            'content': _('Máximo de 500 caracteres')
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user:
            instance.user = self.user
        
        if self.post:
            instance.post = self.post
        
        # Auto-aprovação para staff/superusers
        if self.user and (self.user.is_staff or self.user.is_superuser):
            instance.is_approved = True
        
        if commit:
            instance.save()
        
        return instance