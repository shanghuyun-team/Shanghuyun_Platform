import cart from './shop.js';

let app = document.getElementById('app');
let temporaryContent = document.getElementById('temporaryContent');

const loadTemplate = () => {
    fetch('/templates/home/shop.html')
    .then(response => response.text())
    .then(html => {
        app.innerHTML = html;
        let contentTab = document.getElementById('contentTab');
        contentTab.innerHTML = temporaryContent.innerHTML;
        temporaryContent.innerHTML = null;
        fetchProducts(); // 在加載模板後加載產品
    });
}

const fetchProducts = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sellerId = urlParams.get('seller_id'); // 從 URL 參數中獲取 seller_id

    fetch(`/api/products/${sellerId}/`)
    .then(response => response.json())
    .then(products => {
        initApp(products, sellerId);
        const productId = urlParams.get('id');
        const product = products.find(p => p.id == productId);
        cart(products);
        fetchProductImages(productId);
    })
    .catch(error => console.error('Error fetching products:', error));
}

const fetchProductImages = (productId) => {
    fetch(`/api/productsImages/${productId}/`)
    .then(response => response.json())
    .then(images => {
        let productPhotosContainer = document.querySelector('.product_photos');
        productPhotosContainer.innerHTML = ''; // 清空之前的內容
        images.forEach(imageData => {
            let imgElement = document.createElement('img');
            imgElement.src = '/media/' + imageData.image;
            imgElement.className = 'products_photos';
            imgElement.style.width = '20vw';
            productPhotosContainer.appendChild(imgElement);
        });
    })
    .catch(error => console.error('Error fetching product images:', error));
}

const initApp = (products, sellerId) => {
    const productId = new URLSearchParams(window.location.search).get('id');
    const thisProduct = products.find(product => product.id == productId);
    if (!thisProduct) {
        window.location.href = "/";
    }
    const mediaUrl = '/media/';
    let detail = document.querySelector('.detail');
    detail.querySelector('.image img').src = mediaUrl +  thisProduct.cover_image;
    detail.querySelector('.name').innerText = thisProduct.name;
    detail.querySelector('.price').innerText = '$' + thisProduct.price;
    detail.querySelector('.description').innerText = thisProduct.description;
    detail.querySelector('.addCart').dataset.id = thisProduct.id;

    let listProductHTML = document.querySelector('.listProduct');
    listProductHTML.innerHTML = ''; // 清空之前的內容

    products.forEach(product => {
        let newProduct = document.createElement('div');
        newProduct.classList.add('item');
        newProduct.innerHTML = 
        `<a href="detail.html?id=${product.id}&seller_id=${sellerId}">
            <img src="${mediaUrl}${product.cover_image}">
        </a>
        <h2>${product.name}</h2>
        <div class="price">$${product.price}</div>
        <button 
            class="addCart" 
            data-id='${product.id}'>
                加入購物車
        </button>`;
        listProductHTML.appendChild(newProduct);
    });
}

loadTemplate();
