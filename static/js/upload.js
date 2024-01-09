function addGoogleSignInEventListener() {
  const googleSignInButton = document.getElementById('google-sign-in-button');
  if (googleSignInButton) {
      googleSignInButton.addEventListener('click', oauth2SignIn);
  }
}

function setupUploadForm() {
  document.getElementById('upload-form').addEventListener('submit', function(event) {
      event.preventDefault();
      uploadFile(this);
  });
}

function uploadFile(formElement) {
  var formData = new FormData(formElement);
  var loader = document.getElementById('loader');
  showLoader(loader);

  fetch('/upload', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      console.log("Upload response:", data);
      if (data.error) {
          alert("Upload Error: " + data.error);
      } else {
          alert('File processed successfully!');
      }
  })
  .catch(error => {
      console.error('Error:', error);
      alert('Error occurred: ' + error.message);
  })
  .finally(() => hideLoader(loader));
}


function showLoader(loaderElement) {
  loaderElement.style.display = 'block';
}

function hideLoader(loaderElement) {
  loaderElement.style.display = 'none';
}

function addDownloadCsvEventListener() {
  const downloadCsvButton = document.getElementById('download-csv-button');
  if (downloadCsvButton) {
      downloadCsvButton.addEventListener('click', downloadCsv);
  }
}

function downloadCsv() {
  fetch('/download_csv', { method: 'GET' })
  .then(response => response.blob())
  .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'firestore_data.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
  })
  .catch(error => {
      console.error('Error downloading CSV:', error);
      alert('Error occurred while downloading CSV: ' + error.message);
  });
}

// Initialize the event listeners
addGoogleSignInEventListener();
setupUploadForm();
addDownloadCsvEventListener();
