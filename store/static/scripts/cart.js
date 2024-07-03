// cart.js

document.addEventListener("DOMContentLoaded", function () {
    window.updateQuantity = function(itemId, quantity, price) {
        fetch(cartUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                let totalPriceElement = document.getElementById(`total-price-${itemId}`);
                totalPriceElement.textContent = formatPrice(quantity * price);
                updateCartTotal();
                updateTotalItems();
                // Despacha el evento 'cartUpdated' aquí para actualizar el contador en todas las vistas
                document.dispatchEvent(new CustomEvent('cartUpdated'));
            } else {
                alert("Hubo un problema al actualizar la cantidad.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    window.removeFromCart = function(itemId) {
        fetch(`/remove_from_cart/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Asegúrate de incluir el token CSRF
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Verificar si el elemento existe antes de intentar eliminarlo
                let cartItemElement = document.getElementById(`cart-item-${itemId}`);
                if (cartItemElement) {
                    cartItemElement.remove();
                    // Actualizar el contador de artículos en el carrito
                    updateCartTotal();
                    updateTotalItems();
                    // Despacha el evento 'cartUpdated' aquí para actualizar el contador en todas las vistas
                    document.dispatchEvent(new CustomEvent('cartUpdated'));
                } else {
                    console.error('Elemento no encontrado:', `cart-item-${itemId}`);
                }
            } else {
                console.error('Error removing item:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

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

    function formatPrice(amount) {
        return amount.toLocaleString('es-CO', { style: 'currency', currency: 'COP' });
    }

    function updateCartTotal() {
        let cartItems = document.querySelectorAll('.cart-item');
        let grandTotal = 0;
        cartItems.forEach(item => {
            let totalPriceText = item.querySelector('[id^="total-price-"]').textContent;
            let totalPrice = parseFloat(totalPriceText.replace(/[^\d,-]/g, "").replace(/\./g, "").replace(/,/g, "."));
            grandTotal += isNaN(totalPrice) ? 0 : totalPrice;
        });
        document.getElementById('grand-total').textContent = formatPrice(grandTotal);
    }

    function updateTotalItems() {
        let cartItems = document.querySelectorAll('.cart-item');
        let totalItems = 0;
        cartItems.forEach(item => {
            let quantityElement = item.querySelector('select.quantity-sec');
            let quantity = parseInt(quantityElement.value);
            totalItems += isNaN(quantity) ? 0 : quantity;
        });
        document.getElementById('total-items').textContent = `${totalItems} Products`;
    }

    function formatInitialPrices() {
        let priceElements = document.querySelectorAll('[id^="total-price-"]');
        priceElements.forEach(element => {
            let priceText = element.textContent.replace(/[^\d,-]/g, "").replace(/\./g, "").replace(/,/g, ".");
            let price = parseFloat(priceText);
            element.textContent = formatPrice(isNaN(price) ? 0 : price);
        });
        updateCartTotal();
        updateTotalItems();
        fetchCartItemCount();  // Llama a fetchCartItemCount aquí para inicializar el contador
    }

    formatInitialPrices();
});
