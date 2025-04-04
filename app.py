from flask import Flask, request, jsonify, render_template
import os
import openai

from werkzeug.utils import secure_filename
import PyPDF2
import docx
import numpy as np

import pickle
import hashlib

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['VECTOR_STORE'] = 'vector_store'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Configure OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_embedding(text, engine):
    response = openai.Embedding.create(
        model=engine,
        input=text
    )
    return response.data[0].embedding

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(filepath):
    if filepath.endswith('.pdf'):
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages])
    elif filepath.endswith('.docx'):
        doc = docx.Document(filepath)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:  # txt file
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def generate_embeddings(chunks):
    return [get_embedding(chunk, engine="text-embedding-ada-002") for chunk in chunks]

def save_vector_store(document_hash, chunks, embeddings):
    os.makedirs(app.config['VECTOR_STORE'], exist_ok=True)
    store_path = os.path.join(app.config['VECTOR_STORE'], f"{document_hash}.pkl")
    with open(store_path, 'wb') as f:
        pickle.dump({'chunks': chunks, 'embeddings': embeddings}, f)

def load_vector_store(document_hash):
    store_path = os.path.join(app.config['VECTOR_STORE'], f"{document_hash}.pkl")
    if os.path.exists(store_path):
        with open(store_path, 'rb') as f:
            return pickle.load(f)
    return None

def get_document_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def retrieve_relevant_chunks(query, chunks, embeddings, top_k=3):
    query_embedding = get_embedding(query, engine="text-embedding-ada-002")
    similarities = [np.dot(query_embedding, emb) for emb in embeddings]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]

def generate_faqs(document_text):
    chunks = chunk_text(document_text)
    relevant_chunks = chunks[:5]  # Use first few chunks for FAQ generation
    
    prompt = f"""
    Analyze these business document sections and generate 10 relevant FAQs with answers:
    
    Document Sections:
    {relevant_chunks}
    
    Format as:
    Q: [Question]
    A: [Answer]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def get_chat_response(query, context_chunks):
    context = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""
    You are a knowledgeable customer support agent for this business. 
    Use the following document sections to answer the customer's question.
    If you don't know the answer, say you don't know - don't make up information.
    
    Relevant Document Sections:
    {context}
    
    Customer Question:
    {query}
    
    Provide a helpful, professional response that directly addresses the question using the provided context.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text and process document
        document_text = extract_text_from_file(filepath)
        document_hash = get_document_hash(document_text)
        
        # Check if we already have this processed
        vector_store = load_vector_store(document_hash)
        
        if not vector_store:
            # Process new document
            chunks = chunk_text(document_text)
            embeddings = generate_embeddings(chunks)
            save_vector_store(document_hash, chunks, embeddings)
        else:
            chunks = vector_store['chunks']
            embeddings = vector_store['embeddings']
        
        # Generate FAQs from first few chunks
        faqs = generate_faqs(document_text)
        
        return jsonify({
            'message': 'File processed successfully',
            'faqs': faqs,
            'document_hash': document_hash,
            'chunk_count': len(chunks)
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    document_hash = data.get('document_hash')
    
    if not query or not document_hash:
        return jsonify({'error': 'Missing query or document hash'}), 400
    
    vector_store = load_vector_store(document_hash)
    if not vector_store:
        return jsonify({'error': 'Document not found'}), 404
    
    # Retrieve relevant chunks
    relevant_chunks = retrieve_relevant_chunks(
        query, 
        vector_store['chunks'], 
        vector_store['embeddings']
    )
    
    # Get response using relevant context
    response = get_chat_response(query, relevant_chunks)
    
    return jsonify({
        'response': response,
        'relevant_chunks': relevant_chunks  # For debugging/display
    })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VECTOR_STORE'], exist_ok=True)
    app.run(debug=True)
