# LLM Analysis Quiz Endpoint

## Setup (local)
1. Copy `.env` with QUIZ_SECRET.
2. Install dependencies:
   pip install -r requirements.txt
   python -m playwright install
3. Ensure Tesseract and Poppler are installed on your system.
4. Run:
   export QUIZ_SECRET="w8xH7k-quiz-secret"
   python app.py

## Test with demo:
curl -X POST http://localhost:8080/quiz-webhook -H "Content-Type: application/json" -d '{"email":"23f3000994@ds.study.iitm.ac.in","secret":"w8xH7k-quiz-secret","url":"https://tds-llm-analysis.s-anand.net/demo"}'
