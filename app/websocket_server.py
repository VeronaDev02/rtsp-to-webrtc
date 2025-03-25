import asyncio
import json
import logging
import websockets
from aiortc import RTCSessionDescription
from typing import Dict
from webrtc_conversion import WebRTCConversion

class WebSocketServer:
    def __init__(self, port):
        self.port = port
        self.active_connections = set()
        self.webrtc_conversions: Dict[str, WebRTCConversion] = {}
        
    async def register(self, websocket):
        self.active_connections.add(websocket)
        
    async def unregister(self, websocket):
        self.active_connections.remove(websocket)
        
    async def cleanup_conversion(self, rtsp_url):
        """Remove a conversão WebRTC quando não estiver mais em uso"""
        if rtsp_url in self.webrtc_conversions:
            conversion = self.webrtc_conversions[rtsp_url]
            await conversion.close()
            del self.webrtc_conversions[rtsp_url]
        
    async def get_or_create_webrtc_conversion(self, rtsp_url):
        """Obtém uma conversão existente ou cria uma nova"""
        if rtsp_url not in self.webrtc_conversions:
            conversion = WebRTCConversion()
            await conversion.connect(rtsp_url)
            self.webrtc_conversions[rtsp_url] = conversion
        return self.webrtc_conversions[rtsp_url]

    async def websocket_handler(self, websocket):
        await self.register(websocket)
        try:
            # Primeira mensagem deve ser a URL RTSP
            rtsp_url = await websocket.recv()
            print(f"Recebida URL RTSP: {rtsp_url}")
            
            # Obtém ou cria conversão WebRTC
            webrtc_conversion = await self.get_or_create_webrtc_conversion(rtsp_url)
            
            # Cria oferta SDP
            offer = await webrtc_conversion.create_offer()
            
            # Envia oferta para o cliente
            print(f"Enviando oferta SDP para o cliente")
            offer_dict = {"sdp": offer.sdp, "type": offer.type}
            await websocket.send(json.dumps(offer_dict))
            
            # Recebe resposta SDP
            answer_json = await websocket.recv()
            answer_dict = json.loads(answer_json)
            answer = RTCSessionDescription(sdp=answer_dict["sdp"], type=answer_dict["type"])
            
            # Processa resposta
            await webrtc_conversion.process_answer(answer)
            
            # Mantém a conexão aberta
            while True:
                try:
                    message = await websocket.recv()
                    if message == "CLOSE":
                        await self.cleanup_conversion(rtsp_url)
                        break
                except websockets.exceptions.ConnectionClosed:
                    await self.cleanup_conversion(rtsp_url)
                    break
                    
        except Exception as e:
            print(f"Erro no handler WebSocket: {e}")
        finally:
            await self.unregister(websocket)

    async def start_async(self):
        logging.basicConfig(level=logging.INFO)
        
        async with websockets.serve(
            self.websocket_handler, 
            "0.0.0.0",  
            self.port
        ):
            print(f"Servidor WebSocket iniciado em 0.0.0.0:{self.port}")
            await asyncio.Future()