import asyncio
import json
import logging
import websockets
from aiortc import RTCSessionDescription

class WebSocketServer:
    def __init__(self, port):
        self.port = port
        self.webrtc_conversion = None
        self.active_connections = set()
        
    async def register(self, websocket):
        self.active_connections.add(websocket)
        
    async def unregister(self, websocket):
        self.active_connections.remove(websocket)
        
    # Corrigindo a assinatura do método para versão atual do websockets
    async def websocket_handler(self, websocket):
        await self.register(websocket)
        try:
            # Primeira mensagem deve ser a URL RTSP
            rtsp_url = await websocket.recv()
            print(f"Recebida URL RTSP: {rtsp_url}")
            
            # Instancia e conecta o WebRTC com RTSP
            from webrtc_conversion import WebRTCConversion
            self.webrtc_conversion = WebRTCConversion()
            await self.webrtc_conversion.connect(rtsp_url)
            
            # Cria oferta SDP
            offer = await self.webrtc_conversion.create_offer()
            
            # Envia oferta para o cliente
            print(f"Enviando oferta SDP para o cliente")
            offer_dict = {"sdp": offer.sdp, "type": offer.type}
            await websocket.send(json.dumps(offer_dict))
            
            # Recebe resposta SDP
            answer_json = await websocket.recv()
            answer_dict = json.loads(answer_json)
            answer = RTCSessionDescription(sdp=answer_dict["sdp"], type=answer_dict["type"])
            
            # Processa resposta
            await self.webrtc_conversion.process_answer(answer)
            
            # Mantém a conexão aberta
            while True:
                try:
                    message = await websocket.recv()
                    if message == "CLOSE":
                        break
                except websockets.exceptions.ConnectionClosed:
                    break
                    
        except Exception as e:
            print(f"Erro no handler WebSocket: {e}")
        finally:
            if self.webrtc_conversion:
                await self.webrtc_conversion.close()
            await self.unregister(websocket)

    # Método compatível com versões mais recentes do websockets
    async def start_async(self):
        logging.basicConfig(level=logging.INFO)
        
        # Versão mais recente do websockets já não passa o argumento 'path'
        async with websockets.serve(
            self.websocket_handler, 
            "0.0.0.0",  # Ouve em todas as interfaces
            self.port
        ):
            print(f"Servidor WebSocket iniciado em 0.0.0.0:{self.port}")
            # Mantém o servidor rodando indefinidamente
            await asyncio.Future()  # Aguarda indefinidamente