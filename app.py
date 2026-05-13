from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from textSummarizer.pipeline.prediction import PredictionPipeline
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Text Summarizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 750px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2rem; color: #4a3f8f; margin-bottom: 8px; }
        .header p { color: #888; font-size: 0.95rem; }
        .badge {
            display: inline-block;
            background: #ede9fe;
            color: #6d28d9;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 12px;
        }
        label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #555;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        textarea {
            width: 100%;
            height: 200px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 14px;
            font-size: 0.95rem;
            resize: vertical;
            transition: border 0.2s;
            outline: none;
            font-family: inherit;
            color: #333;
        }
        textarea:focus { border-color: #7c3aed; }
        .char-count { text-align: right; font-size: 0.8rem; color: #aaa; margin-top: 4px; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 16px;
            transition: opacity 0.2s, transform 0.1s;
        }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        button:active { transform: translateY(0); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .result-box {
            margin-top: 24px;
            background: #f5f3ff;
            border: 2px solid #ddd6fe;
            border-radius: 12px;
            padding: 20px;
            display: none;
        }
        .result-box h3 {
            color: #6d28d9;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        .result-box p { color: #374151; line-height: 1.7; font-size: 0.95rem; }
        .loader { display: none; text-align: center; padding: 16px; color: #7c3aed; font-size: 0.9rem; }
        .spinner {
            border: 3px solid #ede9fe;
            border-top: 3px solid #7c3aed;
            border-radius: 50%;
            width: 28px; height: 28px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .copy-btn {
            background: none;
            border: 1px solid #ddd6fe;
            color: #7c3aed;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            margin-top: 12px;
            width: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">✦ Powered by PEGASUS</span>
            <h1>Text Summarizer</h1>
            <p>Paste any long text and get a concise summary instantly</p>
        </div>
        <label>Input Text</label>
        <textarea id="inputText" placeholder="Paste your article, paragraph or document here..." oninput="updateCount()"></textarea>
        <div class="char-count"><span id="charCount">0</span> characters</div>
        <button onclick="summarize()" id="btn">Summarize</button>
        <div class="loader" id="loader">
            <div class="spinner"></div>
            Generating summary...
        </div>
        <div class="result-box" id="result">
            <h3>Summary</h3>
            <p id="summaryText"></p>
            <button class="copy-btn" onclick="copyText()">Copy Summary</button>
        </div>
    </div>
    <script>
        function updateCount() {
            document.getElementById('charCount').textContent = document.getElementById('inputText').value.length;
        }
        async function summarize() {
            const text = document.getElementById('inputText').value.trim();
            if (!text) { alert('Please enter some text!'); return; }
            document.getElementById('btn').disabled = true;
            document.getElementById('loader').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                });
                const data = await response.json();
                document.getElementById('summaryText').textContent = data.summary;
                document.getElementById('result').style.display = 'block';
            } catch(e) {
                alert('Error: ' + e.message);
            }
            document.getElementById('btn').disabled = false;
            document.getElementById('loader').style.display = 'none';
        }
        function copyText() {
            navigator.clipboard.writeText(document.getElementById('summaryText').textContent);
            alert('Copied!');
        }
    </script>
</body>
</html>
    """)

@app.post("/predict")
async def predict_route(input: TextInput):
    try:
        obj = PredictionPipeline()
        summary = obj.predict(input.text)
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"summary": f"Error: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)