const connections = [null, null, null, null];
const websockets = [null, null, null, null];

function updateStatus(streamId, message) {
    const statusElement = document.getElementById(`status${streamId}`);
    statusElement.textContent = message;
    
    // Change color based on status
    switch(true) {
        case message.includes('Conectando'):
            statusElement.style.backgroundColor = 'rgba(255, 165, 0, 0.7)'; // Orange
            break;
        case message.includes('Conectado'):
            statusElement.style.backgroundColor = 'rgba(0, 128, 0, 0.7)'; // Green
            break;
        case message.includes('Erro') || message.includes('Desconectado'):
            statusElement.style.backgroundColor = 'rgba(255, 0, 0, 0.7)'; // Red
            break;
        default:
            statusElement.style.backgroundColor = 'rgba(0,0,0,0.5)'; // Default
    }
}

async function connect(streamId) {
    const rtspUrl = document.getElementById(`rtspUrl${streamId}`).value;
    if (!rtspUrl) {
        alert(`Por favor, insira uma URL RTSP válida para o stream ${streamId}`);
        return;
    }
    
    updateStatus(streamId, "Conectando ao servidor...");
    
    // Cria WebSocket connection
    const ws = new WebSocket(`ws://localhost:8080`);
    websockets[streamId - 1] = ws;
    
    ws.onopen = function() {
        updateStatus(streamId, "Conectado ao servidor. Enviando URL RTSP...");
        ws.send(rtspUrl);
    };
    
    ws.onmessage = async function(evt) {
        const data = JSON.parse(evt.data);
        if (data.type === "offer") {
            await handleOffer(streamId, data);
        }
    };
    
    ws.onclose = function() {
        updateStatus(streamId, "Desconectado do servidor");
        if (connections[streamId - 1]) {
            connections[streamId - 1].close();
            connections[streamId - 1] = null;
        }
    };
    
    ws.onerror = function(err) {
        updateStatus(streamId, "Erro na conexão WebSocket");
        console.error(`WebSocket Error (Stream ${streamId}):`, err);
    };
}

async function handleOffer(streamId, offer) {
    updateStatus(streamId, "Recebida oferta SDP. Configurando WebRTC...");
    
    try {
        // Cria peer connection
        const pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
        });
        connections[streamId - 1] = pc;
        
        // Seleciona o vídeo correto
        const remoteVideo = document.getElementById(`remoteVideo${streamId}`);
        
        // Adiciona handlers de eventos
        pc.ontrack = function(event) {
            updateStatus(streamId, "Stream recebido! Reproduzindo vídeo...");
            if (remoteVideo.srcObject !== event.streams[0]) {
                remoteVideo.srcObject = event.streams[0];
            }
        };
        
        pc.onicecandidate = function(event) {
            if (event.candidate === null) {
                // ICE gathering completo, envia descrição completa
                const sdp = pc.localDescription;
                websockets[streamId - 1].send(JSON.stringify(sdp));
            }
        };
        
        pc.onconnectionstatechange = function() {
            updateStatus(streamId, "Estado WebRTC: " + pc.connectionState);
        };
        
        // Define oferta remota
        await pc.setRemoteDescription(offer);
        
        // Cria resposta
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        
        updateStatus(streamId, "Enviando resposta SDP...");
        
    } catch (error) {
        updateStatus(streamId, "Erro ao processar oferta: " + error);
        console.error(`Error handling offer (Stream ${streamId}):`, error);
    }
}