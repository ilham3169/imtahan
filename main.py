from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.middleware.trustedhost import TrustedHostMiddleware # type: ignore

import os

from redis import Redis
from routers import questions, exams, answers, user_exams, user_answers
from routers.auth import auth
from aws import s3


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://texnotech.vercel.app", 
                   "https://admin-texnotech.vercel.app", 
                   "http://127.0.0.1:5173",
                   "http://localhost:5173",
                   "http://localhost:5174",
                   "https://texnotech.com",
                   "https://exam-project-gamma.vercel.app"],  # Allow only your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():

    # Connect Redis database to FastAPI application
    redis_url = os.getenv("REDIS_URL")
    app.state.redis = Redis.from_url(redis_url)



# Disconnect from Redis on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()


app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(user_exams.router)
app.include_router(user_answers.router)