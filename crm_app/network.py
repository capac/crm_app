from O365 import Account, FileSystemTokenBackend, MSGraphProtocol
from re import compile


class RetrieveSentDocuments():
    '''Class for the retrieval of documents sent by email to tenants'''

    def __init__(self, settings):
        self.settings = settings
        self.emails = []

        # authenticated token and protocol
        protocol = MSGraphProtocol(api_version='beta')
        token_backend = FileSystemTokenBackend(token_path='.',
                                               token_filename='o365_token.txt')

        # create account with credentials, token and protocol
        credentials = (self.settings['client_id'].get(),
                       self.settings['client_secret'].get())
        self.account = Account(credentials, token_backend=token_backend,
                               protocol=protocol)

    def get(self, tenant_email=None):
        # If it's your first login, you will have to visit a website to authenticate
        # and paste the redirected URL in the console. Then your token will be stored.
        # If you already have a valid token stored, then account.is_authenticated
        # is True.
        if not self.account.is_authenticated:
            self.account.authenticate(scopes=['basic'])

        mailbox = self.account.mailbox(resource=self.settings['account_email'].get())
        outbox = mailbox.sent_folder()
        sent_messages = outbox.get_messages(download_attachments=True)

        # email pattern
        name_str = r'[a-zA-Z\s]+'
        email_str = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        complete_str = '('+name_str+'|'+email_str+')\\s\\(('+email_str+')\\)'
        pattern = compile(complete_str)

        for message in sent_messages:
            for name_and_email in message.to._recipients:
                email = pattern.sub(r'\2', str(name_and_email))
                if tenant_email == email:
                    record = {}
                    record['Subject'] = message.subject
                    record['Recipient'] = email
                    record['Date sent'] = str(message.sent)
                    if message.has_attachments:
                        attachments = [attachment.name for attachment in message.attachments]
                        record['Attachments'] = attachments
                    else:
                        record['Attachments'] = None
                    self.emails.append(record)
