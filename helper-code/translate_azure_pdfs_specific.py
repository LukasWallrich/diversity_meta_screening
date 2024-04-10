import csv
import os
import shutil
from PyPDF2 import PdfReader, PdfWriter
from azure.storage.blob import BlobServiceClient
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
from azure.core.credentials import AzureKeyCredential

# Constants - Replace with your Azure credentials and storage details
CONNECTION_STRING = "SharedAccessSignature=sv=2023-01-03&ss=btqf&srt=sco&st=2023-11-26T16%3A57%3A47Z&se=2023-11-27T16%3A57%3A47Z&sp=rwlacu&sig=LTVlPxGSwQJcCNSMir7c%2FPO4BQwwUQZ6jf4COxLQv3g%3D;BlobEndpoint=https://translatepdf.blob.core.windows.net/;FileEndpoint=https://translatepdf.file.core.windows.net/;QueueEndpoint=https://translatepdf.queue.core.windows.net/;TableEndpoint=https://translatepdf.table.core.windows.net/;"
TRANSLATOR_ENDPOINT = "https://metatranslate.cognitiveservices.azure.com/"
TRANSLATOR_KEY = "2b9f66c90f7647b3aad3a19af0faad43"
CONTAINER_NAME = "pdfs"
TARGET_LANGUAGE = "en"  # Target language for translation

# Initialize Azure clients
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
translator_client = DocumentTranslationClient(TRANSLATOR_ENDPOINT, AzureKeyCredential(TRANSLATOR_KEY))
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def extract_pages(pdf_filename, page_ranges):
    """
    Extracts specified page ranges from a PDF file and saves as a new PDF.
    If page_ranges is blank, the entire file is copied to a new file.
    Args:
        pdf_filename (str): Name of the PDF file to extract pages from.
        page_ranges (str): Page ranges in the format "1-3; 5-7" or blank for the entire file.
    Returns:
        str: Filename of the extracted or copied PDF.
    """
    output_filename = f"extracted_{os.path.basename(pdf_filename)}"

    # Handle the case where no page range is specified
    if not page_ranges.strip():
        shutil.copy(pdf_filename, output_filename)
        return output_filename

    # Initialize PDF reader and writer for page extraction
    reader = PdfReader(pdf_filename)
    writer = PdfWriter()

    # Process each page range
    for range in page_ranges.split(';'):
        start, end = map(int, range.split('-'))
        for page in range(start, end + 1):
            writer.add_page(reader.pages[page - 1])

    # Write the extracted pages to a new file
    with open(output_filename, 'wb') as output_file:
        writer.write(output_file)

    return output_filename


def upload_to_azure(local_file_name):
    # Uploads a file to Azure Storage and returns the URL
    pass

def batch_translate_documents(documents):
    # Starts a batch translation job for a list of document URLs
    inputs = [
        DocumentTranslationInput(
            source_url=document,
            targets=[TranslationTarget(target_url=document, language_code=TARGET_LANGUAGE)]
        ) for document in documents
    ]
    job = translator_client.begin_translation(inputs)
    job.wait()  # Wait for the job to complete

# Read CSV file and prepare for batch processing
translation_tasks = []
document_urls = []

with open('translation_tasks.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        pdf_filename = row['filename']
        page_ranges = row['pageranges']  # Format: "1-3; 5-7"
        
        extracted_file = extract_pages(pdf_filename, page_ranges)
        with open(extracted_file, "rb") as data:
            uploaded_url = container_client.upload_blob(name = extracted_file, data=data, overwrite=True)
        translation_tasks.append(extracted_file)
       
""" 
# Start batch translation
batch_translate_documents(document_urls)

# Download translated documents (implementation needed)
# for url in document_urls:
#     download_translated_document(url)



key = ""
endpoint = ""


source_url = "https://translatepdf.blob.core.windows.net/pdfs?sv=2023-01-03&st=2023-11-26T10%3A36%3A55Z&se=2023-11-27T10%3A36%3A55Z&sr=c&sp=rl&sig=wwkDMFCN%2BMCTEM3w0FE%2B11NtMajUA05eF35oHMI55b4%3D"
target_url = "https://translatepdf.blob.core.windows.net/translate-out?sv=2023-01-03&st=2023-11-26T10%3A37%3A29Z&se=2023-11-27T10%3A37%3A29Z&sr=c&sp=racwl&sig=48Glr4fC893dvEyJDhn7Uc1GQUshnumTqt0057a8xIw%3D"

from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

document_translation_client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
poller = document_translation_client.begin_translation(source_url, target_url, "en")

# Get the result from the poller
result = poller.result()

# Print the number of documents that failed and succeeded
print(f"\nOf total documents...")
print(f"{poller.details.documents_failed_count} failed")
print(f"{poller.details.documents_succeeded_count} succeeded")

# Loop through each document in the result
for document in result:
    print(f"Document ID: {document.id}")
    print(f"Document status: {document.status}")
    
    # Check if the document processing succeeded
    if document.status == "Succeeded":
        print(f"Source document location: {document.source_document_url}")
        print(f"Translated document location: {document.translated_document_url}")
        print(f"Translated to language: {document.translated_to}\n")
    else:
        # Handle error case
        print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")

### Download

from azure.storage.blob import BlobServiceClient

# Initialize BlobServiceClient
connection_str = "your_connection_string_here"
blob_service_client = BlobServiceClient.from_connection_string(connection_str)

# Get container client
container_name = "translate-out"
container_client = blob_service_client.get_container_client(container_name)

# Download all blobs in container
for blob in container_client.list_blobs():
    blob_client = container_client.get_blob_client(blob.name)
    blob_data = blob_client.download_blob()
    
    # Save blob to a local file
    with open(f"~/{blob.name}", "wb") as f:
        f.write(blob_data.readall())
 """