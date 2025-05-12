from dandy.intel import BaseIntel


class EmailIntel(BaseIntel):
    to_email_address: str
    from_email_address: str
    subject: str
    body: str
