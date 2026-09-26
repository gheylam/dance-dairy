from fastapi import FastAPI
from api.stubs import get_classes


def create_app():
    app = FastAPI(title="Klassified")

    @app.get("/api/classes")
    def list_classes():
        return get_classes()

    return app


app = create_app()
