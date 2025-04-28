const cart = (products) => {
    let listCartHTML = document.querySelector('.listCart');
    let iconCart = document.querySelector('.icon-cart');
    let iconCartSpan = iconCart.querySelector('span');
    let body = document.querySelector('body');
    let closeCart = document.querySelector('.close');
    let cart = [];

    // open and close tab
    iconCart.addEventListener('click', () => {
        body.classList.toggle('activeTabCart');
    })
    closeCart.addEventListener('click', () => {
        body.classList.toggle('activeTabCart');
    })

    const setProductInCart = (idProduct, value) => {
        let positionThisProductInCart = cart.findIndex((value) => value.product_id == idProduct);
        if(value <= 0){
            cart.splice(positionThisProductInCart, 1);
        }else if(positionThisProductInCart < 0){
            cart.push({
                product_id: idProduct,
                quantity: 1
            });
        }else{
            cart[positionThisProductInCart].quantity = value;
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        addCartToHTML();
    }

    const addCartToHTML = () => {
        listCartHTML.innerHTML = '';
        let totalQuantity = 0;
        if(cart.length > 0){
            cart.forEach(item => {
                totalQuantity = totalQuantity +  item.quantity;
                let newItem = document.createElement('div');
                const mediaUrl = '/media/';
                newItem.classList.add('item');
                newItem.dataset.id = item.product_id;
    
                let positionProduct = products.findIndex((value) => value.id == item.product_id);
                if (positionProduct !== -1) {
                    let info = products[positionProduct];
                    listCartHTML.appendChild(newItem);
                    console.log(info);
                    if (info.cover_image) {
                        let coverImage = info.cover_image.replace(/\\/g, '/');
                        newItem.innerHTML = `
                        <div class="image">
                                <img src="${mediaUrl}${coverImage}">
                            </div>
                            <div class="name">
                            ${info.name}
                            </div>
                            <div class="totalPrice">$${info.price * item.quantity}</div>
                            <div class="quantity">
                                <span class="minus" data-id="${info.id}"><</span>
                                <span>${item.quantity}</span>
                                <span class="plus" data-id="${info.id}">></span>
                            </div>
                        `;
                    } else {
                        console.error(`Product with ID ${item.product_id} does not have a cover image.`);
                    }
                } else {
                    console.error(`Product with ID ${item.product_id} not found in products array.`);
                }
            });
        }
        iconCartSpan.innerText = totalQuantity;
    }

    document.addEventListener('click', (event) => {
        let buttonClick = event.target;
        let idProduct = buttonClick.dataset.id;
        let quantity = null;
        let positionProductInCart = cart.findIndex((value) => value.product_id == idProduct);
        switch (true) {
            case (buttonClick.classList.contains('addCart')):
                quantity = (positionProductInCart < 0) ? 1 : cart[positionProductInCart].quantity+1;
                setProductInCart(idProduct, quantity);
                break;
            case (buttonClick.classList.contains('minus')):
                quantity = cart[positionProductInCart].quantity-1;
                setProductInCart(idProduct, quantity);
                break;
            case (buttonClick.classList.contains('plus')):
                quantity = cart[positionProductInCart].quantity+1;
                setProductInCart(idProduct, quantity);
                break;
            default:
                break;
        }
    })

    document.querySelector('.checkOut').addEventListener('click', function() {
        const cart = JSON.parse(localStorage.getItem('cart'));
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(cart)
        })
        .then(response => response.text())
        .then(html => {
            const newWindow = window.open();
            newWindow.document.write(html);
            newWindow.document.forms[0].submit();
        })
        .catch(error => console.error('Error:', error));
    });

    const initApp = () => {
        
    if(localStorage.getItem('cart')){
        cart = JSON.parse(localStorage.getItem('cart'));
        addCartToHTML();
    }
    }
    initApp();
}
export default cart;





