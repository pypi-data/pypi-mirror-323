# This file is auto-generated. DO NOT EDIT.
# Run `python scripts/generate_models.py` to regenerate.

from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator, validator
from difflib import get_close_matches
from .exceptions import SkribbleValidationError

class AuthRequest(BaseModel):
    """Authentication request for the API
    
    Attributes:
        username (str): API username
        api_key (str): API key
    """
    username: str = Field(description="API username", ...)
    api_key: str = Field(description="API key", alias="api-key", ...)

class SignerIdentityData(BaseModel):
    """Identity data for no-account signers
    
    Attributes:
        email_address (EmailStr): Email address of no-account-signer
        mobile_number (Optional[str]): Mobile number of no-account-signer
        first_name (Optional[str]): First name of no-account-signer
        last_name (Optional[str]): Last name of no-account-signer
        language (Optional[str]): Language for communication with the signer
    """
    email_address: EmailStr = Field(description="Email address of no-account-signer", ...)
    mobile_number: Optional[str] = Field(description="Mobile number of no-account-signer", max_length=100)
    first_name: Optional[str] = Field(description="First name of no-account-signer", max_length=1024)
    last_name: Optional[str] = Field(description="Last name of no-account-signer", max_length=1024)
    language: Optional[str] = Field(description="Language for communication with the signer")

    @model_validator(mode='before')
    def check_fields(cls, values):
        valid_fields = cls.model_fields.keys()
        for field in values:
            if field not in valid_fields:
                close_matches = get_close_matches(field, valid_fields, n=1, cutoff=0.6)
                if close_matches:
                    raise ValueError(f"Invalid field '{field}'. Did you mean '{close_matches[0]}'?")
                else:
                    raise ValueError(f"Invalid field '{field}'. Valid fields are: {", ".join(valid_fields)}")
        return values

class Image(BaseModel):
    """Image data with content type and content
    
    Attributes:
        content_type (str): 
        content (str): 
    """
    content_type: str = Field(...)
    content: str = Field(...)

class Position(BaseModel):
    """Position details for visual elements
    
    Attributes:
        x (float): 
        y (float): 
        width (float): 
        height (float): 
        page (str): 
        rotation (Optional[float]): 
    """
    x: float = Field(...)
    y: float = Field(...)
    width: float = Field(...)
    height: float = Field(...)
    page: str = Field(...)
    rotation: Optional[float] = Field(default=0)

class VisualSignature(BaseModel):
    """Visual signature with position and optional image
    
    Attributes:
        form_field (Optional[str]): Name of the document's form field in which the signature is placed. Takes precedence before positions
        position (Position): 
        image (Optional[Image]): 
    """
    form_field: Optional[str] = Field(description="Name of the document's form field in which the signature is placed. Takes precedence before positions", max_length=100)
    position: Position = Field(...)
    image: Optional[Image]

class Signature(BaseModel):
    """Represents a signature in a signature request
    
    Attributes:
        account_email (Optional[EmailStr]): Signer's e-mail address
        signer_identity_data (Optional[SignerIdentityData]): 
        visual_signature (Optional[VisualSignature]): 
        sequence (Optional[int]): Define a signing sequence for signers
        notify (Optional[bool]): Send e-mails to notify the signer
        language (Optional[str]): Language for communication
    """
    account_email: Optional[EmailStr] = Field(description="Signer's e-mail address")
    signer_identity_data: Optional[SignerIdentityData]
    visual_signature: Optional[VisualSignature]
    sequence: Optional[int] = Field(description="Define a signing sequence for signers", ge=1, le=999)
    notify: Optional[bool] = Field(description="Send e-mails to notify the signer", default=True)
    language: Optional[str] = Field(description="Language for communication")

    @model_validator(mode='after')
    def check_email_or_identity(cls, values):
        if not values.account_email and not values.signer_identity_data:
            raise ValueError("Either 'account_email' or 'signer_identity_data' must be provided")
        return values

    @validator('sequence')
    def check_sequence(cls, v):
        if v is not None and (v < 1 or v > 999):
            raise ValueError("Sequence must be between 1 and 999")
        return v


class SignatureRequestLegislation(str, Enum):
    ZERTES = 'ZERTES'
    EIDAS = 'EIDAS'

class SignatureRequestQuality(str, Enum):
    AES = 'AES'
    AES_MINIMAL = 'AES_MINIMAL'
    SES = 'SES'
    QES = 'QES'

class SignatureRequest(BaseModel):
    """Represents a signature request
    
    Attributes:
        title (str): Title of the signature request
        message (Optional[str]): Message sent to the participants
        content (Optional[str]): Base64 encoded bytes of document
        content_type (Optional[str]): Content type of bytes sent in content
        file_url (Optional[str]): Publicly accessible URL for document download
        document_id (Optional[str]): Document ID of an existing document on Skribble
        legislation (Optional[SignatureRequestLegislation]): Legislation of the signatures (ZERTES or EIDAS). Only important for QES signatures
        quality (Optional[SignatureRequestQuality]): Minimal quality of the signatures (AES, AES_MINIMAL, SES or QES)
        cc_email_addresses (Optional[List[EmailStr]]): CC email addresses
        callback_success_url (Optional[str]): Callback-URL for success
        callback_error_url (Optional[str]): Callback-URL for errors
        callback_update_url (Optional[str]): Callback-URL for updates
        custom (Optional[str]): Custom field for own/customer settings
        write_access (Optional[List[EmailStr]]): Users with full write access
        signatures (Optional[List[Signature]]): 
    """
    title: str = Field(description="Title of the signature request", max_length=1024, ...)
    message: Optional[str] = Field(description="Message sent to the participants", max_length=1024)
    content: Optional[str] = Field(description="Base64 encoded bytes of document")
    content_type: Optional[str] = Field(description="Content type of bytes sent in content", max_length=1024)
    file_url: Optional[str] = Field(description="Publicly accessible URL for document download", max_length=2048)
    document_id: Optional[str] = Field(description="Document ID of an existing document on Skribble", max_length=100)
    legislation: Optional[SignatureRequestLegislation] = Field(description="Legislation of the signatures (ZERTES or EIDAS). Only important for QES signatures", max_length=100)
    quality: Optional[SignatureRequestQuality] = Field(description="Minimal quality of the signatures (AES, AES_MINIMAL, SES or QES)", max_length=100)
    cc_email_addresses: Optional[List[EmailStr]] = Field(description="CC email addresses")
    callback_success_url: Optional[str] = Field(description="Callback-URL for success", max_length=2048)
    callback_error_url: Optional[str] = Field(description="Callback-URL for errors", max_length=2048)
    callback_update_url: Optional[str] = Field(description="Callback-URL for updates", max_length=2048)
    custom: Optional[str] = Field(description="Custom field for own/customer settings", max_length=10000)
    write_access: Optional[List[EmailStr]] = Field(description="Users with full write access")
    signatures: Optional[List[Signature]]

    @model_validator(mode='after')
    def check_document_source(self):
        if not any([self.content, self.file_url, self.document_id]):
            raise SkribbleValidationError("At least one of 'content', 'file_url', or 'document_id' must be provided",
                errors=[{"field": "document_source", "message": "At least one of 'content', 'file_url', or 'document_id' must be provided"}])
        return self

    @model_validator(mode='before')
    def check_fields(cls, values):
        valid_fields = cls.model_fields.keys()
        for field in values:
            if field not in valid_fields:
                close_matches = get_close_matches(field, valid_fields, n=1, cutoff=0.6)
                if close_matches:
                    raise ValueError(f"Invalid field '{field}'. Did you mean '{close_matches[0]}'?")
                else:
                    raise ValueError(f"Invalid field '{field}'. Valid fields are: {", ".join(valid_fields)}")
        return values

class Document(BaseModel):
    """Represents a document
    
    Attributes:
        id (str): ID of the Document object
        parent_id (Optional[str]): ID of the previous version of the Document object
        title (str): Given title of the document
        content_type (str): Content type of the document
        size (int): Size in bytes of the document
        page_count (Optional[int]): Number of pages in the document
        page_width (Optional[int]): Width of the document pages
        page_height (Optional[int]): Height of the document pages
        owner (str): Owner of the document
    """
    id: str = Field(description="ID of the Document object", ...)
    parent_id: Optional[str] = Field(description="ID of the previous version of the Document object")
    title: str = Field(description="Given title of the document", max_length=1024, ...)
    content_type: str = Field(description="Content type of the document", ...)
    size: int = Field(description="Size in bytes of the document", ...)
    page_count: Optional[int] = Field(description="Number of pages in the document")
    page_width: Optional[int] = Field(description="Width of the document pages")
    page_height: Optional[int] = Field(description="Height of the document pages")
    owner: str = Field(description="Owner of the document", ...)

class DocumentRequest(BaseModel):
    """Request to create a new document
    
    Attributes:
        title (str): Title of the document
        content_type (Optional[str]): Content type of bytes sent in content
        content (Optional[str]): Base64 encoded bytes of document
        file_url (Optional[str]): Publicly accessible URL for document download
        write_access (Optional[List[EmailStr]]): E-mail addresses with write access to the object
    """
    title: str = Field(description="Title of the document", max_length=1024, ...)
    content_type: Optional[str] = Field(description="Content type of bytes sent in content", max_length=100)
    content: Optional[str] = Field(description="Base64 encoded bytes of document")
    file_url: Optional[str] = Field(description="Publicly accessible URL for document download", max_length=2048)
    write_access: Optional[List[EmailStr]] = Field(description="E-mail addresses with write access to the object")

    @model_validator(mode='after')
    def check_content_or_file_url(cls, values):
        if bool(values.content) == bool(values.file_url):
            raise SkribbleValidationError("Either 'content' or 'file_url' must be provided, but not both",
                errors=[{"field": "content_source", "message": "Either 'content' or 'file_url' must be provided, but not both"}])
        if values.content and not values.content_type:
            raise SkribbleValidationError("'content_type' must be provided when 'content' is used",
                errors=[{"field": "content_type", "message": "'content_type' must be provided when 'content' is used"}])
        return values

class SignerRequest(BaseModel):
    """Request to add a signer
    
    Attributes:
        account_email (Optional[EmailStr]): Signer's e-mail address
        signer_identity_data (Optional[SignerIdentityData]): 
        visual_signature (Optional[VisualSignature]): 
        sequence (Optional[int]): 
        notify (Optional[bool]): 
        language (Optional[str]): 
    """
    account_email: Optional[EmailStr] = Field(description="Signer's e-mail address")
    signer_identity_data: Optional[SignerIdentityData]
    visual_signature: Optional[VisualSignature]
    sequence: Optional[int] = Field(ge=1, le=999)
    notify: Optional[bool] = Field(default=True)
    language: Optional[str]

    @model_validator(mode='after')
    def check_email_or_identity(cls, values):
        if not values.account_email and not values.signer_identity_data:
            raise ValueError("Either 'account_email' or 'signer_identity_data' must be provided")
        return values

class UpdateSignatureRequest(BaseModel):
    """Request to update a signature request
    
    Attributes:
        id (str): ID of the signature request to update
        title (Optional[str]): New title of the signature request
        message (Optional[str]): New message sent to the participants
        legislation (Optional[str]): New legislation of the signatures
        quality (Optional[str]): New minimal quality of the signatures
        cc_email_addresses (Optional[List[EmailStr]]): New CC email addresses
        callback_success_url (Optional[str]): New callback-URL for success
        callback_error_url (Optional[str]): New callback-URL for errors
        callback_update_url (Optional[str]): New callback-URL for updates
        custom (Optional[str]): New custom field for own/customer settings
        write_access (Optional[List[EmailStr]]): New users with full write access
    """
    id: str = Field(description="ID of the signature request to update", ...)
    title: Optional[str] = Field(description="New title of the signature request", max_length=1024)
    message: Optional[str] = Field(description="New message sent to the participants", max_length=1024)
    legislation: Optional[str] = Field(description="New legislation of the signatures", max_length=100)
    quality: Optional[str] = Field(description="New minimal quality of the signatures", max_length=100)
    cc_email_addresses: Optional[List[EmailStr]] = Field(description="New CC email addresses")
    callback_success_url: Optional[str] = Field(description="New callback-URL for success", max_length=2048)
    callback_error_url: Optional[str] = Field(description="New callback-URL for errors", max_length=2048)
    callback_update_url: Optional[str] = Field(description="New callback-URL for updates", max_length=2048)
    custom: Optional[str] = Field(description="New custom field for own/customer settings", max_length=10000)
    write_access: Optional[List[EmailStr]] = Field(description="New users with full write access")

class Attachment(BaseModel):
    """Attachment for a document
    
    Attributes:
        title (str): Title of the attachment
        content (str): Base64 encoded bytes of the attachment
        content_type (str): Content type of the attachment
    """
    title: str = Field(description="Title of the attachment", max_length=1024, ...)
    content: str = Field(description="Base64 encoded bytes of the attachment", ...)
    content_type: str = Field(description="Content type of the attachment", max_length=100, ...)

class SealRequest(BaseModel):
    """Request to seal a document
    
    Attributes:
        title (str): Title of the seal document
        content (str): Base64 encoded bytes of document
        account_name (Optional[str]): Specifies the seal to use for sealing
        visual_signature (Optional[VisualSignature]): 
    """
    title: str = Field(description="Title of the seal document", max_length=1024, ...)
    content: str = Field(description="Base64 encoded bytes of document", ...)
    account_name: Optional[str] = Field(description="Specifies the seal to use for sealing", max_length=256)
    visual_signature: Optional[VisualSignature]

class Seal(BaseModel):
    """Seal for a document
    
    Attributes:
        title (Optional[str]): Title of the seal document
        content (str): Base64 encoded bytes of document
        account_name (Optional[str]): Specifies the seal to use for sealing
        visual_signature (Optional[VisualSignature]): 
    """
    title: Optional[str] = Field(description="Title of the seal document", max_length=1024)
    content: str = Field(description="Base64 encoded bytes of document", ...)
    account_name: Optional[str] = Field(description="Specifies the seal to use for sealing", max_length=256)
    visual_signature: Optional[VisualSignature]

class SignatureRequestResponse(BaseModel):
    """Response object for a signature request
    
    Attributes:
        id (str): ID of the SignatureRequest object
        title (str): Given title for the signature request
        message (Optional[str]): Given message that is shown to the participants
        document_id (str): ID of the Document object
        legislation (Optional[str]): Given legislation of the signatures (ZERTES or EIDAS)
        quality (Optional[str]): Given quality of the signatures (AES, SES, QES or DEMO)
        status_overall (str): Status of the signature request (OPEN, DECLINED, WITHDRAWN or SIGNED)
        signatures (List[SignatureResponse]): Array of signatures within this signature request
        cc_email_addresses (Optional[List[EmailStr]]): Array of email-addresses for notifications
        owner (str): Creator of the SignatureRequest object
        read_access (List[EmailStr]): Array of users with read access
        write_access (List[EmailStr]): Array of users with write access
        created_at (str): Timestamp at which the signature request was created
        updated_at (Optional[str]): Timestamp at which the signature request was last updated
    """
    id: str = Field(description="ID of the SignatureRequest object", ...)
    title: str = Field(description="Given title for the signature request", max_length=1024, ...)
    message: Optional[str] = Field(description="Given message that is shown to the participants", max_length=1024)
    document_id: str = Field(description="ID of the Document object", ...)
    legislation: Optional[str] = Field(description="Given legislation of the signatures (ZERTES or EIDAS)", max_length=100)
    quality: Optional[str] = Field(description="Given quality of the signatures (AES, SES, QES or DEMO)", max_length=100)
    status_overall: str = Field(description="Status of the signature request (OPEN, DECLINED, WITHDRAWN or SIGNED)", ...)
    signatures: List[SignatureResponse] = Field(description="Array of signatures within this signature request", ...)
    cc_email_addresses: Optional[List[EmailStr]] = Field(description="Array of email-addresses for notifications")
    owner: str = Field(description="Creator of the SignatureRequest object", ...)
    read_access: List[EmailStr] = Field(description="Array of users with read access", ...)
    write_access: List[EmailStr] = Field(description="Array of users with write access", ...)
    created_at: str = Field(description="Timestamp at which the signature request was created", ...)
    updated_at: Optional[str] = Field(description="Timestamp at which the signature request was last updated")

class SignatureResponse(BaseModel):
    """Response object for a signature
    
    Attributes:
        sid (str): ID of the Signature object
        account_email (Optional[EmailStr]): Email address of the signer
        signer_identity_data (Optional[SignerIdentityData]): Identity data of the signer
        sequence (Optional[int]): Signing sequence for the signer
        order (Optional[int]): Deprecated. Replaced by sequence
        status_code (str): Status of the signature (OPEN, DECLINED or SIGNED)
        notify (bool): Whether the signer will be notified about changes
        signed_at (Optional[str]): Timestamp UTC at which the signature was executed
        signed_quality (Optional[str]): Quality level with which the signature was executed
        signed_legislation (Optional[str]): Legislation with which the signature was executed
        last_viewed_at (Optional[str]): Timestamp UTC at which the signer last viewed the document
        decline_message (Optional[str]): Message provided when declining the signature
        language (Optional[str]): Language in which the signer was invited
        signing_url (str): URL where to find the prepared document ready for signing
    """
    sid: str = Field(description="ID of the Signature object", ...)
    account_email: Optional[EmailStr] = Field(description="Email address of the signer")
    signer_identity_data: Optional[SignerIdentityData] = Field(description="Identity data of the signer")
    sequence: Optional[int] = Field(description="Signing sequence for the signer", ge=1, le=999)
    order: Optional[int] = Field(description="Deprecated. Replaced by sequence", le=999)
    status_code: str = Field(description="Status of the signature (OPEN, DECLINED or SIGNED)", ...)
    notify: bool = Field(description="Whether the signer will be notified about changes", ...)
    signed_at: Optional[str] = Field(description="Timestamp UTC at which the signature was executed")
    signed_quality: Optional[str] = Field(description="Quality level with which the signature was executed")
    signed_legislation: Optional[str] = Field(description="Legislation with which the signature was executed")
    last_viewed_at: Optional[str] = Field(description="Timestamp UTC at which the signer last viewed the document")
    decline_message: Optional[str] = Field(description="Message provided when declining the signature")
    language: Optional[str] = Field(description="Language in which the signer was invited")
    signing_url: str = Field(description="URL where to find the prepared document ready for signing")

class DocumentResponse(BaseModel):
    """Response object for a document
    
    Attributes:
        id (str): ID of the Document object
        parent_id (Optional[str]): ID of the previous version of the Document object
        title (str): Given title of the document
        content_type (str): Content type of the document (always application/pdf)
        size (int): Size in bytes of the document
        page_count (Optional[int]): Number of pages of the document
        page_width (Optional[int]): Width of the document in pixel
        page_height (Optional[int]): Height of the document in pixel
        signature_fields (Optional[List[object]]): PDF AcroForm signature fields found in the document
        read_access (List[EmailStr]): Array of users with read access
        write_access (List[EmailStr]): Array of users with write access
        created_at (str): Timestamp at which the document was created
        updated_at (Optional[str]): Timestamp at which the document was last updated
    """
    id: str = Field(description="ID of the Document object", ...)
    parent_id: Optional[str] = Field(description="ID of the previous version of the Document object")
    title: str = Field(description="Given title of the document", max_length=1024, ...)
    content_type: str = Field(description="Content type of the document (always application/pdf)", ...)
    size: int = Field(description="Size in bytes of the document", ...)
    page_count: Optional[int] = Field(description="Number of pages of the document")
    page_width: Optional[int] = Field(description="Width of the document in pixel")
    page_height: Optional[int] = Field(description="Height of the document in pixel")
    signature_fields: Optional[List[object]] = Field(description="PDF AcroForm signature fields found in the document")
    read_access: List[EmailStr] = Field(description="Array of users with read access", ...)
    write_access: List[EmailStr] = Field(description="Array of users with write access", ...)
    created_at: str = Field(description="Timestamp at which the document was created", ...)
    updated_at: Optional[str] = Field(description="Timestamp at which the document was last updated")
