import random
import string


def generate_otp():
    return "".join(random.choices(string.digits, k=4))


def create_otp(email, otp):
    context_data = {
        "otp": otp,
    }
    # template = get_template('otp_email.html')
    # html_content = template.render(context_data)
    try:
        # send_mail(
        #     'Your OTP Code',
        #     f'Your OTP code is {otp}',
        #     settings.EMAIL_HOST_USER,
        #     [email],
        #     fail_silently=False,
        #     html_message=html_content
        # )
        return True
    except:
        return False
