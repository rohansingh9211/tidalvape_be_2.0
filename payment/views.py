from common.exception import StandardAPIException
from payment.payment import create_transaction

# from payment.payment_operators.cybersource.cybersourceweb3ds import CspEnrollWebPendingAuthOperator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class CspEnrollWebPendingAuthenticationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # _csp_enroll = CspEnrollWebPendingAuthOperator(request)
        try:
            # return _csp_enroll.enroll_web_pending_auth()
            return create_transaction(request.data)
        except Exception as err:
            raise StandardAPIException(
                code='payment_issue',
                detail=err,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
