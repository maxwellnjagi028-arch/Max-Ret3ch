import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting MaxReT3ch AI Platform on http://127.0.0.1:{port}")
    print("Operated by Ted - Autonomous AI Operations Specialist")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
