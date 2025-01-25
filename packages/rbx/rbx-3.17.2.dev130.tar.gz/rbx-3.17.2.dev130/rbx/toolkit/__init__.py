__all__ = ["Options", "run"]

import logging
import shutil
import tempfile
from pathlib import Path
from typing import NamedTuple, Optional

import mutagen

from .aws import upload
from .browser import record, screenshot
from .media import convert, merge
from .web import download

logger = logging.getLogger(__name__)


class Options(NamedTuple):
    url: str
    width: int
    height: int
    format: str
    duration: Optional[int] = 0
    path: Optional[str] = "/tmp"
    output: Optional[str] = "."
    filename: Optional[str] = None


def filename(output, filename):
    if output.startswith("s3://"):
        return "s3://" + str(Path(output[5:]) / filename)

    return str(Path(output) / filename)


def add_audio(filename: str, path: Path) -> None:
    """Add audio stream.

    The source of the audio is extracted from a "source.mp4" video file found in the `path`.
    The video file is first renamed because FFmpeg cannot edit existing files in-place.
    """
    source = str(path / "source.mp4")
    audio = str(path / "audio.mp3")
    convert(infile=source, outfile=audio)

    video = str(path / f"_{filename}")
    shutil.move(path / filename, video)
    merge(infiles=[video, audio], outfile=str(path / filename))


async def capture(filename: str, options: Options, path: Path) -> None:
    recording = await record(
        dirname=str(path),
        duration=1000 * options.duration,
        height=options.height,
        url=options.url,
        width=options.width,
    )

    audio = None
    if recording.source:
        logger.debug(f"Downloading video source from {recording.source}")
        audio = path / "source.mp4"
        download(url=recording.source, filename=str(audio))
        file = mutagen.File(audio)
        if file.info.channels == 0:
            logger.debug("Video source has no audio")
            audio = None

    convert(
        infile=recording.location,
        outfile=str(path / filename),
        delay=recording.delay,
        duration=1000 * options.duration,
        # use highest quality, and place MOOV atom at the beginning
        opts=["-crf", "1", "-movflags", "faststart"],
    )
    if audio:
        logger.info(f"Adding audio from {audio}")
        add_audio(filename=filename, path=path)


async def screengrab(filename: str, options: Options, path: Path) -> None:
    await screenshot(
        filename=str(path / filename),
        height=options.height,
        url=options.url,
        width=options.width,
    )


async def run(options: Options) -> None:
    with tempfile.TemporaryDirectory(dir=options.path) as dirname:
        path = Path(dirname)
        logger.debug(f"Working directory: '{path}'")
        if options.format == "video":
            asset = options.filename or "video.mp4"
            output = filename(options.output, asset)
            if options.duration:
                logger.info(
                    f"Capturing '{options.url}' [{options.width}x{options.height}]"
                    f" for {options.duration}s to '{output}'",
                )
            else:
                logger.info(
                    f"Capturing '{options.url}' [{options.width}x{options.height}] to '{output}'",
                )
            await capture(filename=asset, options=options, path=path)
        else:
            asset = options.filename or "screenshot.png"
            output = filename(options.output, asset)
            logger.info(
                f"Taking screenshot of '{options.url}' [{options.width}x{options.height}]"
                f" to '{output}'"
            )
            await screengrab(filename=asset, options=options, path=path)

        if output.startswith("s3://"):
            upload(str(path / asset), output)
        else:
            shutil.copy(path / asset, output)
