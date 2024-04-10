key = "2b9f66c90f7647b3aad3a19af0faad43"
endpoint = "https://metatranslate.cognitiveservices.azure.com/"


source_url = "https://translatepdf.blob.core.windows.net/pdfs?sv=2023-01-03&st=2023-11-27T13%3A02%3A46Z&se=2023-12-28T13%3A02%3A00Z&sr=c&sp=rl&sig=yMOUQN5NHca3M5jetfkXd7n%2FyKvhCcJi6iFRrn8TBFg%3D"
target_url = "https://translatepdf.blob.core.windows.net/translate-out?sv=2023-01-03&st=2023-11-27T13%3A03%3A18Z&se=2023-12-28T13%3A03%3A00Z&sr=c&sp=rawl&sig=uP5IXzHERgjRvxrdlCWsFWjEdVwEVETz3aAbs86C8OI%3D"

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

""" ### Download

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