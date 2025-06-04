console.log("Program Running")
var updatebuttons = document.getElementsByClassName('update-cart');

for (let i = 0; i < updatebuttons.length; i++) {
    updatebuttons[i].addEventListener('click', function() {
        var productID = this.dataset.product;
        var action = this.dataset.action;
        console.log('Button clicked');  // Debug statement
        console.log('productID:', productID, 'Action:', action);

        if (user === 'AnonymousUser') {
            console.log('User is invalid');
        } else {
            updateUserOrder(productID, action);
        }
    });
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...');

    var url = '/updateitem/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productID': productId, 'action': action })
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then((data) => {
        console.log('Data:', data);
        location.reload();
    })
    .catch((error) => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

