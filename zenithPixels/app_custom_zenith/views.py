from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .forms import Etapa1Form, Etapa2Form, DevlogPostForm, PostCommentForm
from .models import CustomUser, UserProfile, DevlogPost, PostLike, PostComment, PostCategory 
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

# Novos imports
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404

logger = logging.getLogger(__name__)

def get_nav_items(request):
    nav_items = {
        'main': [
            {
                'name': 'Home',
                'url': reverse('home'),
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-purple-600 dark:text-yellow-400"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'
            },
            {
                'name': 'Equipe',
                'url': '#team',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-purple-600 dark:text-yellow-400"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
            },
            {
                'name': 'Jogos',
                'url': '#games',
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-purple-600 dark:text-yellow-400"><path d="M2 6v12"></path><path d="M6 12H4"></path><path d="M10 6H8"></path><path d="M10 18H8"></path><path d="M14 6h-2"></path><path d="M14 18h-2"></path><path d="M18 12h-2"></path><path d="M22 6v12"></path><path d="M18 12h2"></path><rect width="8" height="16" x="6" y="4" rx="2"></rect></svg>'
            },
            {
                'name': 'Notícias',
                'url': reverse('devlog'),
                'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-purple-600 dark:text-yellow-400"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h16v14"></path><path d="M14 2v4"></path><path d="M8 2v4"></path><path d="M12 10h4"></path><path d="M12 14h4"></path><path d="M12 18h4"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path><path d="M8 18h.01"></path></svg>'
            }
        ],
        'utility': []
    }

    if request.user.is_authenticated:
        nav_items['utility'].append({
            'name': 'Meu Perfil',
            'url': reverse('profile'),
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-purple-600 dark:text-yellow-400"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
        })
        nav_items['utility'].append({
            'name': 'Sair',
            'url': reverse('logout'),
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 text-purple-600 dark:text-yellow-400"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>'
        })
    else:
        nav_items['utility'].append({
            'name': 'Login',
            'url': reverse('login'),
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-8 h-8 text-purple-600 dark:text-yellow-400"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>'
        })

    nav_items['utility'].append({
        'id': 'theme-toggle',
        'name': 'Tema',
        'icon': '''
            <svg class="w-6 h-6 text-purple-600 dark:text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path id="theme-toggle-dark-icon" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                <g id="theme-toggle-light-icon" class="hidden">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </g>
            </svg>
        '''
    })

    return nav_items

def get_theme_preference(request):
    """Obtém a preferência de tema do usuário"""
    dark_mode = False
    
    # Primeiro verifica se já está na sessão
    if 'dark_mode' in request.session:
        dark_mode = request.session['dark_mode']
        return dark_mode
    
    # Se não está na sessão, verifica no perfil do usuário (se logado)
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            dark_mode = profile.dark_mode
            # Salva na sessão para futuras requisições
            request.session['dark_mode'] = dark_mode
            return dark_mode
        except UserProfile.DoesNotExist:
            # Cria perfil se não existir
            profile = UserProfile.objects.create(user=request.user, dark_mode=False)
            request.session['dark_mode'] = False
            return False
    
    # Se não está logado, verifica no cookie do navegador via request
    theme_cookie = request.COOKIES.get('color-theme', '')
    if theme_cookie == 'dark':
        request.session['dark_mode'] = True
        return True
    elif theme_cookie == 'light':
        request.session['dark_mode'] = False
        return False
    
    # Padrão: light mode
    request.session['dark_mode'] = False
    return False

def get_base_context(request):
    """Função auxiliar para obter contexto base comum"""
    dark_mode = get_theme_preference(request)
    
    return {
        'dark_mode': dark_mode,
        'nav_items': get_nav_items(request),
        'current_path': request.path,
    }

def home(request):
    context = get_base_context(request)
    return render(request, 'index/home.html', context)

def devlog(request):
    # Obter parâmetros da URL
    category_slug = request.GET.get('categoria')
    search_query = request.GET.get('q', '')
    
    # Base query - apenas posts publicados
    posts = DevlogPost.objects.filter(
        status=DevlogPost.Status.PUBLISHED
    ).select_related('category', 'author').order_by('-published_at', '-created_at')
    
    # Aplicar filtro por categoria
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Aplicar busca
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(posts, 10)  # 10 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obter categorias ativas para os filtros
    categories = PostCategory.objects.filter(is_active=True)
    
    # Verificar se usuário curtiu cada post e contar likes/comentários
    for post in page_obj:
        post.likes_count = post.likes.count()
        post.comments_count = post.comments.filter(is_approved=True).count()
        post.user_has_liked = False
        if request.user.is_authenticated:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
    
    context = get_base_context(request)
    context.update({
        'posts': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'page_title': 'Notícias & Devlog'
    })
    return render(request, 'devlog/logs.html', context)

def devlog_post_detail(request, slug):
    """View para visualizar um post específico do devlog"""
    post = get_object_or_404(
        DevlogPost.objects.select_related('author', 'category'),
        slug=slug
    )
    
    # Verificar se o post está publicado ou se o usuário tem permissão
    if post.status != DevlogPost.Status.PUBLISHED:
        if not request.user.is_staff and post.author != request.user:
            raise Http404("Post não encontrado")
    
    # Incrementar contador de visualizações
    post.increment_view_count()
    
    # Obter comentários aprovados
    comments = post.comments.filter(is_approved=True).select_related('user__profile')
    
    # Verificar se usuário atual curtiu o post
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()
    
    # Posts relacionados (da mesma categoria)
    related_posts = DevlogPost.objects.filter(
        category=post.category,
        status=DevlogPost.Status.PUBLISHED
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    # Contar likes e comentários
    likes_count = post.likes.count()
    comments_count = post.comments.filter(is_approved=True).count()
    
    context = get_base_context(request)
    context.update({
        'post': post,
        'comments': comments,
        'user_has_liked': user_has_liked,
        'related_posts': related_posts,
        'likes_count': likes_count,
        'comments_count': comments_count,
        'page_title': post.title
    })
    
    return render(request, 'devlog/post_detail.html', context)

@staff_member_required
def create_devlog_post(request):
    """Criar um novo post do devlog - CORRIGIDA"""
    logger.info(f"=== CREATE POST CHAMADO ===")
    logger.info(f"Usuário: {request.user}")
    logger.info(f"Path: {request.path}")
    
    if request.method == 'POST':
        form = DevlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                
                # Definir status baseado no checkbox
                if form.cleaned_data.get('is_published'):
                    post.status = DevlogPost.Status.PUBLISHED
                    if not post.published_at:
                        post.published_at = timezone.now()
                else:
                    post.status = DevlogPost.Status.DRAFT
                
                post.save()
                form.save_m2m()
                
                logger.info(f"Post criado com sucesso: {post.title} (ID: {post.id}, Slug: {post.slug})")
                messages.success(request, 'Notícia criada com sucesso!')
                return redirect('devlog_post_detail', slug=post.slug)
            except Exception as e:
                logger.error(f"Erro ao salvar post: {str(e)}", exc_info=True)
                messages.error(request, f'Erro ao salvar a notícia: {str(e)}')
        else:
            logger.error(f"Form inválido: {form.errors}")
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = DevlogPostForm()
    
    context = get_base_context(request)
    context.update({
        'form': form,
        'page_title': 'Criar Nova Notícia'
    })
    return render(request, 'devlog/create_post.html', context)

@staff_member_required
def edit_devlog_post(request, slug):
    """Editar um post existente"""
    post = get_object_or_404(DevlogPost, slug=slug)
    
    # Verificar se o usuário é o autor ou superuser
    if not request.user.is_superuser and post.author != request.user:
        messages.error(request, 'Você não tem permissão para editar esta notícia.')
        return redirect('devlog_post_detail', slug=slug)
    
    if request.method == 'POST':
        form = DevlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            
            # Atualizar status baseado no checkbox
            if form.cleaned_data.get('is_published'):
                updated_post.status = DevlogPost.Status.PUBLISHED
                if not updated_post.published_at:
                    updated_post.published_at = timezone.now()
            else:
                updated_post.status = DevlogPost.Status.DRAFT
            
            updated_post.save()
            form.save_m2m()
            
            messages.success(request, 'Notícia atualizada com sucesso!')
            return redirect('devlog_post_detail', slug=updated_post.slug)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Configurar valor inicial do checkbox
        initial_data = {'is_published': post.status == DevlogPost.Status.PUBLISHED}
        form = DevlogPostForm(instance=post, initial=initial_data)
    
    context = get_base_context(request)
    context.update({
        'form': form,
        'post': post,
        'page_title': f'Editar: {post.title}'
    })
    return render(request, 'devlog/create_post.html', context)

@require_POST
@staff_member_required
def delete_devlog_post(request, slug):
    """Deletar um post do devlog - CORRIGIDA"""
    logger.info(f"=== DELETE POST CHAMADO ===")
    logger.info(f"Slug: {slug}")
    logger.info(f"Usuário: {request.user}")
    logger.info(f"Método: {request.method}")
    
    try:
        post = get_object_or_404(DevlogPost, slug=slug)
        
        # Verificar se o usuário é o autor ou superuser
        if not request.user.is_superuser and post.author != request.user:
            messages.error(request, 'Você não tem permissão para excluir esta notícia.')
            return redirect('devlog')
        
        # Salvar título para mensagem
        post_title = post.title
        
        # Deletar imagem se existir
        if post.featured_image:
            try:
                post.featured_image.delete(save=False)
            except:
                pass
        
        # Deletar o post
        post.delete()
        
        logger.info(f"Post excluído: {post_title}")
        messages.success(request, f'Notícia "{post_title}" excluída com sucesso!')
        
    except Exception as e:
        logger.error(f"Erro ao excluir post: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao excluir a notícia: {str(e)}')
    
    return redirect('devlog')

@login_required
def profile(request):
    try:
        profile = request.user.profile
        profile_data = {
            'data_entrada': profile.data_entrada,
            'join_date': request.user.date_joined,
            'role': profile.role if profile.role else '',
            'bio': profile.bio if profile.bio else '',
            'twitter': profile.twitter if profile.twitter else '',
            'linkedin': profile.linkedin if profile.linkedin else '',
            'dark_mode': profile.dark_mode
        }
        profile_data['join_date_display'] = profile_data['join_date'].strftime('%Y-%m')
        
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, dark_mode=False)
        profile_data = {
            'data_entrada': profile.data_entrada,
            'join_date': request.user.date_joined,
            'join_date_display': request.user.date_joined.strftime('%Y-%m'),
            'role': '',
            'bio': '',
            'twitter': '',
            'linkedin': '',
            'dark_mode': False
        }
    
    context = get_base_context(request)
    context.update({
        'profile_data': profile_data,
        'user': request.user,
        'page_title': 'Meu Perfil'
    })
    return render(request, 'profile/person.html', context)

@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
        profile_data = {
            'data_entrada': profile.data_entrada,
            'join_date': request.user.date_joined,
            'role': profile.role if profile.role else '',
            'bio': profile.bio if profile.bio else '',
            'twitter': profile.twitter if profile.twitter else '',
            'linkedin': profile.linkedin if profile.linkedin else '',
            'dark_mode': profile.dark_mode,
            'profile_image_url': profile.get_profile_image_url()
        }
        profile_data['join_date_display'] = profile_data['join_date'].strftime('%Y-%m')
        
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, dark_mode=False)
        profile_data = {
            'data_entrada': profile.data_entrada,
            'join_date': request.user.date_joined,
            'join_date_display': request.user.date_joined.strftime('%Y-%m'),
            'role': '',
            'bio': '',
            'twitter': '',
            'linkedin': '',
            'dark_mode': False,
            'profile_image_url': '/static/images/default_profile.png'
        }
    
    context = get_base_context(request)
    context.update({
        'profile_data': profile_data,
        'user': request.user,
        'page_title': 'Editar Perfil'
    })
    return render(request, 'profile/edit.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        try:
            user = request.user
            profile = user.profile
            
            # Atualiza campos do usuário (nome)
            if 'first_name' in request.POST:
                user.first_name = request.POST.get('first_name', '')
                user.save(update_fields=['first_name'])
            if 'last_name' in request.POST:
                user.last_name = request.POST.get('last_name', '')
                user.save(update_fields=['last_name'])
            
            # Atualiza campos do perfil
            update_fields = []
            
            if 'role' in request.POST:
                profile.role = request.POST.get('role', '')
                update_fields.append('role')
            
            if 'bio' in request.POST:
                profile.bio = request.POST.get('bio', '')
                update_fields.append('bio')
            
            if 'twitter' in request.POST:
                twitter = request.POST.get('twitter', '')
                if twitter and not twitter.startswith('@'):
                    twitter = '@' + twitter
                profile.twitter = twitter
                update_fields.append('twitter')
            
            if 'linkedin' in request.POST:
                profile.linkedin = request.POST.get('linkedin', '')
                update_fields.append('linkedin')
            
            if 'profile_image' in request.FILES:
                if profile.profile_image:
                    profile.profile_image.delete(save=False)
                profile.profile_image = request.FILES['profile_image']
                update_fields.append('profile_image')
            
            if update_fields:
                profile.save(update_fields=update_fields)
            
            return JsonResponse({
                'status': 'success',
                'profile_image_url': profile.get_profile_image_url(),
                'full_name': user.get_full_name(),
                'message': 'Perfil atualizado com sucesso!',
            })
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)

# ===== VIEWS DE INTERAÇÃO =====

@require_POST
@login_required
def like_post(request, post_id):
    """API para curtir/descurtir um post - CORRIGIDA"""
    logger.info(f"=== LIKE POST API CHAMADA ===")
    logger.info(f"Post ID: {post_id}")
    logger.info(f"Usuário: {request.user.username}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        post = get_object_or_404(DevlogPost, id=post_id)
        
        # Verificar se já curtiu
        existing_like = PostLike.objects.filter(user=request.user, post=post).first()
        
        if existing_like:
            # Descurtir
            existing_like.delete()
            liked = False
            logger.info("Like removido")
        else:
            # Curtir
            PostLike.objects.create(user=request.user, post=post)
            liked = True
            logger.info("Like adicionado")
        
        # Atualizar contagem
        likes_count = post.likes.count()
        
        response_data = {
            'status': 'success',
            'liked': liked,
            'likes_count': likes_count,
            'message': 'Curtido!' if liked else 'Curtida removida!'
        }
        
        logger.info(f"Resposta: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro no like_post: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao processar curtida'
        }, status=400)

@require_POST
@login_required
def add_comment(request, slug):  # Mude para slug em vez de post_id
    """API para adicionar comentário"""
    logger.info(f"=== ADD COMMENT API CHAMADA ===")
    logger.info(f"Post slug: {slug}")
    logger.info(f"Usuário: {request.user.username}")
    
    try:
        # Buscar post pelo slug
        post = get_object_or_404(DevlogPost, slug=slug)
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'O comentário não pode estar vazio'
            }, status=400)
        
        if len(content) > 500:
            return JsonResponse({
                'status': 'error',
                'message': 'O comentário deve ter no máximo 500 caracteres'
            }, status=400)
        
        # Criar comentário
        comment = PostComment.objects.create(
            user=request.user,
            post=post,
            content=content,
            is_approved=request.user.is_staff
        )
        
        # URL do avatar
        user_avatar = '/static/images/default_profile.png'
        try:
            if hasattr(request.user, 'profile') and request.user.profile.profile_image:
                user_avatar = request.user.profile.profile_image.url
        except:
            pass
        
        response_data = {
            'status': 'success',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'user_name': request.user.get_short_name(),
                'user_avatar': user_avatar,
                'is_approved': comment.is_approved
            },
            'comments_count': post.comments.filter(is_approved=True).count(),
            'message': 'Comentário enviado com sucesso!'
        }
        
        logger.info(f"Comentário criado: ID {comment.id}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro no add_comment: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao adicionar comentário'
        }, status=500)
    
def share_post(request, post_id):
    """API para obter URL de compartilhamento - CORRIGIDA"""
    logger.info(f"=== SHARE POST API CHAMADA ===")
    logger.info(f"Post ID: {post_id}")
    
    try:
        post = get_object_or_404(DevlogPost, id=post_id)
        post_url = request.build_absolute_uri(post.get_absolute_url())
        
        response_data = {
            'status': 'success',
            'url': post_url,
            'title': post.title,
            'message': f'Confira esta notícia: {post.title}'
        }
        
        logger.info(f"URL gerada: {post_url}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro no share_post: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao gerar link de compartilhamento'
        }, status=400)

@login_required
def get_comments(request, post_id):
    """API para obter comentários de um post"""
    logger.info(f"=== GET COMMENTS CHAMADO ===")
    logger.info(f"Post ID: {post_id}")
    
    try:
        post = get_object_or_404(DevlogPost, id=post_id)
        
        # Obter comentários aprovados (ou não aprovados se for staff)
        if request.user.is_staff:
            comments = post.comments.all().select_related('user__profile')
        else:
            comments = post.comments.filter(is_approved=True).select_related('user__profile')
        
        comments_data = []
        for comment in comments:
            # Obter URL do avatar
            user_avatar = '/static/images/default_profile.png'
            try:
                if comment.user.profile and comment.user.profile.profile_image:
                    user_avatar = comment.user.profile.profile_image.url
            except:
                pass
            
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_approved': comment.is_approved,
                'user': {
                    'name': comment.user.get_short_name(),
                    'avatar': user_avatar
                }
            })
        
        logger.info(f"Comentários encontrados: {len(comments_data)}")
        return JsonResponse(comments_data, safe=False)
        
    except Exception as e:
        logger.error(f"Erro ao obter comentários: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@require_POST
@login_required
def delete_comment(request, comment_id):
    """Deletar comentário (apenas staff ou autor)"""
    logger.info(f"=== DELETE COMMENT CHAMADO ===")
    logger.info(f"Comment ID: {comment_id}")
    
    try:
        comment = get_object_or_404(PostComment, id=comment_id)
        
        # Verificar permissões
        if not request.user.is_staff and comment.user != request.user:
            logger.warning(f"Permissão negada para usuário: {request.user}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Permissão negada'
            }, status=403)
        
        post_id = comment.post.id
        comment.delete()
        logger.info(f"Comentário {comment_id} excluído")
        
        # Atualizar contagem
        post = get_object_or_404(DevlogPost, id=post_id)
        comments_count = post.comments.filter(is_approved=True).count()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comentário excluído',
            'comments_count': comments_count
        })
        
    except Exception as e:
        logger.error(f"Erro ao excluir comentário: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

# ===== VIEWS DE AUTENTICAÇÃO =====

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        logger.info(f"Tentativa de login: {email}")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo(a) de volta, {user.get_short_name()}!')
            
            # Sincronizar tema do perfil com a sessão
            try:
                profile = user.profile
                request.session['dark_mode'] = profile.dark_mode
            except UserProfile.DoesNotExist:
                # Cria perfil se não existir
                profile = UserProfile.objects.create(user=user, dark_mode=False)
                request.session['dark_mode'] = False
            
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou senha incorretos. Por favor, tente novamente.')
    
    context = get_base_context(request)
    context['page_title'] = 'Login'
    return render(request, 'user/login.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')

def cadastro_usuario(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Você já está cadastrado e logado!')
        return redirect('home')
    
    if request.method == 'POST':
        if request.path == reverse('cadastro_usuario'):
            return processar_etapa1(request)
        elif request.path == reverse('cadastro_etapa2'):
            return processar_etapa2(request)
    
    return renderizar_formulario_cadastro(request)

def processar_etapa1(request):
    form = Etapa1Form(request.POST)
    if form.is_valid():
        request.session['dados_etapa1'] = {
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name'],
            'email': form.cleaned_data['email'],
            'data_nascimento': form.cleaned_data['data_nascimento'].isoformat(),
            'telefone': form.cleaned_data['telefone'],
        }
        return redirect('cadastro_etapa2')
    
    messages.error(request, 'Por favor, corrija os erros no formulário.')
    return renderizar_formulario_cadastro(request, form_etapa1=form)

def processar_etapa2(request):
    dados_etapa1 = request.session.get('dados_etapa1')
    if not dados_etapa1:
        messages.error(request, 'Sessão expirada. Por favor, recomece o cadastro.')
        return redirect('cadastro_usuario')
    
    form = Etapa2Form(request.POST)
    if not form.is_valid():
        messages.error(request, 'Por favor, corrija os erros no formulário.')
        return renderizar_formulario_cadastro(request, form_etapa2=form)
    
    try:
        with transaction.atomic():
            user = criar_usuario(dados_etapa1, form.cleaned_data)
            
            # Verifica se já existe um perfil antes de criar
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, dark_mode=False)
            
            login(request, user)
            
            # Inicializar tema para novo usuário
            request.session['dark_mode'] = False
            del request.session['dados_etapa1']
            
            messages.success(request, f'Cadastro realizado com sucesso! Bem-vindo, {user.get_short_name()}!')
            return redirect('home')
        
    except IntegrityError as e:
        logger.error(f"Erro de integridade: {str(e)}")
        if 'username' in str(e):
            form.add_error('username', 'Este nome de usuário já está em uso')
        elif 'email' in str(e):
            form.add_error(None, 'Este email já está cadastrado')
        elif 'telefone' in str(e):
            form.add_error(None, 'Este telefone já está em uso')
        else:
            messages.error(request, 'Erro ao criar conta. Por favor, tente novamente.')
        
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        messages.error(request, 'Ocorreu um erro inesperado. Por favor, tente novamente.')
    
    return renderizar_formulario_cadastro(request, form_etapa2=form)

def criar_usuario(dados_etapa1, dados_etapa2):
    """Função melhorada com validações adicionais"""
    from datetime import datetime
    
    user_data = {
        'username': dados_etapa2['username'],
        'password': dados_etapa2['password1'],
        'email': dados_etapa1['email'],
        'first_name': dados_etapa1['first_name'],
        'last_name': dados_etapa1['last_name'],
        'data_nascimento': datetime.fromisoformat(dados_etapa1['data_nascimento']).date(),
        'telefone': dados_etapa1['telefone'],
    }
    
    return CustomUser.objects.create_user(**user_data)

def renderizar_formulario_cadastro(request, form_etapa1=None, form_etapa2=None):
    if request.path == reverse('cadastro_etapa2'):
        if 'dados_etapa1' not in request.session:
            return redirect('cadastro_usuario')
        form_etapa2 = form_etapa2 or Etapa2Form()
        etapa_atual = 2
    else:
        form_etapa1 = form_etapa1 or Etapa1Form()
        etapa_atual = 1
    
    context = get_base_context(request)
    context.update({
        'form_etapa1': form_etapa1,
        'form_etapa2': form_etapa2,
        'etapa_atual': etapa_atual,
        'page_title': 'Cadastro'
    })
    return render(request, 'user/register.html', context)

def toggle_theme(request):
    # Obter estado atual do tema
    current_theme = request.session.get('dark_mode', False)
    new_theme = not current_theme
    
    # Atualizar na sessão
    request.session['dark_mode'] = new_theme
    
    # Salvar a preferência do usuário se estiver autenticado
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            profile.dark_mode = new_theme
            profile.save(update_fields=['dark_mode'])
        except UserProfile.DoesNotExist:
            # Cria perfil se não existir
            UserProfile.objects.create(user=request.user, dark_mode=new_theme)
    
    # Definir sessão para durar mais tempo (1 mês)
    request.session.set_expiry(60 * 60 * 24 * 30)
    
    # Retornar para a página anterior ou home
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

# ===== VIEWS DE MODERAÇÃO =====

@require_POST
@login_required
def approve_comment(request, comment_id):
    """API para aprovar comentário (apenas staff)"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    try:
        comment = get_object_or_404(PostComment, id=comment_id)
        comment.is_approved = True
        comment.save()
        
        # Atualizar contagem
        comments_count = comment.post.comments.filter(is_approved=True).count()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comentário aprovado',
            'comments_count': comments_count
        })
    except Exception as e:
        logger.error(f"Erro ao aprovar comentário: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@login_required
def publish_post(request, post_id):
    """API para publicar post (apenas staff)"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    try:
        post = get_object_or_404(DevlogPost, id=post_id)
        post.status = DevlogPost.Status.PUBLISHED
        if not post.published_at:
            post.published_at = timezone.now()
        post.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notícia publicada'
        })
    except Exception as e:
        logger.error(f"Erro ao publicar post: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@login_required
def archive_post(request, post_id):
    """API para arquivar post (apenas staff)"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permissão negada'}, status=403)
    
    try:
        post = get_object_or_404(DevlogPost, id=post_id)
        post.status = DevlogPost.Status.ARCHIVED
        post.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notícia arquivada'
        })
    except Exception as e:
        logger.error(f"Erro ao arquivar post: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

def chama_espiral_page(request):
    """View para a página do jogo Chama Espiral"""
    return render(request, 'gamepage/chama_espiral.html')

def lilith_view(request):
    """
    View responsável por renderizar a página do jogo Lilith: Search Truth.
    """
    return render(request, 'gamepage/lilith.html')

def lore_portal(request, fragment_id=1):
    # --- 1. BANCO DE DADOS (TODOS OS ITENS DESBLOQUEADOS) ---
    fragments_db = [
        # --- LORE ---
        {'id': 1, 'category': 'lore', 'subcategory': 'historia', 'title': "A Origem da Chama", 'type': "Lore / História", 'status': 'unlocked', 'content': "Há milênios, quando as estrelas ainda dançavam em harmonia com a terra, nasceu a Chama Espiral. Não era apenas fogo, mas a própria essência do conhecimento cósmico...", 'related_ids': [10]},
        {'id': 2, 'category': 'lore', 'subcategory': 'eventos', 'title': "O Grande Eclipse", 'type': "Lore / Eventos", 'status': 'unlocked', 'content': "Durante o Grande Eclipse, a Chama Espiral oscilou pela primeira vez...", 'related_ids': [1]},
        {'id': 3, 'category': 'lore', 'subcategory': 'cronologia', 'title': "Linha do Tempo Alpha", 'type': "Lore / Cronologia", 'status': 'unlocked', 'content': "Registro temporal da primeira era...", 'related_ids': []},

        # --- PERSONAGENS ---
        {'id': 10, 'category': 'personagens', 'subcategory': 'guardioes', 'title': "Os Guardiões Ancestrais", 'type': "Personagens / Guardiões", 'status': 'unlocked', 'content': "Os primeiros a tocar a chama não foram queimados, mas transformados...", 'related_ids': [20]},
        {'id': 11, 'category': 'personagens', 'subcategory': 'lideres', 'title': "Rei Kaelthas", 'type': "Personagens / Líderes", 'status': 'unlocked', 'content': "O último rei a unir as tribos sob a luz da Chama...", 'related_ids': []},
        {'id': 12, 'category': 'personagens', 'subcategory': 'entidades', 'title': "O Observador", 'type': "Personagens / Entidades", 'status': 'unlocked', 'content': "Uma entidade que existe apenas nos reflexos dos espelhos do templo...", 'related_ids': []},

        # --- LOCAIS ---
        {'id': 20, 'category': 'locais', 'subcategory': 'templos', 'title': "Templo Ancestral", 'type': "Locais / Templos", 'status': 'unlocked', 'content': "No coração da montanha sagrada, o Templo Ancestral foi erguido...", 'related_ids': [1, 10]},
        {'id': 21, 'category': 'locais', 'subcategory': 'ruinas', 'title': "Ruínas Esquecidas", 'type': "Locais / Ruínas", 'status': 'unlocked', 'content': "Antigas estruturas que precedem até mesmo a Chama...", 'related_ids': []},
        {'id': 22, 'category': 'locais', 'subcategory': 'santuarios', 'title': "Santuário da Luz", 'type': "Locais / Santuários", 'status': 'unlocked', 'content': "Um local de cura e meditação...", 'related_ids': []},

        # --- ARTEFATOS ---
        {'id': 30, 'category': 'artefatos', 'subcategory': 'reliquias', 'title': "Cálice de Fogo", 'type': "Artefatos / Relíquias", 'status': 'unlocked', 'content': "O cálice usado para transportar brasas da chama original...", 'related_ids': []},
        {'id': 31, 'category': 'artefatos', 'subcategory': 'fragmentos', 'title': "Fragmento Estelar", 'type': "Artefatos / Fragmentos", 'status': 'unlocked', 'content': "Um pedaço de estrela solidificado...", 'related_ids': []},

        # --- GALERIA ---
        {'id': 40, 'category': 'galeria', 'subcategory': 'concept_art', 'title': "Concept: Templo", 'type': "Galeria / Concept Art", 'status': 'unlocked', 'content': "Esboços originais da arquitetura do templo...", 'related_ids': []},
        {'id': 41, 'category': 'galeria', 'subcategory': 'ilustracoes', 'title': "Batalha Final", 'type': "Galeria / Ilustrações", 'status': 'unlocked', 'content': "Representação artística da grande guerra...", 'related_ids': []},

        # --- PUZZLES ---
        {'id': 50, 'category': 'puzzles', 'subcategory': 'facil', 'title': "Enigma da Porta", 'type': "Puzzles / Fácil", 'status': 'unlocked', 'content': "Fale 'amigo' e entre...", 'related_ids': []},
        {'id': 51, 'category': 'puzzles', 'subcategory': 'medio', 'title': "Torres de Hanoi", 'type': "Puzzles / Médio", 'status': 'unlocked', 'content': "Mova os discos sem colocar um maior sobre um menor...", 'related_ids': []},
        {'id': 52, 'category': 'puzzles', 'subcategory': 'dificil', 'title': "Cubo do Tempo", 'type': "Puzzles / Difícil", 'status': 'unlocked', 'content': "Alinhe as faces em quatro dimensões...", 'related_ids': []},

        # --- EXTRAS ---
        {'id': 60, 'category': 'extras', 'subcategory': 'curiosidades', 'title': "Easter Egg #1", 'type': "Extras / Curiosidades", 'status': 'unlocked', 'content': "Os desenvolvedores esconderam suas iniciais nas estrelas...", 'related_ids': []},
        {'id': 61, 'category': 'extras', 'subcategory': 'referencias', 'title': "Inspirações", 'type': "Extras / Referências", 'status': 'unlocked', 'content': "Baseado em mitologias antigas...", 'related_ids': []},
    ]

    # --- 2. LÓGICA DE SELEÇÃO ---
    try:
        selected_item = next((f for f in fragments_db if f['id'] == int(fragment_id)), fragments_db[0])
    except:
        selected_item = fragments_db[0]

    # --- 3. HELPER DE LINKS ---
    def get_first_id(cat, subcat=None):
        found = next((f for f in fragments_db if f['category'] == cat and (subcat is None or f['subcategory'] == subcat)), None)
        return found['id'] if found else 1

    # --- 4. LINKS DE NAVEGAÇÃO ---
    nav_links = {
        'lore_historia': get_first_id('lore', 'historia'),
        'lore_eventos': get_first_id('lore', 'eventos'),
        'lore_cronologia': get_first_id('lore', 'cronologia'),
        'personagens_guardioes': get_first_id('personagens', 'guardioes'),
        'personagens_lideres': get_first_id('personagens', 'lideres'),
        'personagens_entidades': get_first_id('personagens', 'entidades'),
        'locais_templos': get_first_id('locais', 'templos'),
        'locais_ruinas': get_first_id('locais', 'ruinas'),
        'locais_santuarios': get_first_id('locais', 'santuarios'),
        'artefatos_reliquias': get_first_id('artefatos', 'reliquias'),
        'artefatos_fragmentos': get_first_id('artefatos', 'fragmentos'),
        'galeria_concept': get_first_id('galeria', 'concept_art'),
        'galeria_ilustracoes': get_first_id('galeria', 'ilustracoes'),
        'puzzles_facil': get_first_id('puzzles', 'facil'),
        'puzzles_medio': get_first_id('puzzles', 'medio'),
        'puzzles_dificil': get_first_id('puzzles', 'dificil'),
        'extras_curiosidades': get_first_id('extras', 'curiosidades'),
        'extras_referencias': get_first_id('extras', 'referencias'),
    }

    # --- 5. LINKS PRINCIPAIS ---
    main_category_links = {
        'lore': nav_links['lore_historia'],
        'personagens': nav_links['personagens_guardioes'],
        'locais': nav_links['locais_templos'],
        'artefatos': nav_links['artefatos_reliquias'],
        'galeria': nav_links['galeria_concept'],
        'puzzles': nav_links['puzzles_facil'],
        'extras': nav_links['extras_curiosidades'],
    }

    # --- 6. FILTRO DA LISTA DO MEIO ---
    current_list_items = [
        f for f in fragments_db 
        if f['category'] == selected_item['category'] and f['subcategory'] == selected_item['subcategory']
    ]

    # --- 7. CONTAGENS ---
    def count_sub(cat, sub):
        return len([f for f in fragments_db if f['category'] == cat and f['subcategory'] == sub])

    counts = {
        'historia': count_sub('lore', 'historia'), 'eventos': count_sub('lore', 'eventos'), 'cronologia': count_sub('lore', 'cronologia'),
        'guardioes': count_sub('personagens', 'guardioes'), 'lideres': count_sub('personagens', 'lideres'), 'entidades': count_sub('personagens', 'entidades'),
        'templos': count_sub('locais', 'templos'), 'ruinas': count_sub('locais', 'ruinas'), 'santuarios': count_sub('locais', 'santuarios'),
        'reliquias': count_sub('artefatos', 'reliquias'), 'fragmentos': count_sub('artefatos', 'fragmentos'),
        'concept': count_sub('galeria', 'concept_art'), 'ilustracoes': count_sub('galeria', 'ilustracoes'),
        'facil': count_sub('puzzles', 'facil'), 'medio': count_sub('puzzles', 'medio'), 'dificil': count_sub('puzzles', 'dificil'),
        'curiosidades': count_sub('extras', 'curiosidades'), 'referencias': count_sub('extras', 'referencias'),
    }

    total_items = len(fragments_db)
    unlocked_count = len([f for f in fragments_db if f['status'] == 'unlocked'])
    progress_percent = int((unlocked_count / total_items) * 100) if total_items > 0 else 0

    context = {
        'selected': selected_item,
        'current_list_items': current_list_items,
        'related_items': [f for f in fragments_db if f['id'] in selected_item.get('related_ids', [])],
        'nav_links': nav_links,
        'main_links': main_category_links,
        'counts': counts,
        'active_category': selected_item['category'],
        'active_subcategory': selected_item['subcategory'],
        'total_items': total_items,
        'unlocked_count': unlocked_count,
        'progress_percent': progress_percent
    }

    return render(request, 'gamepage/chama_espiralLore.html', context)
   