#!/bin/bash
export $(cat .env.local | grep -v '^#' | xargs)
uvicorn app.main:app --reload
