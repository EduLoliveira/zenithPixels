from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from app_custom_zenith.views import (
    home, 
    devlog, 
    toggle_theme, 
    cadastro_usuario,
    custom_login,
    custom_logout,
    profile,
    profile_edit,
    profile_update,
    like_post,
    add_comment,
    share_post,
    create_devlog_post,
    edit_devlog_post,
    devlog_post_detail,
    delete_comment,
    get_comments,
    approve_comment,
    publish_post,
    archive_post,
    delete_devlog_post,
    lilith_view,
    chama_espiral_page,
    lore_portal, 
)

urlpatterns = [
    # Página inicial
    path('', home, name='home'),
    
    # --- ROTAS DOS JOGOS ---
    path('chama_espiral/', chama_espiral_page, name='chama_espiral'),
    path('chama-espiral/lore/', lore_portal, name='lore_portal'),
    path('chama-espiral/lore/<int:fragment_id>/', lore_portal, name='lore_detail'),
    
    # Rota do Lilith
    path('games/lilith/', lilith_view, name='lilith_page'),

    # Autenticação
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    
    # Cadastro
    path('cadastro/', cadastro_usuario, name='cadastro_usuario'),
    path('cadastro/etapa2/', cadastro_usuario, name='cadastro_etapa2'),
    
    # Perfil
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/update/', profile_update, name='profile_update'),
    
    # Notícias/Devlog
    path('noticias/', devlog, name='devlog'),
    path('noticias/criar/', create_devlog_post, name='create_devlog_post'),
    path('noticias/editar/<slug:slug>/', edit_devlog_post, name='edit_devlog_post'),
    path('noticias/excluir/<slug:slug>/', delete_devlog_post, name='delete_devlog_post'),
    path('noticias/<slug:slug>/', devlog_post_detail, name='devlog_post_detail'),
    
    # Comentários com slug
    path('noticias/<slug:slug>/comentar/', add_comment, name='add_comment'),
    
    # API - Interações
    path('api/post/<int:post_id>/like/', like_post, name='like_post'),
    path('api/post/<int:post_id>/share/', share_post, name='share_post'),
    path('api/post/<int:post_id>/comments/', get_comments, name='get_comments'),
    
    # API - Moderação
    path('api/comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('api/comment/<int:comment_id>/approve/', approve_comment, name='approve_comment'),
    path('api/post/<int:post_id>/publish/', publish_post, name='publish_post'),
    path('api/post/<int:post_id>/archive/', archive_post, name='archive_post'),
    
    # Funcionalidades
    path('toggle-theme/', toggle_theme, name='toggle_theme'),
    
    # Admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)