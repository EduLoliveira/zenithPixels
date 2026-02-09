// static/js/interactions.js

class PostInteractions {
    constructor() {
        this.csrfToken = this.getCsrfToken();
        console.log('Interações inicializadas. CSRF:', this.csrfToken ? 'OK' : 'FALHA');
        this.bindEvents();
    }
    
    getCsrfToken() {
        // Método 1: Meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) return metaToken.getAttribute('content');
        
        // Método 2: Input hidden
        const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (csrfInput) return csrfInput.value;
        
        // Método 3: Cookie
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
    
    showMessage(message, type = 'info') {
        if (typeof showNotification === 'function') {
            showNotification(message, type);
            return;
        }
        
        // Fallback simples
        const div = document.createElement('div');
        div.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            'bg-blue-500'
        }`;
        div.textContent = message;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    }
    
    async handleLike(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const button = event.currentTarget;
        const postId = button.dataset.postId;
        
        if (!postId) {
            this.showMessage('Erro: Post não identificado', 'error');
            return;
        }
        
        if (button.disabled) {
            this.showMessage('Faça login para curtir', 'error');
            return;
        }
        
        // Efeito visual
        button.classList.add('animate-pulse-once');
        
        try {
            const response = await fetch(`/api/post/${postId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Atualizar ícone e contador
                const likeIcon = button.querySelector('svg');
                const likeCount = button.querySelector('.like-count');
                
                if (data.liked) {
                    likeIcon.setAttribute('fill', 'currentColor');
                    button.classList.add('text-brand-yellow');
                } else {
                    likeIcon.setAttribute('fill', 'none');
                    button.classList.remove('text-brand-yellow');
                }
                
                if (likeCount) {
                    likeCount.textContent = data.likes_count;
                }
                
                this.showMessage(data.message, 'success');
            } else {
                this.showMessage(data.message || 'Erro ao curtir', 'error');
            }
        } catch (error) {
            console.error('Erro ao curtir:', error);
            this.showMessage('Erro de conexão', 'error');
        } finally {
            setTimeout(() => button.classList.remove('animate-pulse-once'), 300);
        }
    }
    
    async handleShare(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const button = event.currentTarget;
        const postId = button.dataset.postId;
        
        if (!postId) {
            this.showMessage('Erro: Post não identificado', 'error');
            return;
        }
        
        try {
            const response = await fetch(`/api/post/${postId}/share/`);
            const data = await response.json();
            
            if (data.status === 'success') {
                // Tentar Web Share API primeiro
                if (navigator.share) {
                    try {
                        await navigator.share({
                            title: data.title,
                            text: data.message,
                            url: data.url
                        });
                    } catch (shareError) {
                        if (shareError.name !== 'AbortError') {
                            // Fallback para cópia
                            await navigator.clipboard.writeText(data.url);
                            this.showMessage('Link copiado!', 'success');
                        }
                    }
                } else {
                    // Fallback para navegadores antigos
                    await navigator.clipboard.writeText(data.url);
                    this.showMessage('Link copiado!', 'success');
                }
            } else {
                this.showMessage(data.message || 'Erro ao compartilhar', 'error');
            }
        } catch (error) {
            console.error('Erro ao compartilhar:', error);
            this.showMessage('Erro ao compartilhar', 'error');
        }
    }
    
    bindEvents() {
        // Curtir
        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', this.handleLike.bind(this));
        });
        
        // Compartilhar
        document.querySelectorAll('.share-btn').forEach(btn => {
            btn.addEventListener('click', this.handleShare.bind(this));
        });
        
        // Comentar (se houver modal)
        document.querySelectorAll('.comment-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showMessage('Funcionalidade de comentários em desenvolvimento', 'info');
            });
        });
    }
}

// Inicializar quando o DOM carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.postInteractions = new PostInteractions();
    });
} else {
    window.postInteractions = new PostInteractions();
}