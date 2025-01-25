from typing import Optional

import sh


def convert(
    infile: str,
    outfile: str,
    delay: Optional[int] = 0,
    duration: Optional[int] = 0,
    opts: Optional[list] = None,
):
    """Convert `infile` to `outfile`.

    For WebM to MP4 conversion, see
        https://blog.addpipe.com/converting-webm-to-mp4-with-ffmpeg/

    """
    args = ["-y"]
    args.extend(["-i", infile])
    if delay:
        args.extend(["-ss", milliseconds_to_duration(delay)])
    if duration:
        args.extend(["-to", milliseconds_to_duration(delay + duration)])
    if delay or duration:
        args.extend(["-c:v", "libx264", "-preset", "slow", "-crf", "18"])
    if opts:
        args.extend(opts)
    args.append(outfile)
    ffmpg(args)


def merge(infiles: [str], outfile: str) -> None:
    args = ["-y"]
    for file in infiles:
        args.extend(["-i", file])
    args.extend(["-c", "copy", outfile])
    ffmpg(args)


def ffmpg(args):
    try:
        sh.ffmpeg(*args)
    except sh.ErrorReturnCode as e:
        raise RuntimeError(
            f"Command {e.full_cmd} exited with {e.exit_code}\n\n{e.stderr.decode()}"
        )


def milliseconds_to_duration(milliseconds):
    minutes, rem = divmod(milliseconds / 1000.0, 60)
    seconds, ms = divmod(1000 * rem, 1000)
    return f"00:{int(minutes):02d}:{int(seconds):02d}.{int(ms)}"
