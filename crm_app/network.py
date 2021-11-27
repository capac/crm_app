from O365 import Account, FileSystemTokenBackend, MSGraphProtocol
import re


class RetrieveSentDocuments():
    '''Class for the retrieval of documents sent by email to tenants'''

    def __init__(self, settings):
        self.settings = settings
        self.emails = []

        # create account with credentials, token and protocol
        self.credentials = (self.settings['client_id'].get(),
                            self.settings['client_secret'].get())

        # authenticated token and protocol
        protocol = MSGraphProtocol(api_version='beta')
        token_backend = FileSystemTokenBackend(token_path='.',
                                               token_filename='o365_token.txt')

        self.account = Account(self.credentials, token_backend=token_backend,
                               protocol=protocol)

        # authentication step for account
        if not self.account.is_authenticated:
            self.account.authenticate(scopes=['basic'])

    def get(self, tenant_email=None):
        '''Retrieve sent emails from Microsoft Outlook/Office365/Exchange server'''

        mailbox = self.account.mailbox(resource=self.settings['account_email'].get())
        outbox = mailbox.sent_folder()
        sent_messages = outbox.get_messages(download_attachments=True)

        # email pattern
        name_str = r'[a-zA-Z\s]+'
        email_str = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        complete_str = '('+name_str+'|'+email_str+')\\s\\(('+email_str+')\\)'
        pattern = re.compile(complete_str)

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
