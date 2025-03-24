import argparse
import asyncio
from websocket_server import WebSocketServer

async def run_server(port):
    # Inicia o servidor WebSocket
    server = WebSocketServer(port)
    await server.start_async()

def main():
    parser = argparse.ArgumentParser(description='Servidor RTSP para WebRTC')
    parser.add_argument('--port', type=int, default=8080, help='Porta do servidor WebSocket')
    args = parser.parse_args()
    
    try:
        # No Python 3.13, precisamos criar e executar o loop explicitamente
        asyncio.run(run_server(args.port))
    except KeyboardInterrupt:
        print("Servidor finalizado pelo usuário")

if __name__ == "__main__":
    main()