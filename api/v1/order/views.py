from django.shortcuts import render
import json
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from .models import Order, OrderItem
from api.v1.product.models import Product

logger = logging.getLogger(__name__)


@login_required
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

    try:
        data = json.loads(request.body)
        items_data = data.get("items", [])
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    if not items_data:
        return JsonResponse({"error": "No items provided"}, status=400)

    try:
        with transaction.atomic():
            # Calculate total amount and validate products
            total_amount = 0
            products_to_add = []

            for item in items_data:
                try:
                    product_id = int(item.get("product_id", 0))
                    quantity = int(item.get("quantity", 1))

                    if quantity <= 0:
                        return JsonResponse({"error": f"Invalid quantity for product {product_id}"}, status=400)

                    product = get_object_or_404(Product, id=product_id, is_active=True)

                    # Check stock availability
                    if product.stock < quantity:
                        return JsonResponse({
                            "error": f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {quantity}"
                        }, status=400)

                    total_amount += product.price * quantity
                    products_to_add.append((product, quantity))

                except (ValueError, TypeError):
                    return JsonResponse({"error": f"Invalid product data: {item}"}, status=400)

            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
            )

            # Create order items and update stock
            order_items = []
            for product, qty in products_to_add:
                oi = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )

                # Update product stock
                product.stock -= qty
                product.save()
                order_items.append({
                    "product_id": oi.product.id,
                    "name": oi.product.name,
                    "quantity": oi.quantity,
                    "price": float(oi.price),
                    "total": float(oi.price * oi.quantity)
                })

        return JsonResponse({
            "success": True,
            "order_id": order.id,
            "merchant_trade_no": order.merchant_trade_no,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "items": order_items,
            "message": "Order created successfully"
        })

    except Exception as e:
        logger.exception("Order creation failed: %s", e)
        return JsonResponse({"error": f"Order creation failed: {str(e)}"}, status=500)


@login_required
def order_result(request):
    order_id = request.GET.get("order_id")
    order = None

    if order_id:
        try:
            order = get_object_or_404(Order, id=int(order_id))
            # 確保只有訂單的所有者或管理員可以查看
            if not (order.user == request.user or request.user.is_staff):
                order = None  # 不允許查看
        except (ValueError, TypeError):
            order = None

    context = {
        "order": order
    }
    return render(request, "order/order_result.html", context)


@login_required
def order_history(request):
    """用戶訂單紀錄"""
    # 獲取用戶的所有訂單，按創建時間倒序排列
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # 狀態篩選（先篩選再分頁）
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)

    # 統計數據
    user_orders = Order.objects.filter(user=request.user)
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status=Order.STATUS_PENDING).count()
    paid_orders = user_orders.filter(status=Order.STATUS_PAID).count()

    # 分頁處理（篩選後才分頁）
    paginator = Paginator(orders, 10)  # 每頁顯示10個訂單
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'current_status': status_filter or 'all',
    }

    return render(request, "order/order_history.html", context)
