document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.getElementById('upload-button');
    const fileInput = document.getElementById('document-upload');

    async function uploadDocument() {
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file first');
            return;
        }

        uploadButton.disabled = true;
        uploadButton.textContent = 'Uploading...';

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            alert(result.message || result.error);
            fileInput.value = '';
        } catch (error) {
            alert('Error uploading file');
        } finally {
            uploadButton.disabled = false;
            uploadButton.textContent = 'Upload Knowledge Base';
        }
    }

    uploadButton.addEventListener('click', uploadDocument);
});