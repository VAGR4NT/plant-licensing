from django.core.mail import send_mail
from django.core.mail import send_mass_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# First, render the plain text content.
text_content = render_to_string(
    "templates/email/test_email_text.txt",
    context={"my_variable": 42},
)

# Then, create a multipart email instance.
msg = EmailMultiAlternatives(
    "Test Email Subject",
    text_content,
    "tho241@uky.edu",
    ["tho241@uky.edu"],
    headers={},
)


msg.attach_file("pdfs/dealer_renewal_fillable.pdf")
msg.send()