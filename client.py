import asyncio
from argparse import ArgumentParser

async def send_once(host: str, port: int, text: str, timeout: float = 10.0) -> None:
    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
    writer.write((text + "\n").encode("utf-8"))
    await writer.drain()
    # Optional: ACK lesen (nicht zwingend)
    try:
        _ = await asyncio.wait_for(reader.readline(), timeout=5.0)
    except asyncio.TimeoutError:
        pass
    writer.close()
    with contextlib.suppress(Exception):
        await writer.wait_closed()

async def main():
    parser = ArgumentParser(description="Einfacher Socket-Client")
    parser.add_argument("--host", default="127.0.0.1", help="Server-Host")
    parser.add_argument("--port", type=int, default=9999, help="Server-Port")
    parser.add_argument("--text", required=True, help="Nachrichtentext")
    parser.add_argument("-n", type=int, default=1, help="Anzahl Nachrichten/Clients")
    parser.add_argument("--parallel", type=int, default=100, help="Sendeparallelität (Throttle)")
    args = parser.parse_args()

    sem = asyncio.Semaphore(max(1, args.parallel))

    async def worker(i: int):
        async with sem:
            t = args.text if args.n == 1 else f"{args.text} #{i+1}"
            await send_once(args.host, args.port, t)

    await asyncio.gather(*(worker(i) for i in range(args.n)))

if __name__ == "__main__":
    import contextlib
    asyncio.run(main())
