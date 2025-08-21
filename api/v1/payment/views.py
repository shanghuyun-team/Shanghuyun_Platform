from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from .ecpay_payment_sdk import ECPayPaymentSdk
from api.v1.order.models import Order
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

ReturnURL = " https://0824482167f1.ngrok-free.app/api/v1/payment/return/"
OrderResultURL = " https://0824482167f1.ngrok-free.app/order/result/"

def ecpay_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    item_names = "#".join([f"{item.product.name} x {item.quantity}" for item in order.items.all()])

    ecpay_payment_sdk = ECPayPaymentSdk(
        MerchantID=settings.MERCHANT_ID,
        HashKey=settings.HASH_KEY,
        HashIV=settings.HASH_IV,
    )

    order_params = {
        'MerchantTradeNo': order.merchant_trade_no,
        'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'PaymentType': 'aio',
        'TotalAmount': int(order.total_amount),  # 必須是整數
        'TradeDesc': '訂單付款',
        'ItemName': item_names,
        'ReturnURL': ReturnURL,
        'ChoosePayment': 'ALL',
        'OrderResultURL': f'{OrderResultURL}?order_id={order.id}',
        'NeedExtraPaidInfo': 'Y',
        'EncryptType': 1,
    }

    final_order_params = ecpay_payment_sdk.create_order(order_params)
    action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'
    html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
    return HttpResponse(html)


@csrf_exempt
def ecpay_return(request):
    if request.method == 'POST':
        data = request.POST.dict()

        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID=settings.MERCHANT_ID,
            HashKey=settings.HASH_KEY,
            HashIV=settings.HASH_IV,
        )

        try:
            if not ecpay_payment_sdk.compare_check_mac_value(data):
                return JsonResponse({'status': 'fail', 'msg': 'CheckMacValue 驗證失敗'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'fail', 'msg': str(e)}, status=400)

        trade_no = data.get('MerchantTradeNo')
        rtn_code = data.get('RtnCode')

        if rtn_code == '1':  # 付款成功
            try:
                order = Order.objects.get(merchant_trade_no=trade_no)
                order.status = 'paid'
                order.save()
            except Order.DoesNotExist:
                return JsonResponse({'status': 'fail', 'msg': '找不到訂單'}, status=404)

        return HttpResponse('1|OK')