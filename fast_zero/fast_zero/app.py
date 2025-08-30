from http import HTTPStatus

from fastapi import FastAPI

from .routers import auth, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'A api está rodando, entre em /docs para saber mais'}
