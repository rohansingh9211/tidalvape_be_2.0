import os
import json
from pathlib import Path
from django.http import JsonResponse
from importlib.machinery import SourceFileLoader
from CyberSource import *
from y6u.models import *
from CyberSource.rest import ApiException
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from y6u.utils import (Find_total_calculate_for_order, find_total_calculation, generate_unique_order_id, Find_total_calculate, webUserAddressDetail)
from y6u.serializers import OrderItemSerializer, UserOrderSerializer
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from y6u.Shopify.shopify_order import ShopifyOrderBoard

# Load the configuration module
config_file = os.path.join(os.getcwd(), "Configuration.py")
configuration = SourceFileLoader("module.name", config_file).load_module()

# Function to delete None values in the JSON request body
def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d

def getUserAddressDetail(data):
    user = User.objects.get(id=data['user'])
    address = Address.objects.get(id=data['address'])
    payload = {
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email,
        "phone_number":user.phone_number,
        "address":f"{address.flate_name}",
        "zip_code": address.zip_code,
        "city":address.city,
        "postal_code":address.zip_code,
        "admin_area":address.landmark
    }
    return payload


def create_transaction(return_data, amount, status, request_data, user_detail):
    try:
        try:
            user = User.objects.get(email=user_detail['email'])
        except User.DoesNotExist:  
            user = User.objects.create(
                email=user_detail['email'],
                password=make_password(user_detail['email'])
            )

        quantity = int(request_data['quantity'])
        # price = int(request_data['total'])
        price = float(request_data['total'])
        is_subscription = request_data.get('is_subscription', False)
        delivery_charge = float(request_data['delivery_charge'])
        discount_percentage = request_data['discount_percentage']
        transaction = Transaction.objects.get(cyber_transactionid=request_data['authenticationTransactionId'])
        if request_data['delivery_type'] == "standard":
            address_text = f"{user_detail['address']} {user_detail['zip_code']} United Kingdom"
        else:
            address_text = "Tidal Vape Chandler's Ford, 8-9 Fryern Arcade, Winchester Road, Chandler's Ford, Eastleigh, SO53 2DP"


        order_data = find_total_calculation(request_data)
        orderObj = Order.objects.create(
            order_id=generate_unique_order_id(),
            user=user,
            transaction=transaction,
            delivery_charge=order_data.get('delivery_charge'),
            total_price=order_data.get('grand_total'),
            sub_total_price=order_data.get('total_amt'),
            discount_amount=order_data.get('discount_amount'),
            # status=return_data.status,
            status='SUCCESS',
            address=address_text,
            payload=str(request_data),
            is_subscribed=is_subscription
        )

        if is_subscription:
            if 'subscibe_id' in request_data:
                subscibe_data = Subscription.objects.get(id=request_data['subscibe_id'])
                subscibe_data.quantity = quantity
                subscibe_data.total_price = amount
                subscibe_data.order = orderObj
                subscibe_data.save()
            # else:
            if "cart_product" in request_data:
                for item in order_data.get('order_item'):
                    if 'subscibe_id' not in request_data:
                        
                        Subscription.objects.create(
                            product=item.get('product'),
                            product_meta=item.get("product_meta"),
                            days=request_data.get('subscription_days'),
                            user=user,
                            delivery_charge=order_data.get('delivery_charge'),
                            quantity=item.get('quantity'),
                            total_price=order_data.get('grand_total'),
                            address=address_text,
                            order=orderObj,
                            sub_total=order_data.get('total_amt'),
                            price=item.get('price'),
                            discount_percentage=item.get('discount_percentage'),
                            catgeory_key=item.get('catgeory_key'),
                            category_value=item.get('category_value')
                        )
                    
                    OrderItems.objects.create(
                        product=item.get('product'),
                        order=orderObj,
                        quantity=item['quantity'],
                        price=item.get('price'),
                        total_price=item.get('sub_total'),
                        # is_subscribed=is_subscription,
                        catgeory_key=item.get('catgeory_key'),
                        category_value=item.get('category_value'),
                        product_meta=item.get("product_meta"),
                        apply_deal=item.get('deal')
                    )
            else:
                print('nooooooooooooooooooo')
        else:
            if "promo_code" in request_data:
                reedem_code = ReedemCode.objects.get(id=request_data['promo_code'])
                if reedem_code:
                    UserReedem.objects.create(
                        user=user,
                        reedem_code=reedem_code
                    )
                
            if "cart_product" in request_data:
                try:
                    for item in order_data.get('order_item'):
                        print(item, '-----------------------item in it')
                        OrderItems.objects.create(
                            product=item.get('product'),
                            order=orderObj,
                            quantity=item['quantity'],
                            price=item.get('price'),
                            total_price=item.get('sub_total'),
                            # is_subscribed=is_subscription,
                            catgeory_key=item.get('catgeory_key'),
                            category_value=item.get('category_value'),
                            product_meta=item.get("product_meta"),
                            apply_deal=item.get('deal')
                        )
                except Exception as e:
                    print(e, '---------------')
                    
        # CartItem.objects.filter(user__id=request_data['user']).delete()

        email_forward(request_data, user_detail, orderObj, address_text)
        
        # Shopify data are comming
        try:
            data=UserOrderSerializer(orderObj).data
            shopifyOrder = ShopifyOrderBoard()
            shopifyOrder.CreateOrder(data)
        except Exception as e:
            print(e, '----------------------------error in shopify data')
            
            
            
        response = {
            "msg": "The payment process is completed successfully.",
            "order_detail": UserOrderSerializer(orderObj).data,
            "status": 201
        }
        return response
    except Exception as e:
        return {"msg":e, "status":422}

def email_forward(request_data, user_detail, orderObj, address_text):
    try:
        context_data={}
        order_items = OrderItems.objects.filter(order__id=orderObj.id).select_related('product')
        serialized_order_items = OrderItemSerializer(order_items, many=True)
        all_order = []
        
        date_str = orderObj.created_at
        new_date = date_str + timedelta(days=2)
        delivery_date = new_date.strftime("%b %d %Y")
        
        for item_data in serialized_order_items.data:
            product = item_data['product']
            meta_data = product.get('meta_data', [])
            image_url = meta_data[0].get('image', None) if meta_data else None

            payload = {
                "product_image": item_data['product_meta']['image'],
                "product_name": product['name'],
                "quantity": item_data['quantity'],
                "total_price": item_data['total_price'],
                "price": item_data['price'],
                "varient_label": item_data['catgeory_key'],
                "varient_category": item_data.get('category_value', "")
            }
            all_order.append(payload)

        context_data = {
            "first_name":user_detail['first_name'],
            "to_email":user_detail['email'],
            "order_date":orderObj.created_at,
            "delivery_at":delivery_date,
            "order_id":orderObj.order_id,
            "ordered":all_order,
            "price":request_data['total'],
            "total_price":round(orderObj.total_price, 2),
            "quantity":request_data['quantity'],
            "discount":request_data['discount_percentage'],
            "address":address_text,
            "zip_code":user_detail['zip_code'],
            "city":user_detail['city'],
            "admin_area":user_detail['admin_area'],
            "delivery_charge":request_data['delivery_charge'],
            "card_number":request_data['card_number'][-4:],
            "delivery_type": request_data['delivery_type']
        }
        
        if request_data['is_subscription'] == False:
            template_path= 'regular_email.html'
        else:
            for i in request_data['subscription_days']:
                date_str = orderObj.created_at
                next_billing = date_str + timedelta(days=int(i))
            context_data['next_billing'] = next_billing.strftime("%d-%m-%Y")
            context_data['start_date'] = orderObj.created_at.strftime("%d-%m-%Y")
            context_data['subscription_days'] = request_data['subscription_days']
            template_path= 'subscription_email.html'
            
        template = get_template(template_path)
        html_content = template.render(context_data)
        send_mail(
            'Order Successfully',
            "Order Purchased",
            settings.EMAIL_HOST_USER,
            [user_detail['email']],
            fail_silently=False,
            html_message=html_content
        )
    except Exception as e:
        print(e, '---------------nfkndk')
    

def capture_payment(authorization_id, amount, currency, request_data, user_detail):
    try:
        # Client Reference Information
        clientReferenceInformationCode = "TC50171_4"
        clientReferenceInformation = Ptsv2paymentsClientReferenceInformation(
            code=clientReferenceInformationCode
        )
        
        # Processing Information
        processingInformationCapture = True
        processingInformation = Ptsv2paymentsProcessingInformation(
            capture=processingInformationCapture
        )
        
        # Order Information Amount Details
        orderInformationAmountDetails = Ptsv2paymentsOrderInformationAmountDetails(
            total_amount=amount,
            currency=currency
        )
        
        # Order Information
        orderInformation = Ptsv2paymentsOrderInformation(
            amount_details=orderInformationAmountDetails.__dict__
        )
        
        # Construct Capture Request as a Dictionary
        capture_request = {
            "clientReferenceInformation": clientReferenceInformation.__dict__,
            "processingInformation": processingInformation.__dict__,
            "orderInformation": orderInformation.__dict__
        }
        
        # Remove any None values from the request
        capture_request = del_none(capture_request)
        
        # Convert the request to JSON format
        capture_request_json = json.dumps(capture_request)
        
        # Setup Configuration
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        
        # Initialize Capture API instance
        api_instance = CaptureApi(client_config)
        authorization_id_str = str(authorization_id)
        response_data, status_code, response_body = api_instance.capture_payment(capture_request_json, authorization_id_str)
        
        print(response_data, '------------------------response_data')
    
        return create_transaction(response_data, amount, status_code, request_data, user_detail)
    
    except ApiException as e:
        print(f"\nException when calling CaptureApi->capture_payment 123: {e}\n")


# Function to create a simple authorization request
def simple_authorizationinternetWeb(flag, request_data):
    quantity = int(request_data['quantity'])
    price = float(request_data['total'])
    is_subscription = request_data.get('is_subscription', False)
    total_price = price
    
    # Calculate total price with discount and delivery charge
    # total_price = (price * quantity) - ((price * quantity) * int(request_data['discount_percentage'])/100)
    # total_price += request_data['delivery_charge']
    
    # Get user address details
    user_detail = webUserAddressDetail(request_data)

    # Client Reference Information
    clientReferenceInformationCode = "TC50171_3"
    clientReferenceInformation = Ptsv2paymentsClientReferenceInformation(
        code=clientReferenceInformationCode
    )

    # Processing Information (flag controls capture behavior)
    processingInformationCapture = flag
    processingInformationActionList = ["VALIDATE_CONSUMER_AUTHENTICATION"]  # Ensures 3DS validation
    processingInformation = Ptsv2paymentsProcessingInformation(
        capture=processingInformationCapture,
        action_list=processingInformationActionList
    )

    # Payment Information (Card details)
    paymentInformationCardNumber = request_data['card_number']
    paymentInformationCardExpirationMonth = request_data['month']
    paymentInformationCardExpirationYear = request_data['year']
    paymentInformationCardCVV = request_data['cvv']
    paymentInformationCard = Ptsv2paymentsPaymentInformationCard(
        number=paymentInformationCardNumber,
        expiration_month=paymentInformationCardExpirationMonth,
        expiration_year=paymentInformationCardExpirationYear,
        security_code=paymentInformationCardCVV
    )
    paymentInformation = Ptsv2paymentsPaymentInformation(
        card=paymentInformationCard.__dict__
    )

    # Order Information (Billing and Amount Details)
    orderInformationAmountDetails = Ptsv2paymentsOrderInformationAmountDetails(
        total_amount=total_price,
        currency="GBP"
    )
    orderInformationBillTo = Ptsv2paymentsOrderInformationBillTo(
        # first_name=user_detail.get('first_name', 'guest'),
        # last_name=user_detail.get('last_name', 'user'),
        first_name = user_detail.get('first_name') or 'guest',
        last_name = user_detail.get('last_name') or 'user',
        address1=user_detail['address'],
        locality=user_detail['city'],
        administrative_area="CA",
        postal_code=user_detail['postal_code'],
        country="UK",
        email=user_detail['email'],
        phone_number=user_detail['phone_number']
    )
    orderInformation = Ptsv2paymentsOrderInformation(
        amount_details=orderInformationAmountDetails.__dict__,
        bill_to=orderInformationBillTo.__dict__
    )

    # Consumer Authentication Information (3DS transaction ID, if available)
    consumerAuthenticationInformation = Ptsv2paymentsConsumerAuthenticationInformation(
        authentication_transaction_id=request_data.get("authenticationTransactionId")
    )

    # Create payment request object
    requestObj = CreatePaymentRequest(
        client_reference_information=clientReferenceInformation.__dict__,
        processing_information=processingInformation.__dict__,
        payment_information=paymentInformation.__dict__,
        order_information=orderInformation.__dict__,
        consumer_authentication_information=consumerAuthenticationInformation.__dict__
    )

    # Remove None values from the request object and convert to JSON
    requestObj = del_none(requestObj.__dict__)
    requestObj = json.dumps(requestObj)

    try:
        # Get client configuration and initialize Payments API instance
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        api_instance = PaymentsApi(client_config)

        # Send the payment request
        try:
            print('erro1')
            return_data, status, body = api_instance.create_payment(requestObj)

            if return_data.status == "AUTHORIZED":
                print("Payment Authorized")
                response_data = capture_payment(return_data.id, total_price, "GBP", request_data, user_detail)
                print(response_data, '---------------ress')
                return response_data
            elif "consumerAuthenticationInformation" in body:
                print("3DS Authentication Required:", body["consumerAuthenticationInformation"])
                return {
                    "msg": "3DS authentication required",
                    "status": 302, 
                    "authentication_url": body["consumerAuthenticationInformation"].get("authentication_url")
                }
            else:
                return {"msg": "Payment process incomplete", "status": 422}
        except Exception as e:
            print(e, '-----------------error')
            return {"msg": e, "status": 422}
        

    except Exception as e:
        print(f"\nException when calling PaymentsApi->create_payment: {e}\n")
        return {"msg": "Payment process incomplete", "status": 422}


    

