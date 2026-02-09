# debug_urls.py
from django.test import Client
from django.urls import reverse
import sys

def test_all_urls():
    """Testa todas as URLs para verificar se estão funcionando"""
    client = Client()
    
    urls_to_test = [
        ('home', {}, 'GET'),
        ('devlog', {}, 'GET'),
        ('login', {}, 'GET'),
        ('logout', {}, 'GET'),
        ('profile', {}, 'GET'),
        ('profile_edit', {}, 'GET'),
        ('cadastro_usuario', {}, 'GET'),
        ('cadastro_etapa2', {}, 'GET'),
        ('toggle_theme', {}, 'GET'),
        ('create_devlog_post', {}, 'GET'),
    ]
    
    print("=== TESTANDO TODAS AS URLS ===")
    
    for url_name, kwargs, method in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url)
            
            print(f"{url_name}: {url} -> {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ⚠️  404 NOT FOUND!")
            elif response.status_code == 403:
                print(f"   ⚠️  403 FORBIDDEN (precisa de login)")
            elif response.status_code == 200:
                print(f"   ✅  200 OK")
            else:
                print(f"   ❌  {response.status_code} - Status inesperado")
                
        except Exception as e:
            print(f"{url_name}: ERRO - {str(e)}")
    
    print("\n=== TESTANDO URLS DE API ===")
    
    api_urls = [
        ('like_post', {'post_id': 1}, 'POST'),
        ('add_comment', {'post_id': 1}, 'POST'),
        ('share_post', {'post_id': 1}, 'GET'),
        ('get_comments', {'post_id': 1}, 'GET'),
        ('delete_comment', {'comment_id': 1}, 'POST'),
        ('approve_comment', {'comment_id': 1}, 'POST'),
        ('publish_post', {'post_id': 1}, 'POST'),
        ('archive_post', {'post_id': 1}, 'POST'),
        ('delete_devlog_post', {'slug': 'test-post'}, 'POST'),
    ]
    
    for url_name, kwargs, method in api_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"{url_name}: {url} -> [EXISTE]")
        except Exception as e:
            print(f"{url_name}: ❌ ERRO - {str(e)}")

if __name__ == '__main__':
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
    django.setup()
    
    test_all_urls()