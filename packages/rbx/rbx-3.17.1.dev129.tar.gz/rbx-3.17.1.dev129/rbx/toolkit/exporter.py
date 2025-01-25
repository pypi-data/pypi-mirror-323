import logging

from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import Response
from starlette.routing import Route

from . import Options, run

config = Config()
logging.basicConfig(level=config("LOG_LEVEL", default="INFO"))


async def handler(request):
    payload = await request.json()

    filename = None
    name = payload.get("name")
    if name:
        ext = "mp4" if payload["format"] == "video" else "png"
        filename = f"{name}.{ext}"

    await run(
        options=Options(
            url=payload["url"],
            width=payload["width"],
            height=payload["height"],
            format=payload["format"],
            duration=int(payload.get("duration", 0)),
            output=payload.get(
                "output", "s3://474071279654-eu-west-1-dev/creatives/exports/"
            ),
            filename=filename,
        )
    )

    return Response("OK")


def create_app() -> Starlette:
    return Starlette(
        routes=[
            Route("/", endpoint=handler, methods=["POST"]),
        ]
    )
