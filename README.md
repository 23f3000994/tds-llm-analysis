# LLM Analysis Quiz Endpoint

## 🔧 Setup (Local)

1. Install dependencies:
   ```
   pip install -r requirements.txt
   playwright install
   ```
2. Set your quiz secret:
   - Windows PowerShell:
     ```
     $env:QUIZ_SECRET="this-is-very-secret"
     ```
   - Linux/macOS:
     ```
     export QUIZ_SECRET="this-is-very-secret"
     ```
3. Run the server:
   ```
   python app.py
   ```

## 🚀 Usage

Send a POST request to your endpoint:

```
POST /quiz-webhook
Content-Type: application/json
```

Example body:
```json
{
  "email": "23f3000994@ds.study.iitm.ac.in",
  "secret": "this-is-very-secret",
  "url": "https://tds-llm-analysis.s-anand.net/demo"
}
```

## 📁 Project Structure

```
app.py
pdf_helpers.py
requirements.txt
Dockerfile
README.md
LICENSE
```

## 📝 Notes

- This endpoint automatically solves quiz tasks and handles chaining.
- Works for both scrape-mode and base64-mode quizzes.
- Ensure your environment has Chromium (Playwright) set up properly.

## 👤 Author

**Vaidik Dave**
