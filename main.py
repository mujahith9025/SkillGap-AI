import os
import uvicorn

if __name__ == "__main__":
    # Render, Railway, and Heroku pass the dynamic port via $PORT
    port = int(os.environ.get("PORT", 10000))
    print(f"[*] Starting SkillGap AI on host 0.0.0.0, port {port}...")
    uvicorn.run("api:app", host="0.0.0.0", port=port, log_level="info")
