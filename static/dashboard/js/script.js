

document.addEventListener('DOMContentLoaded', function() {
    
    initializeSidebarToggles();
    
    setupToggleEvents();
});

function initializeSidebarToggles() {
    document.querySelectorAll('.sidebar-toggle').forEach(toggle => {
        const header = toggle.querySelector('.toggle-header');
        const content = toggle.querySelector('.toggle-content');
        const icon = toggle.querySelector('.toggle-icon');
        
        const hasActiveChild = content.querySelector('.actived') !== null;
        
        const toggleId = toggle.getAttribute('data-toggle-id') || Array.from(document.querySelectorAll('.sidebar-toggle')).indexOf(toggle);
        const storedState = localStorage.getItem(`sidebarToggle_${toggleId}`);
        
        const shouldOpen = hasActiveChild || storedState === 'open';
        
        if (shouldOpen) {
            toggle.classList.add('active');
            content.style.display = 'block';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        } else {
            toggle.classList.remove('active');
            content.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }
    });
}

function setupToggleEvents() {
    document.querySelectorAll('.sidebar-toggle .toggle-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const toggle = this.parentElement;
            const content = this.nextElementSibling;
            const icon = this.querySelector('.toggle-icon');
            
            const isOpening = !toggle.classList.contains('active');
            
            toggle.classList.toggle('active');
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
            
            if (isOpening) {
                content.style.display = 'block';
                content.style.height = '0';
                content.offsetHeight; // Força repaint
                content.style.height = content.scrollHeight + 'px';
                
                setTimeout(() => {
                    content.style.height = '';
                }, 300);
            } else {
                content.style.height = content.scrollHeight + 'px';
                content.offsetHeight; 
                content.style.height = '0';
                
                setTimeout(() => {
                    content.style.display = 'none';
                    content.style.height = '';
                }, 300);
            }
            
            const toggleId = toggle.getAttribute('data-toggle-id') || Array.from(document.querySelectorAll('.sidebar-toggle')).indexOf(toggle);
            localStorage.setItem(`sidebarToggle_${toggleId}`, isOpening ? 'open' : 'closed');
        });
    });
    
    document.addEventListener('click', function(e) {
        if (e.target.closest('.sidebar-toggle .toggle-header')) {
            const currentToggle = e.target.closest('.sidebar-toggle');
            
            document.querySelectorAll('.sidebar-toggle').forEach(toggle => {
                if (toggle !== currentToggle && toggle.classList.contains('active')) {
                    const content = toggle.querySelector('.toggle-content');
                    const icon = toggle.querySelector('.toggle-icon');
                    
                    toggle.classList.remove('active');
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                    
                    
                    content.style.height = content.scrollHeight + 'px';
                    content.offsetHeight; 
                    content.style.height = '0';
                    
                    setTimeout(() => {
                        content.style.display = 'none';
                        content.style.height = '';
                    }, 300);
                    
                    const toggleId = toggle.getAttribute('data-toggle-id') || Array.from(document.querySelectorAll('.sidebar-toggle')).indexOf(toggle);
                    localStorage.setItem(`sidebarToggle_${toggleId}`, 'closed');
                }
            });
        }
    });
}

const logoutModal = document.getElementById("logoutModal");
const closeModal = document.getElementById("closeModal");
const cancelLogout = document.getElementById("cancelLogout");

if (logoutModal && closeModal && cancelLogout) {
    
    const openModal = document.getElementById("openModal");
    if (openModal) {
        openModal.addEventListener("click", () => {
            logoutModal.style.display = "block";
            document.body.style.overflow = "hidden"; 
        });
    }

    
    const closeModalFunctions = () => {
        logoutModal.style.display = "none";
        document.body.style.overflow = ""; 
    };

    closeModal.addEventListener("click", closeModalFunctions);
    cancelLogout.addEventListener("click", closeModalFunctions);

    // Fechar ao clicar fora do modal
    window.addEventListener("click", (event) => {
        if (event.target === logoutModal) {
            closeModalFunctions();
        }
    });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const container = document.querySelector('.container-main');
    
    if (sidebar && container) {
        sidebar.classList.toggle('collapsed');
        container.classList.toggle('sidebar-collapsed');
        
        const toggleBtnIcon = document.querySelector('.toggle-btn i');
        if (toggleBtnIcon) {
            toggleBtnIcon.classList.toggle('fa-chevron-left');
            toggleBtnIcon.classList.toggle('fa-chevron-right');
        }
        
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    }
}

// Restaurar estado da sidebar ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar && localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
        const container = document.querySelector('.container-main');
        if (container) container.classList.add('sidebar-collapsed');
    }
});

function toggleDropdown() {
    const dropdown = document.getElementById("myDropdown");
    const userButton = document.getElementById("userDropdownButton");

    if (!dropdown || !userButton) return;

    userButton.classList.toggle("active");

    // Usando requestAnimationFrame para garantir suavidade
    if (dropdown.style.display === "none" || dropdown.style.display === "") {
        dropdown.style.display = "block";
        requestAnimationFrame(() => {
            dropdown.classList.add("show");
        });
    } else {
        dropdown.classList.remove("show");
        // Espera a transição terminar antes de esconder
        dropdown.addEventListener('transitionend', () => {
            if (!dropdown.classList.contains("show")) {
                dropdown.style.display = "none";
            }
        }, { once: true });
    }
}

// Fechar dropdown ao clicar fora
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById("myDropdown");
    const userButton = document.getElementById("userDropdownButton");
    
    if (!dropdown || !userButton) return;

    if (!event.target.closest('.user-dropdown') && !event.target.matches('.user-button')) {
        userButton.classList.remove("active");
        dropdown.classList.remove("show");
        
        // Espera a transição terminar antes de esconder
        dropdown.addEventListener('transitionend', () => {
            if (!dropdown.classList.contains("show")) {
                dropdown.style.display = "none";
            }
        }, { once: true });
    }
});

