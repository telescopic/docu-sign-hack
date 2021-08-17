import base64
from os import path

from docusign_esign import EnvelopesApi, RecipientViewRequest, Document, Signer, EnvelopeDefinition, SignHere, Tabs, \
    Recipients, ApiClient
from flask import session, url_for, request
import shutil

from ds.auth import generate_access_token
from flask_app_basic.pdf_gen import PDFUtil

class DSUtil:

    def __init__(self):

        self.signer_client_id = 1000  # Used to indicate that the signer will use embedded
        # signing. Represents the signer"s userId within
        # your application.

        self.authentication_method = "None"  # How is this application authenticating
    
    def create_api_client(self, base_path, access_token):
        """Create api client and construct API headers"""
        api_client = ApiClient()
        api_client.host = base_path
        api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {access_token}")

        return api_client

    def get_args_for_esign(self, signer_name, signer_email, doc_path):
        """Get request and session arguments"""
        # More data validation would be a good idea here
        # Strip anything other than characters listed
        # 1. Parse request arguments
        access_token, base_uri, account_id = generate_access_token()

        base_path = base_uri + "/restapi"

        envelope_args = {
            "signer_email": signer_email,
            "signer_name": signer_name,
            "signer_client_id": self.signer_client_id,
            "ds_return_url": url_for('post_sign', _external=True),
        }
        args = {
            "doc_path": doc_path,
            "account_id": account_id,
            "base_path": base_path,
            "access_token": access_token,
            "envelope_args": envelope_args
        }
        return args
    
    def get_args_for_doc_retrieval(self, doc_id, envelope_id):
        
        access_token, base_uri, account_id = generate_access_token()

        base_path = base_uri + "/restapi"

        args = {
            "base_path": base_path,
            "access_token": access_token,
            "document_id": doc_id,
            "account_id": account_id,
            "envelope_id": envelope_id
        }

        return args

    def worker(self, args):
        """
        1. Create the envelope request object
        2. Send the envelope
        3. Create the Recipient View request object
        4. Obtain the recipient_view_url for the embedded signing
        """
        envelope_args = args["envelope_args"]
        # 1. Create the envelope request object
        envelope_definition = self.make_envelope(envelope_args, args["doc_path"])

        print(args["base_path"])
        # 2. call Envelopes::create API method
        # Exceptions will be caught by the calling function
        api_client = self.create_api_client(base_path=args["base_path"], access_token=args["access_token"])

        envelope_api = EnvelopesApi(api_client)
        results = envelope_api.create_envelope(account_id=args["account_id"], envelope_definition=envelope_definition)

        envelope_id = results.envelope_id

        # 3. Create the Recipient View request object
        recipient_view_request = RecipientViewRequest(
            authentication_method=self.authentication_method,
            client_user_id=envelope_args["signer_client_id"],
            recipient_id="1",
            return_url=envelope_args["ds_return_url"],
            user_name=envelope_args["signer_name"],
            email=envelope_args["signer_email"]
        )
        # 4. Obtain the recipient_view_url for the embedded signing
        # Exceptions will be caught by the calling function
        results = envelope_api.create_recipient_view(
            account_id=args["account_id"],
            envelope_id=envelope_id,
            recipient_view_request=recipient_view_request
        )

        return {"envelope_id": envelope_id, "redirect_url": results.url}

    def make_envelope(self, args, doc_path):
        """
        Creates envelope
        args -- parameters for the envelope:
        signer_email, signer_name, signer_client_id
        returns an envelope definition
        """

        # document 1 (pdf) has tag /sn1/
        #
        # The envelope has one recipient.
        # recipient 1 - signer
        with open(doc_path, "rb") as file:
            content_bytes = file.read()
        
        base64_file_content = base64.b64encode(content_bytes).decode("ascii")

        # Create the document model
        document = Document(  # create the DocuSign document object
            document_base64=base64_file_content,
            name="Example document",  # can be different from actual file name
            file_extension="pdf",  # many different document types are accepted
            document_id=1  # a label used to reference the doc
        )

        # Create the signer recipient model
        signer = Signer(
            # The signer
            email=args["signer_email"],
            name=args["signer_name"],
            recipient_id="1",
            routing_order="1",
            # Setting the client_user_id marks the signer as embedded
            client_user_id=args["signer_client_id"]
        )

        # Create a sign_here tab (field on the document)
        sign_here = SignHere(
            # DocuSign SignHere field/tab
            anchor_string="sign",
            anchor_units="pixels",
            anchor_y_offset="5",
            anchor_x_offset="40"
        )

        # Add the tabs model (including the sign_here tab) to the signer
        # The Tabs object wants arrays of the different field/tab types
        signer.tabs = Tabs(sign_here_tabs=[sign_here])

        # Next, create the top level envelope definition and populate it.
        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this document sent from the Python SDK",
            documents=[document],
            # The Recipients object wants arrays for each recipient type
            recipients=Recipients(signers=[signer]),
            status="sent"  # requests that the envelope be created and sent.
        )

        return envelope_definition
    
    def envelope_doc_to_img(self, args, dest_path):
        pdf_util = PDFUtil()
        api_client = self.create_api_client(base_path=args["base_path"], access_token=args["access_token"])

        envelope_api = EnvelopesApi(api_client)
        document_id = args["document_id"]

        # The SDK always stores the received file as a temp file
        # Call the envelope get method
        temp_file = envelope_api.get_document(
            account_id=args["account_id"],
            document_id=document_id,
            envelope_id=args["envelope_id"]
        )

        # dest_path = "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/certificates/cert.jpg"

        pdf_util.convert_pdf_to_image(temp_file, dest_path)
        
