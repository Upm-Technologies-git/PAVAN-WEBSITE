document.addEventListener("DOMContentLoaded", function () {
    const proceedButton = document.getElementById("proceed-to-payment");
    
    if (proceedButton) {
        proceedButton.addEventListener("click", function (event) {
            event.preventDefault();  // Prevent default action

            // Validate shipping method before proceeding
            if (validateShippingSelection()) {
                window.location.href = "/checkout/payment/";  // Redirect to payment page
            }
        });
    }
});

function validateShippingSelection() {
    const shippingMethods = document.getElementsByName("checkoutShippingMethod");
    let isSelected = false;

    for (let i = 0; i < shippingMethods.length; i++) {
        if (shippingMethods[i].checked) {
            isSelected = true;
            break;
        }
    }

    if (!isSelected) {
        alert("Please select a shipping method before proceeding.");
        return false;
    }
    
    return true;
}
