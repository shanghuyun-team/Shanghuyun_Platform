import cart from './shop.js';

let app = document.getElementById('app');
let temporaryContent = document.getElementById('temporaryContent');

// load layout file
const loadTemplate = () => {
    fetch('/templates/home/shop.html')
    .then(response => response.text())
    .then(html => {
        app.innerHTML = html;
        let contentTab = document.getElementById('contentTab');
        if (contentTab) {
            contentTab.innerHTML = temporaryContent.innerHTML;
            temporaryContent.innerHTML = null;
        }
        fetchProducts();  // Fetch products data
    })
}
loadTemplate();

// Fetch products data from the server
const fetchProducts = () => {
    fetch(`/api/products/${sellerId}/`)
    .then(response => response.json())
    .then(products => {
        initApp(products); // Pass the products data to initApp
        cart(products);    // Initialize the cart with products data
    })
    .catch(error => console.error('Error fetching products:', error));
}

const initApp = (products) => {
    let listProductHTML = document.querySelector('.listProduct');
    listProductHTML.innerHTML = null;
    const mediaUrl = '/media/';
    
    products.forEach(product => {
        let newProduct = document.createElement('div');
        newProduct.classList.add('item');
        newProduct.innerHTML = 
        `<a href="detail.html?id=${product.id}&seller_id=${sellerId}">
            <img src="${mediaUrl}${product.cover_image}">
        </a>
        <h2>${product.product_name}</h2>
        <div class="price">$${product.price}</div>
        <button 
            class="addCart" 
            data-id='${product.id}'>
                加入購物車
        </button>`;
        listProductHTML.appendChild(newProduct);
    });
}
