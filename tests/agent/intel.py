from dandy.intel.intel import BaseIntel


class EmailIntel(BaseIntel):
    to_email_address: str
    from_email_address: str
    subject: str
    body: str


class EmailAddressIntel(BaseIntel):
    email_address: str


class EmailBodyIntel(BaseIntel):
    body: str