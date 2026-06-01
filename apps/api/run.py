#!/usr/bin/env python3
"""Universal entry point that detects whether to run web or worker."""
import os
import sys

service_name = os.environ.get("RAILWAY_SERVICE_NAME", "").lower()

if "worker" in service_name or "fortunate" in service_name:
    print(f"[run.py] Detected worker service: {service_name}")
    print("[run.py] Starting Celery worker...")
    sys.argv = ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"]
    from celery.__main__ import main
    main()
else:
    print(f"[run.py] Detected web service: {service_name}")
    print("[run.py] Starting Uvicorn web server...")
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
