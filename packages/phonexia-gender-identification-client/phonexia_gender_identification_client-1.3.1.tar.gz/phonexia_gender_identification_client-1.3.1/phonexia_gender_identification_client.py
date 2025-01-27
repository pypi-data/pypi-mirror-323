import argparse
import logging
from typing import Iterator, Optional

import google.protobuf.duration_pb2
import grpc
import phonexia.grpc.common.core_pb2 as phx_common
import phonexia.grpc.technologies.gender_identification.v1.gender_identification_pb2 as gid
import phonexia.grpc.technologies.gender_identification.v1.gender_identification_pb2_grpc as gid_grpc
import soundfile
import ubjson
from google.protobuf.json_format import MessageToJson
from phonexia.grpc.common.core_pb2 import RawAudioConfig

MAX_BATCH_SIZE = 1024


def time_to_duration(time: float) -> Optional[google.protobuf.duration_pb2.Duration]:
    if time is None:
        return None
    duration = google.protobuf.duration_pb2.Duration()
    duration.seconds = int(time)
    duration.nanos = int((time - duration.seconds) * 1e9)
    return duration


def parse_vp(path: str) -> phx_common.Voiceprint:
    with open(path, mode="rb") as file:
        return phx_common.Voiceprint(content=file.read())


def is_ubjson_file(file_path):
    try:
        with open(file_path, "rb") as f:
            ubjson.load(f)
        return True  # noqa: TRY300
    except Exception:  # noqa: S110
        pass

    try:
        with open(file_path, "rb") as f:
            if f.read(4) == b"VPT ":
                return True
    except Exception:  # noqa: S110
        pass

    return False


def make_vp_batch_request(vp_list: Iterator[str]) -> Iterator[gid.IdentifyRequest]:
    batch_size = 0
    request = gid.IdentifyRequest()
    for vp_file in vp_list:
        if batch_size >= MAX_BATCH_SIZE:
            yield request
            batch_size = 0
            request = gid.IdentifyRequest()
        if vp_file:
            vp = parse_vp(vp_file)
            request.voiceprints.append(vp)
            batch_size += 1
    if len(request.voiceprints):
        yield request


def make_audio_batch_request(
    file: str,
    start: Optional[float],
    end: Optional[float],
    speech_length: Optional[float],
    use_raw_audio: bool,
) -> Iterator[gid.IdentifyRequest]:
    time_range = phx_common.TimeRange(start=time_to_duration(start), end=time_to_duration(end))
    config = gid.IdentifyConfig(speech_length=time_to_duration(speech_length))
    chunk_size = 1024 * 100
    if use_raw_audio:
        with soundfile.SoundFile(file) as r:
            raw_audio_config = RawAudioConfig(
                channels=r.channels,
                sample_rate_hertz=r.samplerate,
                encoding=RawAudioConfig.AudioEncoding.PCM16,
            )
            for data in r.blocks(blocksize=r.samplerate, dtype="int16"):
                yield gid.IdentifyRequest(
                    audio=phx_common.Audio(
                        content=data.flatten().tobytes(),
                        raw_audio_config=raw_audio_config,
                        time_range=time_range,
                    ),
                    config=config,
                )
                time_range = None
                raw_audio_config = None

    else:
        with open(file, mode="rb") as fd:
            while chunk := fd.read(chunk_size):
                yield gid.IdentifyRequest(
                    audio=phx_common.Audio(content=chunk, time_range=time_range), config=config
                )
                time_range = None


def identify_gender(
    file: str,
    channel: grpc.Channel,
    start: Optional[float],
    end: Optional[float],
    speech_length: Optional[float],
    metadata: Optional[list],
    use_raw_audio: bool,
):
    stub = gid_grpc.GenderIdentificationStub(channel)
    if is_ubjson_file(file):
        batch_request = make_vp_batch_request(iter([file]))
    else:
        batch_request = make_audio_batch_request(
            file=file,
            start=start,
            end=end,
            speech_length=speech_length,
            use_raw_audio=use_raw_audio,
        )

    for result in stub.Identify(batch_request, metadata=metadata):
        print(MessageToJson(result, preserving_proto_field_name=True))


def main():
    parser = argparse.ArgumentParser(
        description="Gender Identification gRPC client. Identifies gender from input voiceprint.",
    )
    parser.add_argument(
        "-f", "--file", type=str, help="Voiceprint or audio to identify gender from"
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost:8080",
        help="Server address, default: localhost:8080",
    )
    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="error",
        choices=["critical", "error", "warning", "info", "debug"],
    )
    parser.add_argument(
        "--metadata",
        metavar="key=value",
        nargs="+",
        type=lambda x: tuple(x.split("=")),
        help="Custom client metadata",
    )
    parser.add_argument("--use_ssl", action="store_true", help="Use SSL connection")
    parser.add_argument("--start", type=float, help="Audio start time")
    parser.add_argument("--end", type=float, help="Audio end time")
    parser.add_argument("--speech_length", type=float, help="Maximum amount of speech in seconds")
    parser.add_argument("--use_raw_audio", action="store_true", help="Send a raw audio")
    args = parser.parse_args()

    if not args.file:
        raise ValueError("Parameter --file must not be empty string")

    logging.basicConfig(
        level=args.log_level.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.start is not None and args.start < 0:
        raise ValueError("Parameter 'start' must be a non-negative float.")

    if args.end is not None and args.end <= 0:
        raise ValueError("Parameter 'end' must be a positive float.")

    if args.start is not None and args.end is not None and args.start >= args.end:
        raise ValueError("Parameter 'end' must be larger than 'start'.")

    if args.speech_length is not None and args.speech_length <= 0:
        raise ValueError("Parameter 'speech_length' must be float larger than 0.")

    try:
        logging.info(f"Connecting to {args.host}")
        channel = (
            grpc.secure_channel(target=args.host, credentials=grpc.ssl_channel_credentials())
            if args.use_ssl
            else grpc.insecure_channel(target=args.host)
        )
        identify_gender(
            file=args.file,
            channel=channel,
            metadata=args.metadata,
            start=args.start,
            end=args.end,
            speech_length=args.speech_length,
            use_raw_audio=args.use_raw_audio,
        )

    except grpc.RpcError:
        logging.exception("RPC failed")
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


if __name__ == "__main__":
    main()
