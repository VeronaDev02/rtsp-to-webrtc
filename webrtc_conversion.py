import asyncio
from aiortc import MediaStreamTrack, RTCIceServer, RTCPeerConnection, RTCSessionDescription
# Correção: importar MediaPlayer do submódulo correto
from aiortc.contrib.media import MediaPlayer, MediaBlackhole

import cv2
import numpy as np
import fractions
from av import VideoFrame

class VideoStreamTrack(MediaStreamTrack):
    """
    Uma implementação personalizada de MediaStreamTrack.
    """
    kind = "video"

    def __init__(self, rtsp_connection):
        super().__init__()
        self.rtsp_connection = rtsp_connection
        
    async def recv(self):
        # Captura o frame do RTSP
        frame = self.rtsp_connection.read_frame()
        
        # Converte para formato compatível com aiortc
        # OpenCV usa BGR, precisamos converter para RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Cria um VideoFrame do PyAV
        video_frame = VideoFrame.from_ndarray(frame_rgb, format="rgb24")
        video_frame.pts = 0  # timestamp
        video_frame.time_base = fractions.Fraction(1, 30)  # 30 fps
        
        return video_frame

class WebRTCConversion:
    def __init__(self):
        self.pc = None
        self.rtsp_connection = None

    async def connect(self, rtsp_url):
        from rtsp_connection import RTSPConnection
        
        self.rtsp_connection = RTSPConnection(rtsp_url)
        self.rtsp_connection.connect()
        
        # Criação do peer connection
        self.pc = RTCPeerConnection()
        
        # Adiciona a track de vídeo
        video_track = VideoStreamTrack(self.rtsp_connection)
        self.pc.addTrack(video_track)
        
        print(f"WebRTC conectado e configurado com RTSP: {rtsp_url}")

    async def create_offer(self):
        if not self.pc:
            raise Exception("WebRTC não inicializado. Chame connect() primeiro.")
            
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        return self.pc.localDescription

    async def process_answer(self, answer):
        if not self.pc:
            raise Exception("WebRTC não inicializado. Chame connect() primeiro.")
            
        await self.pc.setRemoteDescription(answer)
        print("Resposta SDP processada com sucesso")

    async def close(self):
        if self.rtsp_connection:
            self.rtsp_connection.close()
            
        if self.pc:
            await self.pc.close()