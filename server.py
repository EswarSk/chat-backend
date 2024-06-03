from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
import os
from pydantic import BaseModel

app = FastAPI()

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=512, api_key='')

class ParameterModel(BaseModel):
    parameter: str

async def event_stream(prompt: str):
    try:
        # Sending a specific JSON event
        for chunk in llm.stream(prompt):
            print(chunk, end="", flush=True)
            data = {"text": chunk}
            yield f"event: data\n"
            yield f"data: {json.dumps(data)}\n\n"

        # Indicating the end of the stream
        yield f"event: end\n"
    except Exception as e:
        yield f"event: error\ndata: {str(e)}\n\n"

@app.post("/stream")
async def stream_endpoint(parameter_model: ParameterModel):
    return StreamingResponse(event_stream(parameter_model.parameter), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
