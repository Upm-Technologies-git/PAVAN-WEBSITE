document.addEventListener("DOMContentLoaded", function () {
    const proceedButton = document.getElementById("proceed-to-checkout");
    
    if (proceedButton) {
        proceedButton.addEventListener("click", function (event) {
            event.preventDefault();  // Prevent default form submission

            // Validate form fields before proceeding
            if (validateCheckoutForm()) {
                window.location.href = "/checkout/shipping/";  // Redirect to the shipping page
            }
        });
    }
});

function validateCheckoutForm() {
    const firstName = document.getElementById("firstName").value.trim();
    const lastName = document.getElementById("lastName").value.trim();
    const email = document.getElementById("email").value.trim();
    const address = document.getElementById("address").value.trim();
    const state = document.getElementById("state").value;
    const zip = document.getElementById("zip").value.trim();

    if (!firstName || !lastName || !email || !address || !state || !zip) {
        alert("Please fill in all required fields before proceeding.");
        return false;
    }
    
    return true;
}
