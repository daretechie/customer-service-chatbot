from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredFileLoader
)
import os

def process_file(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    
    loaders = {
        '.txt': TextLoader,
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.csv': lambda path: CSVLoader(path, encoding='utf-8')
    }
    
    try:
        if extension in loaders:
            loader = loaders[extension](file_path)
        else:
            loader = UnstructuredFileLoader(file_path)
        return loader.load()
    except Exception as e:
        raise Exception(f"Failed to process {file_path}: {str(e)}")