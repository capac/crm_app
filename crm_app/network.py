from O365 import Account, FileSystemTokenBackend, MSGraphProtocol
from os import environ
from re import compile
from pprint import pprint

# account credentials saved as system variables
client_id = environ['CLIENT_ID']
client_secret = environ['CLIENT_SECRET']
account_email = environ['EMAIL']
credentials = (client_id, client_secret)


class RetrieveSentDocuments():
    '''Class for the retrieval of documents sent by email to tenants'''

    def __init__(self, credentials):
        self.credentials = credentials
        self.emails = []

        # authenticated token and protocol
        protocol = MSGraphProtocol(api_version='beta')
        token_backend = FileSystemTokenBackend(token_path='.',
                                               token_filename='token.txt')

        # create account with credentials, token and protocol
        self.account = Account(self.credentials, token_backend=token_backend,
                               protocol=protocol)

    def get(self, tenant_email=None):
        # refresh token if expired
        if not self.account.is_authenticated:
            self.account.authenticate(scopes=['basic'])

        mailbox = self.account.mailbox(resource=account_email)
        outbox = mailbox.sent_folder()
        sent_messages = outbox.get_messages(download_attachments=True)

        # email pattern
        name_str = r'[a-zA-Z\s]+'
        email_str = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        complete_str = '('+name_str+'|'+email_str+')\\s\\(('+email_str+')\\)'
        pattern = compile(complete_str)

        for message in sent_messages:
            email = {}
            email['Subject'] = message.subject
            email['Recipient'] = pattern.sub(r'\2', str(message.to._recipients[0]))
            email['Date sent'] = str(message.sent)
            if message.has_attachments:
                attachments = [item.name for item in message.attachments]
                email['Attachments'] = attachments
            else:
                email['Attachments'] = None
            self.emails.append(email)


if __name__ == '__main__':
    sent_docs = RetrieveSentDocuments(credentials=credentials)
    sent_docs.get()
    pprint(f'{sent_docs.emails}')
