import asyncio
import json
import contextlib
from datetime import datetime
from argparse import ArgumentParser
from pathlib import Path
from datetime import datetime, UTC

MAX_CONCURRENCY = 500
WRITE_LOCK = asyncio.Lock()
SEM = asyncio.Semaphore(MAX_CONCURRENCY)

async def save_record(outfile: Path, record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False)
    async with WRITE_LOCK:
        outfile.parent.mkdir(parents=True, exist_ok=True)
        with outfile.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

async def handle_client(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter,
                        outfile: Path) -> None:
    addr = writer.get_extra_info("peername")
    ip_port = f"{addr[0]}:{addr[1]}" if addr else "unknown"

    async with SEM:
        try:
            data = await asyncio.wait_for(reader.readline(), timeout=15.0)
            if not data:
                # Verbindung ohne Daten beendet
                return
            message = data.decode("utf-8", errors="replace").rstrip("\r\n")

            record = {
                "ts": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
                "addr": ip_port,
                "message": message,
            }
            await save_record(outfile, record)

            writer.write(b"OK\n")
            await writer.drain()

        except asyncio.TimeoutError:
            print(f"[WARN] Timeout von {ip_port}")
        except Exception as e:
            print(f"[ERR ] {ip_port}: {type(e).__name__}: {e}")
        finally:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

async def main():
    parser = ArgumentParser(description="Einfacher Async-Socketserver (JSONL-Storage)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind-Adresse (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9999, help="Port (default: 9999)")
    parser.add_argument("--out", default="messages.jsonl", help="Zieldatei (JSON Lines)")
    args = parser.parse_args()

    outfile = Path(args.out)

    try:
        server = await asyncio.start_server(
            lambda r, w: handle_client(r, w, outfile),
            host=args.host,
            port=args.port,
        )
    except OSError as e:
        print(f"[FATAL] Konnte nicht auf {args.host}:{args.port} binden: {e}")
        print("• Läuft schon ein Prozess auf dem Port?\n"
              "• Windows-Firewall/AV blockiert?\n"
              "• Anderen Port testen: --port 10000")
        return

    addrs = ", ".join(str(sock.getsockname()) for sock in (server.sockets or []))
    print(f"Server läuft auf {addrs} | Speichert nach {outfile} | Max={MAX_CONCURRENCY}")

    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeende Server...")

if __name__ == "__main__":
    asyncio.run(main())
