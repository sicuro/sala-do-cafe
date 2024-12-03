// Função de filtragem de categorias
function setupCategoryFilters() {
    const categoryFilters = document.querySelectorAll('.category-filter');
    
    categoryFilters.forEach(button => {
        button.addEventListener('click', function() {
            const selectedCategory = this.getAttribute('data-category');
            
            // Remover estilo de todos os botões
            categoryFilters.forEach(btn => {
                btn.classList.remove('bg-purple-200', 'bg-gray-200', 'bg-green-200', 'bg-blue-200', 'bg-yellow-200', 'bg-red-200');
                btn.classList.add(
                    btn.getAttribute('data-category') === 'todos' ? 'bg-purple-100' : 
                    btn.getAttribute('data-category') === 'geral' ? 'bg-gray-100' :
                    btn.getAttribute('data-category') === 'ambiente' ? 'bg-green-100' :
                    btn.getAttribute('data-category') === 'gestao' ? 'bg-blue-100' :
                    btn.getAttribute('data-category') === 'beneficios' ? 'bg-yellow-100' :
                    btn.getAttribute('data-category') === 'salarios' ? 'bg-red-100' : ''
                );
            });
            
            // Adicionar estilo ao botão selecionado
            this.classList.remove(
                selectedCategory === 'todos' ? 'bg-purple-100' : 
                selectedCategory === 'geral' ? 'bg-gray-100' :
                selectedCategory === 'ambiente' ? 'bg-green-100' :
                selectedCategory === 'gestao' ? 'bg-blue-100' :
                selectedCategory === 'beneficios' ? 'bg-yellow-100' :
                selectedCategory === 'salarios' ? 'bg-red-100' : ''
            );
            this.classList.add(
                selectedCategory === 'todos' ? 'bg-purple-200' : 
                selectedCategory === 'geral' ? 'bg-gray-200' :
                selectedCategory === 'ambiente' ? 'bg-green-200' :
                selectedCategory === 'gestao' ? 'bg-blue-200' :
                selectedCategory === 'beneficios' ? 'bg-yellow-200' :
                selectedCategory === 'salarios' ? 'bg-red-200' : ''
            );
            
            // Filtrar fofocas
            const gossipCards = document.querySelectorAll('.gossip-card');
            gossipCards.forEach(card => {
                const cardCategory = card.querySelector('.category-tag').textContent.toLowerCase();
                
                if (selectedCategory === 'todos' || cardCategory === selectedCategory) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// Adicionar setup de filtros após o carregamento inicial
document.addEventListener('DOMContentLoaded', setupCategoryFilters);
