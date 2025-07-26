document.addEventListener('DOMContentLoaded', function() {
    // Enable hover dropdowns for desktop
    document.querySelectorAll('.parent-dropdown').forEach(item => {
        const dropdownMenu = item.querySelector('.dropdown-menu');
        
        // Show dropdown on hover (desktop)
        item.addEventListener('mouseenter', function() {
            if (window.innerWidth >= 992) {
                dropdownMenu.classList.add('show');
            }
        });
        
        // Hide dropdown when mouse leaves
        item.addEventListener('mouseleave', function() {
            if (window.innerWidth >= 992) {
                dropdownMenu.classList.remove('show');
            }
        });
    });

    // Keep parent active when sub-item is clicked (mobile)
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                const parentLink = this.closest('.parent-dropdown').querySelector('.parent-link');
                parentLink.classList.add('active');
            }
        });
    });
});