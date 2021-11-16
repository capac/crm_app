from O365 import Account, FileSystemTokenBackend, MSGraphProtocol
from os import environ

# account credentials saved as system variables
CLIENT_ID = environ['CLIENT_ID']
CLIENT_SECRET = environ['CLIENT_SECRET']
credentials = (CLIENT_ID, CLIENT_SECRET)


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

    def get(self, email):
        # refresh token if expired
        if not self.account.is_authenticated:
            self.account.authenticate(scopes=['basic'])

        mailbox = self.account.mailbox(resource=email)
        outbox = mailbox.sent_folder()
        sent_messages = outbox.get_messages(download_attachments=True)

        for message in sent_messages:
            email = {}
            email['Subject'] = message.subject
            email['Date sent'] = str(message.sent)
            if message.has_attachments:
                attachments = [item.name for item in message.attachments]
                email['Attachments'] = attachments
            else:
                email['Attachments'] = None
            self.emails.append(email)
