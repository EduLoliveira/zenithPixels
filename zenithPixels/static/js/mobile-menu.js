document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Alternar estado do menu
            if (isExpanded) {
                mobileMenu.classList.add('max-h-0', 'opacity-0');
                mobileMenu.classList.remove('max-h-screen', 'opacity-100');
            } else {
                mobileMenu.classList.remove('max-h-0', 'opacity-0');
                mobileMenu.classList.add('max-h-screen', 'opacity-100');
            }
            
            this.setAttribute('aria-expanded', !isExpanded);
            
            // Alternar ícone
            const icon = this.querySelector('svg');
            if (icon) {
                icon.innerHTML = isExpanded 
                    ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />'
                    : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />';
            }
        });

        // Fechar ao clicar fora
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && e.target !== menuButton) {
                mobileMenu.classList.add('max-h-0', 'opacity-0');
                mobileMenu.classList.remove('max-h-screen', 'opacity-100');
                menuButton.setAttribute('aria-expanded', 'false');
                const icon = menuButton.querySelector('svg');
                if (icon) {
                    icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />';
                }
            }
        });
    }
});