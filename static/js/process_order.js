document.addEventListener("DOMContentLoaded", function () {
    const shippingButton = document.getElementById("proceed-to-shipping");
    if (shippingButton) {
        shippingButton.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default link behavior
            processOrderAndRedirect();
        });
    }
});

function processOrderAndRedirect() {
    const orderData = {
        name: document.getElementById("firstName").value + " " + document.getElementById("lastName").value,
        email: document.getElementById("email").value,
        address: document.getElementById("address").value,
        city: document.getElementById("city") ? document.getElementById("city").value : "N/A",
        state: document.getElementById("state").value,
        zip: document.getElementById("zip").value,
        items: getCartItems()  // Fetch cart items (replace with real cart logic)
    };

    fetch("/checkout/process_order/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            window.location.href = "/checkout/shipping/";  // Redirect to shipping page after success
        } else {
            alert("Error placing order. Please try again.");
        }
    })
    .catch(error => console.error("Error:", error));
}

// Function to fetch CSRF token (required for Django security)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Dummy function to get cart items (replace with actual cart logic)
function getCartItems() {
    return [
        { name: "Nike Air VaporMax", quantity: 1, price: 85.00 },
        { name: "Nike ZoomX Vaporfly", quantity: 1, price: 125.00 }
    ];
}
