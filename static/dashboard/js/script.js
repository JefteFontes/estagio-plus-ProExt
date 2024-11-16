const openModal = document.getElementById("openModal");
const closeModal = document.getElementById("closeModal");
const modal = document.getElementById("logoutModal");
const cancelLogout = document.getElementById("cancelLogout");

// Abrir o modal
openModal.addEventListener("click", () => {
    modal.style.display = "block";
});

// Fechar o modal ao clicar no botão de fechar
closeModal.addEventListener("click", () => {
    modal.style.display = "none";
});

// Fechar o modal ao clicar no botão "Cancelar"
cancelLogout.addEventListener("click", () => {
    modal.style.display = "none";
});

// Fechar o modal ao clicar fora do conteúdo
window.addEventListener("click", (event) => {
    if (event.target === modal) {
        modal.style.display = "none";
    }
});

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const container = document.querySelector('.container-main');
    
    sidebar.classList.toggle('collapsed'); // Esconde ou mostra a sidebar
    container.classList.toggle('sidebar-collapsed'); // Ajusta o conteúdo
}

function toggleDropdown() {
    console.log("toggleDropdown function executed");
    const dropdown = document.getElementById("myDropdown");
    const userButton = document.getElementById("userDropdownButton");

    userButton.classList.toggle("active");

    // Verifica o estado atual da visibilidade
    if (dropdown.style.display === "none" || dropdown.style.display === "") {
        dropdown.style.display = "block";  // Abre o dropdown
        setTimeout(() => dropdown.classList.add("show"), 10); // Atraso para garantir que o display: block seja aplicado antes da transição
    } else {
        dropdown.classList.remove("show");  // Remove a classe show para fechar com a transição
        setTimeout(() => dropdown.style.display = "none", 300); // Atraso para permitir a animação de transição antes de ocultar
    }
}

// Fecha o dropdown ao clicar fora
window.addEventListener('click', function(event) {
    const dropdown = document.getElementById("myDropdown");
    const userButton = document.getElementById("userDropdownButton");
    if (!event.target.matches('.user-button') && !event.target.closest('.user-dropdown')) {
        // Se o clique não for no botão ou dentro do dropdown, feche o dropdown
        userButton.classList.remove("active");
        dropdown.classList.remove("show");
        setTimeout(() => dropdown.style.display = "none", 300); // Atraso para permitir a transição
    }
});


