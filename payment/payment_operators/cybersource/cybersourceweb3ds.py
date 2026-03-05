from common.exception import StandardAPIException
from common.response import StandardAPIResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from CyberSource import *
from pathlib import Path
import os
import json
from importlib.machinery import SourceFileLoader
from django.http import JsonResponse
from y6u.utils import webUserAddressDetail
from y6u.models import (Transaction, User)
import uuid

config_file = os.path.join(os.getcwd(), "Configuration.py")
configuration = SourceFileLoader("module.name", config_file).load_module()

def write_log_audit(status):
    print(f"[Sample Code Testing] [{Path(__file__).stem}] {status}")
    
# To delete None values in Input Request Json body
def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d

def response_to_dict(obj):
    """
    Convert a CyberSource response object to a dictionary by accessing its __dict__
    and handling any nested attributes.
    """
    if isinstance(obj, list):
        return [response_to_dict(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return {key: response_to_dict(value) for key, value in obj.__dict__.items()}
    else:
        return obj
        
    
# class EnrollWithPendingAuthentication(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Data from request body
#             data = request.data
#             userdetail = getUserAddressDetail(data)
#             reference_id = uuid.uuid4().hex

#             clientReferenceInformationCode = data.get('client_reference_information_code', reference_id)
#             clientReferenceInformation = Riskv1authenticationsetupsClientReferenceInformation(
#                 code=clientReferenceInformationCode
#             )

#             orderInformationAmountDetailsObj = Riskv1authenticationsOrderInformationAmountDetails(
#                 currency="GBP",
#                 total_amount=data['total']
#             )

#             orderInformationBillToObj = Riskv1authenticationsOrderInformationBillTo(
#                 address1= userdetail.get('address', "abc"),
#                 address2=userdetail.get('address', "abc"),
#                 administrative_area=userdetail.get('admin_area', "xyz"),
#                 country="UK",
#                 locality=userdetail.get('admin_area', "xyz"),
#                 first_name=userdetail.get('first_name', "name"),
#                 last_name= userdetail.get('last_name', "name"),
#                 phone_number= userdetail.get('phone_number', "phone_number"),
#                 email=userdetail.get('email', "email"),
#                 postal_code=userdetail.get('postal_code', "postal_code")
#             )

#             orderInformation = Riskv1authenticationsOrderInformation(
#                 amount_details=orderInformationAmountDetailsObj.__dict__,
#                 bill_to=orderInformationBillToObj.__dict__
#             )

#             paymentInformationCardObj = Riskv1authenticationsetupsPaymentInformationCard(
#                 type="001",
#                 expiration_month=data.get('month'),
#                 expiration_year=data.get('year'),
#                 number=data.get('card_number')
#             )

#             paymentInformation = Riskv1authenticationsPaymentInformation(
#                 card=paymentInformationCardObj.__dict__
#             )

#             buyerInformationMobilePhone = userdetail['phone_number']
#             buyerInformation = Riskv1authenticationsBuyerInformation(
#                 mobile_phone=buyerInformationMobilePhone
#             )

#             deviceInformationObj = Riskv1authenticationsDeviceInformation(
#                 ip_address=data.get('ipAddress'),
#                 http_accept_content="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                 http_browser_language="en-US", 
#                 http_browser_java_enabled=False,
#                 http_browser_color_depth="24",
#                 http_browser_screen_height="1080",  
#                 http_browser_screen_width="1920",  
#                 http_browser_time_difference="-300",
#                 user_agent_browser_value= "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
#             )


#             consumerAuthenticationInformationObj = Riskv1decisionsConsumerAuthenticationInformation(
#                 device_channel="BROWSER",
#                 return_url=f"https://locatidalvape.shop/api/validate-auth/?user={data['user']}",
#                 transaction_mode="eCommerce"
#             )

#             requestObj = CheckPayerAuthEnrollmentRequest(
#                 client_reference_information=clientReferenceInformation.__dict__,
#                 order_information=orderInformation.__dict__,
#                 payment_information=paymentInformation.__dict__,
#                 buyer_information=buyerInformation.__dict__,
#                 device_information=deviceInformationObj.__dict__,
#                 consumer_authentication_information=consumerAuthenticationInformationObj.__dict__
#             )

#             requestObj = del_none(requestObj.__dict__)
#             requestObj = json.dumps(requestObj)

#             # Send request to CyberSource API
#             config_obj = configuration.Configuration()
#             client_config = config_obj.get_configuration()
#             api_instance = PayerAuthenticationApi(client_config)
#             return_data, api_status, api_body = api_instance.check_payer_auth_enrollment(requestObj)

        
#             print(type(return_data), '-------------return_data')
#             print(api_status, '-------------api_status')
#             print(api_body, '-------------api_body')


#             json_body = json.loads(api_body)

#             print(json_body, '-json_body-')
#             # Log and return the API response
#             write_log_audit(api_status)
#             if 'status' in json_body:
#                 if json_body['status'] == "PENDING_AUTHENTICATION":
#                     transaction = Transaction.objects.create(
#                         user=User.objects.get(id=data['user']),
#                         quantity=data['quantity'],
#                         total_price=data['total'],
#                         price=float(data['total']),
#                         discount_percentage=data['discount_percentage'],
#                         cyber_status = json_body.get('status'),
#                         cyber_transactionid = json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         transaction_id = reference_id
#                     )
#                     return Response({
#                         "status": api_status,
#                         # "body": json_body,
#                         "access_token": json_body['consumerAuthenticationInformation']['accessToken'],
#                         "transaction_id": json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         "callback_url": json_body['consumerAuthenticationInformation']['stepUpUrl'],
#                         "cyber_status": json_body['status'],
#                         "message": json_body['errorInformation']['message']
#                     }, status=status.HTTP_200_OK)
#             else:
#                 return Response({
#                     "message": json_body['errorInformation']['message']
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             write_log_audit(e.status if hasattr(e, 'status') else 999)
#             return Response({
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# start Website Payment Authentication
# class EnrollWebWithPendingAuthentication(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Data from request body
#             data = request.data
#             userdetail = webUserAddressDetail(data)
#             reference_id = uuid.uuid4().hex

#             try:
#                 user, created = User.objects.get_or_create(
#                     email=userdetail['email'],
#                     defaults={
#                         'username': userdetail['email'],  
#                         'password':  userdetail['email'] 
#                     }
#                 )
#                 if created:
#                     print("User was created:", user)
#                 else:
#                     print("User already exists:", user)
#             except Exception as e:
#                 print("An error occurred:", e)

#             clientReferenceInformationCode = data.get('client_reference_information_code', reference_id)
#             clientReferenceInformation = Riskv1authenticationsetupsClientReferenceInformation(
#                 code=clientReferenceInformationCode
#             )

#             orderInformationAmountDetailsObj = Riskv1authenticationsOrderInformationAmountDetails(
#                 currency="GBP",
#                 total_amount=data['total']
#             )

#             orderInformationBillToObj = Riskv1authenticationsOrderInformationBillTo(
#                 address1= userdetail.get('address', "abc"),
#                 address2=userdetail.get('address', "abc"),
#                 administrative_area=userdetail.get('admin_area', "xyz"),
#                 country="UK",
#                 locality=userdetail.get('admin_area', "xyz"),
#                 first_name=userdetail.get('first_name', "name"),
#                 last_name= userdetail.get('last_name', "name"),
#                 phone_number= userdetail.get('phone_number', "phone_number"),
#                 email=userdetail.get('email', "email"),
#                 postal_code=userdetail.get('postal_code', "postal_code")
#             )

#             orderInformation = Riskv1authenticationsOrderInformation(
#                 amount_details=orderInformationAmountDetailsObj.__dict__,
#                 bill_to=orderInformationBillToObj.__dict__
#             )

#             paymentInformationCardObj = Riskv1authenticationsetupsPaymentInformationCard(
#                 type="001",
#                 expiration_month=data.get('month'),
#                 expiration_year=data.get('year'),
#                 number=data.get('card_number')
#             )

#             paymentInformation = Riskv1authenticationsPaymentInformation(
#                 card=paymentInformationCardObj.__dict__
#             )

#             buyerInformationMobilePhone = userdetail['phone_number']
#             buyerInformation = Riskv1authenticationsBuyerInformation(
#                 mobile_phone=buyerInformationMobilePhone
#             )

#             deviceInformationObj = Riskv1authenticationsDeviceInformation(
#                 ip_address=data.get('ipAddress'),
#                 http_accept_content="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                 http_browser_language="en-US", 
#                 http_browser_java_enabled=False,
#                 http_browser_color_depth="24",
#                 http_browser_screen_height="1080",  
#                 http_browser_screen_width="1920",  
#                 http_browser_time_difference="-300",
#                 user_agent_browser_value= "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
#             )


#             consumerAuthenticationInformationObj = Riskv1decisionsConsumerAuthenticationInformation(
#                 device_channel="BROWSER",
#                 return_url=f"https://locatidalvape.shop/api/validate-web-auth/?user={user.id}",
#                 transaction_mode="eCommerce"
#             )

#             requestObj = CheckPayerAuthEnrollmentRequest(
#                 client_reference_information=clientReferenceInformation.__dict__,
#                 order_information=orderInformation.__dict__,
#                 payment_information=paymentInformation.__dict__,
#                 buyer_information=buyerInformation.__dict__,
#                 device_information=deviceInformationObj.__dict__,
#                 consumer_authentication_information=consumerAuthenticationInformationObj.__dict__
#             )

#             requestObj = del_none(requestObj.__dict__)
#             requestObj = json.dumps(requestObj)

#             # Send request to CyberSource API
#             config_obj = configuration.Configuration()
#             client_config = config_obj.get_configuration()
#             api_instance = PayerAuthenticationApi(client_config)
#             return_data, api_status, api_body = api_instance.check_payer_auth_enrollment(requestObj)

        
#             print(type(return_data), '-------------return_data')
#             print(api_status, '-------------api_status')
#             print(api_body, '-------------api_body')


#             json_body = json.loads(api_body)

#             print(json_body, '-json_body-')
#             # Log and return the API response
#             write_log_audit(api_status)
#             if 'status' in json_body:
#                 if json_body['status'] == "PENDING_AUTHENTICATION":
#                     transaction = Transaction.objects.create(
#                         user=User.objects.get(id=user.id),
#                         quantity=data['quantity'],
#                         total_price=data['total'],
#                         price=float(data['total']),
#                         discount_percentage=data['discount_percentage'],
#                         cyber_status = json_body.get('status'),
#                         cyber_transactionid = json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         transaction_id = reference_id
#                     )
#                     return Response({
#                         "status": api_status,
#                         # "body": json_body,
#                         "user":user.id,
#                         "access_token": json_body['consumerAuthenticationInformation']['accessToken'],
#                         "transaction_id": json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         "callback_url": json_body['consumerAuthenticationInformation']['stepUpUrl'],
#                         "cyber_status": json_body['status'],
#                         "message": json_body['errorInformation']['message']
#                     }, status=status.HTTP_200_OK)
#             else:
#                 return Response({
#                     "message": json_body['errorInformation']['message']
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             write_log_audit(e.status if hasattr(e, 'status') else 999)
#             return Response({
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # End Website Payment Authentication


# # To delete None values in Input Request Json body
# def del_none(d):
#     for key, value in list(d.items()):
#         if value is None:
#             del d[key]
#         elif isinstance(value, dict):
#             del_none(value)
#         elif isinstance(value, list):
#             for item in value:
#                 del_none(item)
#     return d


# class ValidateWebAuthenticationResults(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             user = request.GET.get('user')
#             transaction_date = request.POST
#             clientReferenceInformationCode = "pavalidatecheck"
#             clientReferenceInformationPartnerDeveloperId = "7891234"
#             clientReferenceInformationPartnerSolutionId = "89012345"
#             clientReferenceInformationPartner = Riskv1decisionsClientReferenceInformationPartner(
#                 developer_id=clientReferenceInformationPartnerDeveloperId,
#                 solution_id=clientReferenceInformationPartnerSolutionId
#             )

#             clientReferenceInformation = Riskv1authenticationsetupsClientReferenceInformation(
#                 code=clientReferenceInformationCode,
#                 partner=clientReferenceInformationPartner.__dict__
#             )


#             consumerAuthenticationInformationAuthenticationTransactionId = transaction_date['TransactionId']
#             consumerAuthenticationInformation = Riskv1authenticationresultsConsumerAuthenticationInformation(
#                 authentication_transaction_id=consumerAuthenticationInformationAuthenticationTransactionId
#             )

#             requestObj = ValidateRequest(
#                 client_reference_information=clientReferenceInformation.__dict__,
#                 # order_information=orderInformation.__dict__,
#                 consumer_authentication_information=consumerAuthenticationInformation.__dict__
#             )

#             requestObj = del_none(requestObj.__dict__)
#             requestObj = json.dumps(requestObj)

#             # Call the CyberSource API
#             config_obj = configuration.Configuration()
#             client_config = config_obj.get_configuration()
#             api_instance = PayerAuthenticationApi(client_config)
#             return_data, status, body = api_instance.validate_authentication_results(requestObj)
#             json_return_res = json.loads(body)
#             # user_data = User.objects.get(id=user)
#             print(transaction_date['TransactionId'])
#             # Fetch the transaction based on the user ID and the cyber transaction ID
#             transaction = Transaction.objects.get(user__id=user, cyber_transactionid=transaction_date['TransactionId'])
#             transaction.cyber_status = json_return_res['status']
#             transaction.save()

#             html_content = """
#                                 <html>
#                                     <head><title>Web Content</title></head>
#                                     <body>
#                                         <h1>This is a sample HTML content</h1>
#                                         <p>This is some web content returned by the API.</p>
#                                     </body>
#                                 </html>
#                             """
#             return Response(html_content, content_type='text/html')
        
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     def get(self, request, *args, **kwargs):
#         html_content = """
#                 <html>
#                     <head>
#                         <title>Payment Process</title>
#                     </head>
#                     <body>
#                         <h1>Payment in Process</h1>
#                         # <p>Your payment is being processed. Please wait a moment.</p>
#                         # <div>
#                         #     <p>Thank you for your patience.</p>
#                         #     <p>If the payment is not completed within a few minutes, please check your payment details or contact support.</p>
#                         # </div>
#                     </body>
#                 </html>

#             """
#         return Response(html_content, content_type='text/html')
        

        
        
        
# class CspEnrollWebPendingAuthOperator:
#     def __init__(self, request):
#         self.request = request
    
#     @staticmethod
#     def write_log_audit(status):
#         print(f"[Sample Code Testing] [{Path(__file__).stem}] {status}")
    
#     @staticmethod
#     def del_none(d):
#         for key, value in list(d.items()):
#             if value is None:
#                 del d[key]
#             elif isinstance(value, dict):
#                 del_none(value)
#         return d
    
#     def enroll_web_pending_auth(self):
#         try:
#             # Data from request body
#             data = self.request.data
#             userdetail = webUserAddressDetail(data)
#             reference_id = uuid.uuid4().hex

#             try:
#                 user, created = User.objects.get_or_create(
#                     email=userdetail['email'],
#                     defaults={
#                         'username': userdetail['email'],  
#                         'password':  userdetail['email'] 
#                     }
#                 )
#                 if created:
#                     print("User was created:", user)
#                 else:
#                     print("User already exists:", user)
#             except Exception as e:
#                 print("An error occurred:", e)

#             print("hello how are you122")
#             clientReferenceInformationCode = data.get('client_reference_information_code', reference_id)
#             # clientReferenceInformation = Riskv1authenticationsetupsClientReferenceInformation(
#             #     code=clientReferenceInformationCode
#             # )
#             print("hello how are you")
            

#             orderInformationAmountDetailsObj = Riskv1authenticationsOrderInformationAmountDetails(
#                 currency="GBP",
#                 total_amount=data['total']
#             )

#             orderInformationBillToObj = Riskv1authenticationsOrderInformationBillTo(
#                 address1= userdetail.get('address', "abc"),
#                 address2=userdetail.get('address', "abc"),
#                 administrative_area=userdetail.get('admin_area', "xyz"),
#                 country="UK",
#                 locality=userdetail.get('admin_area', "xyz"),
#                 first_name=userdetail.get('first_name', "name"),
#                 last_name= userdetail.get('last_name', "name"),
#                 phone_number= userdetail.get('phone_number', "phone_number"),
#                 email=userdetail.get('email', "email"),
#                 postal_code=userdetail.get('postal_code', "postal_code")
#             )

#             orderInformation = Riskv1authenticationsOrderInformation(
#                 amount_details=orderInformationAmountDetailsObj.__dict__,
#                 bill_to=orderInformationBillToObj.__dict__
#             )

#             paymentInformationCardObj = Riskv1authenticationsetupsPaymentInformationCard(
#                 type="001",
#                 expiration_month=data.get('month'),
#                 expiration_year=data.get('year'),
#                 number=data.get('card_number')
#             )

#             paymentInformation = Riskv1authenticationsPaymentInformation(
#                 card=paymentInformationCardObj.__dict__
#             )

#             buyerInformationMobilePhone = userdetail['phone_number']
#             buyerInformation = Riskv1authenticationsBuyerInformation(
#                 mobile_phone=buyerInformationMobilePhone
#             )

#             deviceInformationObj = Riskv1authenticationsDeviceInformation(
#                 ip_address=data.get('ipAddress'),
#                 http_accept_content="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                 http_browser_language="en-US", 
#                 http_browser_java_enabled=False,
#                 http_browser_color_depth="24",
#                 http_browser_screen_height="1080",  
#                 http_browser_screen_width="1920",  
#                 http_browser_time_difference="-300",
#                 user_agent_browser_value= "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
#             )


#             consumerAuthenticationInformationObj = Riskv1decisionsConsumerAuthenticationInformation(
#                 device_channel="BROWSER",
#                 return_url=f"https://app.tidalvape.co.uk/api/validate-web-auth/?user={user.id}",
#                 transaction_mode="eCommerce"
#             )

#             requestObj = CheckPayerAuthEnrollmentRequest(
#                 # client_reference_information=clientReferenceInformation.__dict__,
#                 order_information=orderInformation.__dict__,
#                 payment_information=paymentInformation.__dict__,
#                 buyer_information=buyerInformation.__dict__,
#                 device_information=deviceInformationObj.__dict__,
#                 consumer_authentication_information=consumerAuthenticationInformationObj.__dict__
#             )

#             requestObj = del_none(requestObj.__dict__)
#             requestObj = json.dumps(requestObj)

#             # Send request to CyberSource API
#             config_obj = configuration.Configuration()
#             client_config = config_obj.get_configuration()
#             api_instance = PayerAuthenticationApi(client_config)
#             return_data, api_status, api_body = api_instance.check_payer_auth_enrollment(requestObj)

        
#             print(type(return_data), '-------------return_data')
#             print(api_status, '-------------api_status')
#             print(api_body, '-------------api_body')


#             json_body = json.loads(api_body)

#             print(json_body, '-json_body-')
#             # Log and return the API response
#             write_log_audit(api_status)
            
#             if 'status' in json_body:
#                 if json_body['status'] == "PENDING_AUTHENTICATION":
#                     transaction = Transaction.objects.create(
#                         user=User.objects.get(id=user.id),
#                         quantity=data['quantity'],
#                         total_price=data['total'],
#                         price=float(data['total']),
#                         discount_percentage=data['discount_percentage'],
#                         cyber_status = json_body.get('status'),
#                         cyber_transactionid = json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         transaction_id = reference_id
#                     )
#                     return StandardAPIResponse({
#                         "status": api_status,
#                         # "body": json_body,
#                         "user":user.id,
#                         "access_token": json_body['consumerAuthenticationInformation']['accessToken'],
#                         "transaction_id": json_body['consumerAuthenticationInformation']['authenticationTransactionId'],
#                         "callback_url": json_body['consumerAuthenticationInformation']['stepUpUrl'],
#                         "cyber_status": json_body['status'],
#                         "message": json_body['errorInformation']['message']
#                     }, status=status.HTTP_200_OK)
#             else:
#                 return StandardAPIResponse({
#                     "message": json_body['errorInformation']['message']
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             write_log_audit(e.status if hasattr(e, 'status') else 999)
#             return StandardAPIException(
#                 code='error',
#                 detail=str(e), 
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

import uuid
import json
import logging
from pathlib import Path

from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from rest_framework import status

from cybersource_rest_client import (
    Riskv1authenticationsOrderInformationAmountDetails,
    Riskv1authenticationsOrderInformationBillTo,
    Riskv1authenticationsOrderInformation,
    Riskv1authenticationsetupsPaymentInformationCard,
    Riskv1authenticationsPaymentInformation,
    Riskv1authenticationsBuyerInformation,
    Riskv1authenticationsDeviceInformation,
    Riskv1decisionsConsumerAuthenticationInformation,
    CheckPayerAuthEnrollmentRequest,
    PayerAuthenticationApi,
)

logger = logging.getLogger(__name__)
config_file = os.path.join(os.getcwd(), "Configuration.py")
configuration = SourceFileLoader("module.name", config_file).load_module()

class CspEnrollWebPendingAuthOperator:
    def __init__(self, request):
        self.request = request

    @staticmethod
    def write_log_audit(status):
        logger.info(f"[{Path(__file__).stem}] Status: {status}")

    @staticmethod
    def del_none(data):
        """Remove None values recursively from dict"""
        if isinstance(data, dict):
            return {
                key: CspEnrollWebPendingAuthOperator.del_none(value)
                for key, value in data.items()
                if value is not None
            }
        return data

    def enroll_web_pending_auth(self):
        data = self.request.data

        # =========================
        # Validate Required Fields
        # =========================
        required_fields = ['total', 'quantity', 'card_number', 'month', 'year']
        for field in required_fields:
            if not data.get(field):
                raise StandardAPIException(
                    code="validation_error",
                    detail=f"{field} is required",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        userdetail = webUserAddressDetail(data)
        reference_id = uuid.uuid4().hex

        # =========================
        # Create / Get User Safely
        # =========================
        user, created = User.objects.get_or_create(
            email=userdetail['email'],
            defaults={'username': userdetail['email']}
        )

        if created:
            user.set_password(userdetail['email'])
            user.save()

        # =========================
        # Order Information
        # =========================
        amount_details = Riskv1authenticationsOrderInformationAmountDetails(
            currency="GBP",
            total_amount=data['total']
        )

        bill_to = Riskv1authenticationsOrderInformationBillTo(
            address1=userdetail.get('address'),
            address2=userdetail.get('address'),
            administrative_area=userdetail.get('admin_area'),
            country="GB",  # ✅ Correct ISO country
            locality=userdetail.get('admin_area'),
            first_name=userdetail.get('first_name'),
            last_name=userdetail.get('last_name'),
            phone_number=userdetail.get('phone_number'),
            email=userdetail.get('email'),
            postal_code=userdetail.get('postal_code')
        )

        order_information = Riskv1authenticationsOrderInformation(
            amount_details=amount_details.__dict__,
            bill_to=bill_to.__dict__
        )

        # =========================
        # Payment Information
        # =========================
        card = Riskv1authenticationsetupsPaymentInformationCard(
            type="001",
            expiration_month=data.get('month'),
            expiration_year=data.get('year'),
            number=data.get('card_number')
        )

        payment_information = Riskv1authenticationsPaymentInformation(
            card=card.__dict__
        )

        # =========================
        # Buyer Information
        # =========================
        buyer_information = Riskv1authenticationsBuyerInformation(
            mobile_phone=userdetail.get('phone_number')
        )

        # =========================
        # Device Information
        # =========================
        device_information = Riskv1authenticationsDeviceInformation(
            ip_address=data.get('ipAddress'),
            http_accept_content="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            http_browser_language="en-US",
            http_browser_java_enabled=False,
            http_browser_color_depth="24",
            http_browser_screen_height="1080",
            http_browser_screen_width="1920",
            http_browser_time_difference="0",
            user_agent_browser_value=self.request.META.get("HTTP_USER_AGENT")
        )

        # =========================
        # Consumer Authentication
        # =========================
        consumer_auth = Riskv1decisionsConsumerAuthenticationInformation(
            device_channel="BROWSER",
            return_url=f"https://app.tidalvape.co.uk/api/validate-web-auth/?user={user.id}",
            transaction_mode="eCommerce"
        )

        request_object = CheckPayerAuthEnrollmentRequest(
            order_information=order_information.__dict__,
            payment_information=payment_information.__dict__,
            buyer_information=buyer_information.__dict__,
            device_information=device_information.__dict__,
            consumer_authentication_information=consumer_auth.__dict__
        )

        request_dict = self.del_none(request_object.__dict__)
        request_json = json.dumps(request_dict)

        # =========================
        # Call CyberSource API
        # =========================
        config_obj = configuration.Configuration()
        client_config = config_obj.get_configuration()
        api_instance = PayerAuthenticationApi(client_config)

        return_data, api_status, api_body = api_instance.check_payer_auth_enrollment(request_json)

        self.write_log_audit(api_status)

        json_body = json.loads(api_body)

        status_value = json_body.get("status")

        # =========================
        # Handle PENDING_AUTHENTICATION
        # =========================
        if status_value == "PENDING_AUTHENTICATION":
            consumer_info = json_body.get("consumerAuthenticationInformation", {})

            with db_transaction.atomic():
                Transaction.objects.create(
                    user=user,
                    quantity=data['quantity'],
                    total_price=data['total'],
                    price=float(data['total']),
                    discount_percentage=data.get('discount_percentage', 0),
                    cyber_status=status_value,
                    cyber_transactionid=consumer_info.get("authenticationTransactionId"),
                    transaction_id=reference_id
                )

            return StandardAPIResponse({
                "status": api_status,
                "user": user.id,
                "access_token": consumer_info.get("accessToken"),
                "transaction_id": consumer_info.get("authenticationTransactionId"),
                "callback_url": consumer_info.get("stepUpUrl"),
                "cyber_status": status_value
            }, status=status.HTTP_200_OK)

        # =========================
        # Handle Failed Response
        # =========================
        error_info = json_body.get("errorInformation", {})
        raise StandardAPIException(
            code="cybersource_error",
            detail=error_info.get("message", "Authentication failed"),
            status_code=status.HTTP_400_BAD_REQUEST
        )
