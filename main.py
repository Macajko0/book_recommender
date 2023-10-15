from fastapi import FastAPI

from endpoints import book as book_endpoints


tags_metadata = [
  {
    "name": "Books",
    "description": "The description is being worked on..."
  },
]

app = FastAPI(
    debug=True,
    reload=True,
    openapi_tags=tags_metadata,
    title="Book recommender",
    version="1.0.0",
)


app.include_router(
  book_endpoints.app, prefix="/books", tags=['Books'],
)
