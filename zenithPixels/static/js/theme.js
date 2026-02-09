document.addEventListener('DOMContentLoaded', function () {
    // Controle do Tema
    const themeToggleBtn = document.getElementById('theme-toggle');
    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');
    
    // Primeiro, verificar e aplicar o tema do localStorage
    function applyThemeFromStorage() {
        const savedTheme = localStorage.getItem('color-theme');
        const htmlElement = document.documentElement;
        
        if (savedTheme === 'dark') {
            htmlElement.classList.add('dark');
            if (darkIcon && lightIcon) {
                lightIcon.classList.remove('hidden');
                darkIcon.classList.add('hidden');
            }
        } else if (savedTheme === 'light') {
            htmlElement.classList.remove('dark');
            if (darkIcon && lightIcon) {
                lightIcon.classList.add('hidden');
                darkIcon.classList.remove('hidden');
            }
        } else {
            // Se não tem no localStorage, usar preferência do sistema
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (systemPrefersDark) {
                htmlElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
                if (darkIcon && lightIcon) {
                    lightIcon.classList.remove('hidden');
                    darkIcon.classList.add('hidden');
                }
            } else {
                localStorage.setItem('color-theme', 'light');
                if (darkIcon && lightIcon) {
                    lightIcon.classList.add('hidden');
                    darkIcon.classList.remove('hidden');
                }
            }
        }
    }
    
    // Aplicar tema inicial
    applyThemeFromStorage();
    
    // Função para alternar tema
    function toggleTheme() {
        const htmlElement = document.documentElement;
        const currentIsDark = htmlElement.classList.contains('dark');
        const newTheme = currentIsDark ? 'light' : 'dark';
        
        // Alternar classe no HTML
        if (currentIsDark) {
            htmlElement.classList.remove('dark');
        } else {
            htmlElement.classList.add('dark');
        }
        
        // Atualizar ícones
        if (darkIcon && lightIcon) {
            if (currentIsDark) {
                lightIcon.classList.add('hidden');
                darkIcon.classList.remove('hidden');
            } else {
                lightIcon.classList.remove('hidden');
                darkIcon.classList.add('hidden');
            }
        }
        
        // Salvar no localStorage
        localStorage.setItem('color-theme', newTheme);
        
        // Sincronizar com o servidor
        fetch('/toggle-theme/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        }).catch(error => {
            // Não fazer nada em caso de erro
        });
    }
    
    // Event listener
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    // Função para pegar cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});