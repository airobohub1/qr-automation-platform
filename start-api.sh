#!/bin/sh
exec python -m uvicorn app.modules.qr_generator.backend.main:app --host 0.0.0.0 --port ${PORT}
