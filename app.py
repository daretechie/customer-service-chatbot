from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import openai
import glob
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from config import Config
from file_processor import process_file

app = Flask(__name__)
app.config.from_object(Config)
auth = HTTPBasicAuth()

# Initialize OpenAI
openai.api_key = app.config['OPENAI_API_KEY']
embeddings = OpenAIEmbeddings(openai_api_key=app.config['OPENAI_API_KEY'])

# Vector store instance
vector_store = None

# Authentication
users = {
    app.config['ADMIN_USER']: generate_password_hash(app.config['ADMIN_PASSWORD'])
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_documents():
    global vector_store
    documents = []
    
    for file_path in glob.glob('data/**/*.*', recursive=True):
        try:
            documents += process_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    vector_store = FAISS.from_documents(docs, embeddings)

@app.route('/')
def chat():
    return render_template('chat.html')

@app.route('/admin')
@auth.login_required
def admin():
    return render_template('admin.html')

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    user_input = request.json['message']
    
    context = ""
    if vector_store:
        docs = vector_store.similarity_search(user_input, k=2)
        context = "\n".join([doc.page_content for doc in docs])
    
    prompt = f"""Answer using context below. If unsure, say you don't know.
    
    Context: {context}
    
    Question: {user_input}
    
    Answer:"""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return jsonify({'response': response.choices[0].message.content})

@app.route('/api/upload', methods=['POST'])
@auth.login_required
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        process_documents()
        return jsonify({'message': 'File uploaded and processed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)