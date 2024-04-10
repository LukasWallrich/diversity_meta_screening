import google.cloud.translate as translate
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_translate.json"
os.environ["GOOGLE_PROJECT_ID"] = "airy-box-268214"

def translate_pdf(file_path: str, destination: str, target_lang: str = 'en', source_lang: str = ''):

    if not os.path.isfile(file_path):
        raise ValueError("Error: The file does not exist or is not a regular file.")

    if not file_path.lower().endswith('.pdf'):
        raise ValueError("Error: The file is not a PDF file.")

    client = translate.TranslationServiceClient()

    location = "us-central1"

    parent = f"projects/{os.environ['GOOGLE_PROJECT_ID']}/locations/{location}"

    # Supported file types: https://cloud.google.com/translate/docs/supported-formats
    with open(file_path, "rb") as document:
        document_content = document.read()

    document_input_config = {
        "content": document_content,
        "mime_type": "application/pdf",
    }

    response = client.translate_document(
        request={
            "parent": parent,
            "target_language_code": target_lang,
            "source_language_code": source_lang,
            "document_input_config": document_input_config,
        }
    )

    # To output the translated document, uncomment the code below.
    f = open(destination, 'wb')
    f.write(response.document_translation.byte_stream_outputs[0])
    f.close()

    # If not provided in the TranslationRequest, the translated file will only be returned through a byte-stream
    # and its output mime type will be the same as the input file's mime type
    print(f"Response: Detected Language Code - {response.document_translation.detected_language_code}")
