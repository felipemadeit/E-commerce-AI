document.addEventListener('DOMContentLoaded', function() {
    fetchCartItemCount();

    const menuToggle = document.getElementById('list-nav');
    const buttonToggle = document.getElementById('nav-toggle');

    function unfoldMenu() { 
        if (menuToggle.style.display === 'none' || menuToggle.style.display === '') {
            menuToggle.style.display = 'flex';
        } else {
            menuToggle.style.display = 'none';
        }
    }

    buttonToggle.addEventListener('click', function() {
        unfoldMenu();
    });

    
});

function fetchCartItemCount() {
    fetch('/api/cart_item_count/')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else if (response.status === 401) { // Unauthorized
                window.location.href = '/login/';
                return Promise.reject('User not authenticated');
            } else {
                return Promise.reject('Unexpected response status: ' + response.status);
            }
        })
        .then(data => {
            let totalCartElement = document.getElementById('total-cart');
            if (totalCartElement && data.total_items !== undefined) {
                totalCartElement.textContent = `${data.total_items}`;
            }
        })
        .catch(error => console.error('Error fetching cart item count:', error));
}
