document.addEventListener('DOMContentLoaded', () => {
    // 1. Scroll suave com offset do header
    const configureSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                e.preventDefault();
                const targetElement = document.querySelector(targetId);

                if (targetElement) {
                    const headerHeight = document.querySelector('header')?.offsetHeight || 0;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });

                    history.pushState(null, null, targetId);
                }
            });
        });

        if ('scrollBehavior' in document.documentElement.style) {
            document.documentElement.style.scrollBehavior = 'smooth';
        }
    };

    // 2. Auto scroll inicial
    const initAutoScroll = () => {
        if (window.location.pathname === '/' || window.location.pathname === '/home') {
            const homeSection = document.getElementById('home');
            if (homeSection) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            setTimeout(() => {
                                const welcomeSection = document.getElementById('welcome');
                                if (welcomeSection) {
                                    const headerHeight = document.querySelector('header')?.offsetHeight || 0;
                                    const targetPosition = welcomeSection.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                                    window.scrollTo({
                                        top: targetPosition,
                                        behavior: 'smooth'
                                    });
                                }
                            }, 1200);
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.7, rootMargin: '0px 0px -50px 0px' });

                observer.observe(homeSection);
            }
        }
    };

    // 3. Animações ao scroll
    const setupScrollAnimations = () => {
        const animateOnScroll = (elements) => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1, rootMargin: '0px 0px -100px 0px' });

            elements.forEach(element => observer.observe(element));
        };

        const animatedElements = document.querySelectorAll('[data-animate]');
        if (animatedElements.length) {
            animatedElements.forEach(el => {
                el.classList.add('opacity-0', 'translate-y-6', 'transition-all', 'duration-500', 'ease-out');
            });
            animateOnScroll(animatedElements);
        }
    };

    // 4. Parallax
    const setupParallax = () => {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        if (parallaxElements.length) {
            const handleScroll = () => {
                parallaxElements.forEach(element => {
                    const speed = parseFloat(element.dataset.parallaxSpeed) || 0.3;
                    const offset = window.pageYOffset * speed;
                    element.style.transform = `translateY(${offset}px)`;
                });
            };
            window.addEventListener('scroll', handleScroll);
            handleScroll();
            return () => window.removeEventListener('scroll', handleScroll);
        }
    };

    // 5. Lazy loading + prefetch
    const optimizeLoading = () => {
        const lazyImages = document.querySelectorAll('img[data-src]');
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.onload = () => {
                            img.classList.add('opacity-100');
                            img.classList.remove('opacity-0');
                        };
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            }, { rootMargin: '200px 0px' });

            lazyImages.forEach(img => {
                img.classList.add('opacity-0', 'transition-opacity', 'duration-500');
                imageObserver.observe(img);
            });
        } else {
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }

        const prefetchResources = [
            'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
        ];
        prefetchResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    };

    // 6. Tema
    const setupThemeToggle = () => {
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        if (themeToggle) {
            const savedTheme = localStorage.getItem('theme') ||
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            if (savedTheme === 'dark') {
                html.classList.add('dark');
                themeToggle.checked = true;
            } else {
                html.classList.remove('dark');
                themeToggle.checked = false;
            }
            themeToggle.addEventListener('change', () => {
                if (themeToggle.checked) {
                    html.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                } else {
                    html.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                }
            });
        }
    };

    // 7. Menu mobile
    const setupMobileMenu = () => {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true';
                mobileMenuButton.setAttribute('aria-expanded', !isExpanded);
                mobileMenu.classList.toggle('hidden');
                if (!isExpanded) {
                    mobileMenu.style.animation = 'slideDown 0.3s ease-out forwards';
                } else {
                    mobileMenu.style.animation = 'slideUp 0.2s ease-out forwards';
                }
            });
            document.querySelectorAll('#mobile-menu a').forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                    mobileMenu.classList.add('hidden');
                });
            });
        }
    };

    // 8. Formulário de contato
    const setupContactForm = () => {
        const contactForm = document.getElementById('contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(contactForm);
                const submitButton = contactForm.querySelector('button[type="submit"]');
                const originalButtonText = submitButton.textContent;
                try {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="flex items-center justify-center"><svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Enviando...</span>';
                    await new Promise(resolve => setTimeout(resolve, 1500));
                    const successMessage = document.createElement('div');
                    successMessage.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4';
                    successMessage.innerHTML = `
                        <strong class="font-bold">Sucesso!</strong>
                        <span class="block sm:inline">Sua mensagem foi enviada. Entraremos em contato em breve.</span>
                    `;
                    contactForm.reset();
                    contactForm.parentNode.insertBefore(successMessage, contactForm);
                    setTimeout(() => successMessage.remove(), 5000);
                } catch (error) {
                    console.error('Erro ao enviar formulário:', error);
                } finally {
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                }
            });
        }
    };

    // Inicialização
    const init = () => {
        optimizeLoading();
        configureSmoothScroll();
        setupScrollAnimations();
        const parallaxCleanup = setupParallax();
        setupThemeToggle();
        setupMobileMenu();
        setupContactForm();
        window.addEventListener('load', () => initAutoScroll());
        window.addEventListener('beforeunload', () => {
            if (parallaxCleanup) parallaxCleanup();
        });
    };

    init();
});
