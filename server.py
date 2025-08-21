import asyncio
import json
from datetime import datetime
from argparse import ArgumentParser
from pathlib import Path

# Maximal gleichzeitige Verbindungen/Nachrichten
MAX_CONCURRENCY = 500

# Globale Synchronisationsobjekte
WRITE_LOCK = asyncio.Lock()
SEM = asyncio.Semaphore(MAX_CONCURRENCY)

async def save_record(outfile: Path, record: dict) -> None:
    """Append-sicher in JSONL-Datei schreiben (eine Zeile pro Nachricht)."""
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

    async with SEM:  # begrenzt die gleichzeitigen Handler auf 500
        try:
            # Eine Zeile lesen (bis \n), mit Timeout
            data = await asyncio.wait_for(reader.readline(), timeout=15.0)
        except asyncio.TimeoutError:
            writer.close()
            try:
                await writer.wait_closed()
            finally:
                return

        message = data.decode("utf-8", errors="replace").rstrip("\r\n")
        record = {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "addr": ip_port,
            "message": message,
        }
        await save_record(outfile, record)

        # optionales ACK
        try:
            writer.write(b"OK\n")
            await writer.drain()
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
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, outfile),
        host=args.host,
        port=args.port,
    )

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"Server läuft auf {addrs} | Speichert nach {outfile} | Max={MAX_CONCURRENCY}")

    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeende Server...")

if __name__ == "__main__":
    import contextlib
    asyncio.run(main())
