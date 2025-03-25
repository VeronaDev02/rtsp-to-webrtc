let pc;
let ws;

const connectButton = document.getElementById('connect');
const rtspUrlInput = document.getElementById('rtspUrl');
const statusDiv = document.getElementById('status');
const remoteVideo = document.getElementById('remoteVideo');

connectButton.addEventListener('click', connect);

function updateStatus(message) {
    statusDiv.textContent = message;
}

async function connect() {
    const rtspUrl = rtspUrlInput.value;
    if (!rtspUrl) {
        alert("Por favor, insira uma URL RTSP válida");
        return;
    }
    
    updateStatus("Conectando ao servidor...");
    
    // Cria WebSocket connection
    ws = new WebSocket(`ws://localhost:8080`);
    
    ws.onopen = function() {
        updateStatus("Conectado ao servidor. Enviando URL RTSP...");
        ws.send(rtspUrl);
    };
    
    ws.onmessage = async function(evt) {
        const data = JSON.parse(evt.data);
        if (data.type === "offer") {
            await handleOffer(data);
        }
    };
    
    ws.onclose = function() {
        updateStatus("Desconectado do servidor");
        if (pc) {
            pc.close();
            pc = null;
        }
    };
    
    ws.onerror = function(err) {
        updateStatus("Erro na conexão WebSocket");
        console.error("WebSocket Error:", err);
    };
}

async function handleOffer(offer) {
    updateStatus("Recebida oferta SDP. Configurando WebRTC...");
    
    try {
        // Cria peer connection
        pc = new RTCPeerConnection({
            iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
        });
        
        // Adiciona handlers de eventos
        pc.ontrack = function(event) {
            updateStatus("Stream recebido! Reproduzindo vídeo...");
            if (remoteVideo.srcObject !== event.streams[0]) {
                remoteVideo.srcObject = event.streams[0];
            }
        };
        
        pc.onicecandidate = function(event) {
            if (event.candidate === null) {
                // ICE gathering completo, envia descrição completa
                const sdp = pc.localDescription;
                ws.send(JSON.stringify(sdp));
            }
        };
        
        pc.onconnectionstatechange = function() {
            updateStatus("Estado WebRTC: " + pc.connectionState);
        };
        
        // Define oferta remota
        await pc.setRemoteDescription(offer);
        
        // Cria resposta
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        
        updateStatus("Enviando resposta SDP...");
        
    } catch (error) {
        updateStatus("Erro ao processar oferta: " + error);
        console.error("Error handling offer:", error);
    }
}