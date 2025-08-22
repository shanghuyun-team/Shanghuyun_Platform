from django.shortcuts import render
import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Product, Order, OrderItem

@csrf_exempt
def create_order(request):
    """
    Create an order with multiple products.
    Expected POST JSON format:
    {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
        items_data = data.get("items", [])
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not items_data:
        return JsonResponse({"error": "No items provided"}, status=400)

    # Calculate total amount
    total_amount = 0
    products_to_add = []
    for item in items_data:
        product = get_object_or_404(Product, id=item["product_id"])
        qty = int(item.get("quantity", 1))
        total_amount += product.price * qty
        products_to_add.append((product, qty))

    # Create order (first save to generate ID for merchant_trade_no)
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
    )

    # Assign merchant_trade_no automatically
    order.merchant_trade_no = f"EC{order.id}{uuid.uuid4().hex[:6].upper()}"
    order.save()

    # Create order items
    order_items = []
    for product, qty in products_to_add:
        oi = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=product.price
        )
        order_items.append({
            "product_id": oi.product.id,
            "name": oi.product.name,
            "quantity": oi.quantity,
            "price": float(oi.price)
        })

    return JsonResponse({
        "order_id": order.id,
        "merchant_trade_no": order.merchant_trade_no,
        "total_amount": float(order.total_amount),
        "items": order_items
    })

def order_result(request):
    order_id = request.GET.get("order_id") 
    order = None

    if order_id:
        order = get_object_or_404(Order, id=order_id)

    context = {
        "order": order
    }
    return render(request, "payment_result.html", context)
