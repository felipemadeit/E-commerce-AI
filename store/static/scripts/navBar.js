document.addEventListener('DOMContentLoaded', function() {
    fetchCartItemCount();
});

function fetchCartItemCount() {
    fetch('/api/cart_item_count/')
        .then(response => response.json())
        .then(data => {
            let totalCartElement = document.getElementById('total-cart');
            if (totalCartElement) {
                totalCartElement.textContent = `${data.total_items}`;
            }
        })
        .catch(error => console.error('Error fetching cart item count:', error));
}