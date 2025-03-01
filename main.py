from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import HTMLResponse
from opensearchpy import OpenSearch
import os

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OpenSearch Configuration
OPENSEARCH_HOST = "localhost"
OPENSEARCH_PORT = 9200
INDEX_NAME = "files_index"

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    http_auth=("admin", "admin"),  # Change if necessary
)

# Ensure index exists
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(index=INDEX_NAME)

@app.get("/", response_class=HTMLResponse)
def get_html_form():
    html_content = """
    <html>
        <body>
            <h2>Upload a File</h2>
            <form id="uploadForm" enctype="multipart/form-data" method="post">
                <input id="fileInput" name="file" type="file">
                <button type="button" onclick="uploadFile()">Upload</button>
            </form>

            <h2>Search Files</h2>
            <input type="text" id="searchBox" placeholder="Search files..." onkeyup="fetchFiles()">

            <h2>Uploaded Files</h2>
            <ul id="fileList"></ul>

            <script>
                async function uploadFile() {
                    let fileInput = document.getElementById("fileInput");
                    let formData = new FormData();
                    formData.append("file", fileInput.files[0]);

                    let response = await fetch("/uploadfile/", { method: "POST", body: formData });
                    if (response.ok) {
                        alert("File uploaded successfully!");
                        fetchFiles();
                    }
                }

                async function fetchFiles() {
                    let searchQuery = document.getElementById("searchBox").value;
                    let response = await fetch(`/files/?search=${searchQuery}`);
                    let files = await response.json();

                    let fileList = document.getElementById("fileList");
                    fileList.innerHTML = "";
                    files.forEach(file => {
                        let li = document.createElement("li");
                        li.textContent = file;
                        fileList.appendChild(li);
                    });
                }

                window.onload = fetchFiles;
            </script>
        </body>
    </html>
    """
    return html_content

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Index file metadata in OpenSearch
    document = {"filename": file.filename, "path": file_path}
    client.index(index=INDEX_NAME, body=document)

    return {"message": f"File '{file.filename}' uploaded successfully!"}

@app.get("/files/")
async def search_files(search: str = Query("", description="Search term for filenames")):
    query = {
        "query": {
            "match": {
                "filename": search
            }
        }
    } if search else {"query": {"match_all": {}}}

    response = client.search(index=INDEX_NAME, body=query)
    files = [hit["_source"]["filename"] for hit in response["hits"]["hits"]]

    return files
