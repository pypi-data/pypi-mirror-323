import datetime
import logging
from typing import NamedTuple, Optional

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class Continue(Exception):
    pass


class Recording(NamedTuple):
    location: str
    delay: Optional[int] = 0
    source: Optional[str] = None


async def record(
    dirname: str, duration: int, height: int, url: str, width: int
) -> Recording:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            args=["--autoplay-policy=no-user-gesture-required"]
        )
        context = await browser.new_context(
            record_video_dir=dirname,
            record_video_size={"width": width, "height": height},
            viewport={"width": width, "height": height},
        )
        page = await context.new_page()
        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(url, wait_until="domcontentloaded")
        start = datetime.datetime.now(datetime.UTC)

        try:
            # Wait for the appropriate events to be seen in the console log.
            # These events are expected to occur within 5 seconds, so we never wait any longer
            # than that.
            has_video = False
            ready = None
            while True:
                async with page.expect_console_message(timeout=0) as msg_info:
                    message = await msg_info.value
                    if message.type == "log":
                        for arg in message.args:
                            line = await arg.json_value()
                            if "/session" in line:
                                ready = datetime.datetime.now(datetime.UTC)
                            elif "action=p0" in line or "action=p10" in line:
                                has_video = True

                if (ready and has_video) or (
                    datetime.datetime.now(datetime.UTC) - start
                ).total_seconds() >= 5:
                    raise Continue

        except Continue:
            checkpoint = datetime.datetime.now(datetime.UTC)
            text = "with" if has_video else "without"
            logger.debug(f"Recording {text} video @ {to_ms(checkpoint - start)}ms")
            src = None

            if has_video:
                video = page.locator("video")
                await video.wait_for(timeout=2000)
                for source in await video.locator("source").all():
                    if await source.get_attribute("type") == "video/mp4":
                        value = await source.get_attribute("src")
                        src, _, _ = value.partition("?")

                # Record until the end of the video, at which point the `video` element will be set
                # as hidden.
                await page.locator("video").first.wait_for(
                    state="hidden", timeout=60000
                )
                checkpoint = datetime.datetime.now(datetime.UTC)
                finished = datetime.datetime.now(datetime.UTC)

                # Continue recording until the required duration.
                checkpoint = datetime.datetime.now(datetime.UTC)
                elapsed = int(1000 * (checkpoint - ready).total_seconds())
                remaining = duration - elapsed
                if remaining > 0:
                    logger.debug(f"{remaining}ms left to record")
                    expression = (
                        "window.recording = 1; setTimeout(() => { window.recording = 0 }, "
                        + str(remaining)
                        + ");"
                    )
                    await page.evaluate(expression)
                    await page.wait_for_function("() => window.recording == 0")
                else:
                    logger.debug("Nothing left to record")

                finished = datetime.datetime.now(datetime.UTC)

            else:
                elapsed = int(1000 * (checkpoint - start).total_seconds())
                remaining = duration - elapsed
                if remaining > 0:
                    logger.debug(f"{remaining}ms left to record")
                    expression = (
                        "window.recording = 1; setTimeout(() => { window.recording = 0 }, "
                        + str(remaining)
                        + ");"
                    )
                    await page.evaluate(expression)
                    await page.wait_for_function("() => window.recording == 0")
                else:
                    logger.debug("Nothing left to record")

                finished = datetime.datetime.now(datetime.UTC)

        logger.debug(f"Finished @ {to_ms(finished - ready)}ms")
        await context.close()
        location = await page.video.path()
        await browser.close()

    # The delay is the lag between the start of the recording session and the time the video
    # started playing.
    delay = to_ms(ready - start)
    logger.debug(f"Recorded with delay of {delay}ms")

    return Recording(delay=delay, location=location, source=src)


async def screenshot(filename: str, height: int, url: str, width: int) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=filename)
        await browser.close()


def to_ms(timedelta: datetime.timedelta) -> int:
    return round(1000 * timedelta.total_seconds())
