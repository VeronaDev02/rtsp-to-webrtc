# RTSP para WebRTC

Uma aplicação que permite visualizar streams RTSP em navegadores web utilizando tecnologia WebRTC, eliminando a necessidade de plugins especiais ou players dedicados.

## Visão Geral

Este projeto cria uma ponte entre streams RTSP (Real Time Streaming Protocol) e WebRTC (Web Real-Time Communication), permitindo que câmeras de segurança, dispositivos IoT, e outros equipamentos que utilizam RTSP possam ter seus streams visualizados diretamente em navegadores web modernos.

A aplicação consiste em:
- Um servidor Python que recebe conexões de clientes web
- Um cliente web HTML/JavaScript para visualização do stream
- Uma pipeline de conversão que transforma o stream RTSP em WebRTC

## Requisitos

- Python 3.8+
- OpenCV
- aiortc
- websockets
- PyAV

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/rtsp-para-webrtc.git
cd rtsp-para-webrtc
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

Para gerar o arquivo requirements.txt, execute:
```bash
pip freeze > requirements.txt
```

Ou instale manualmente as dependências necessárias:
```bash
pip install opencv-python aiortc websockets av
```

## Uso

### Iniciando o Servidor

Execute o servidor com:

```bash
python main.py --port 8080
```

Por padrão, o servidor usa a porta 8080, mas você pode especificar outra porta com o argumento `--port`.

### Acessando a Interface Web

1. Abra o arquivo `index.html` em um navegador web moderno (Chrome, Firefox, etc.)
2. Insira a URL RTSP no formato: `rtsp://usuario:senha@endereço:porta/caminho`
3. Clique em "Conectar"
4. O stream deve começar a ser exibido no player de vídeo

## Arquitetura

### Componentes Principais

#### `main.py`
O ponto de entrada da aplicação que configura e inicia o servidor WebSocket.

#### `rtsp_connection.py`
Gerencia a conexão com o stream RTSP utilizando OpenCV:
- Estabelece a conexão com o servidor RTSP
- Captura frames do stream
- Gerencia o ciclo de vida da conexão

#### `webrtc_conversion.py`
Realiza a conversão entre RTSP e WebRTC:
- Converte frames do OpenCV para o formato compatível com WebRTC
- Cria e gerencia conexões WebRTC (peer connections)
- Gera ofertas SDP para estabelecer a conexão com o cliente

#### `websocket_server.py`
Implementa o servidor WebSocket que:
- Recebe conexões dos clientes web
- Processa a URL RTSP fornecida pelo cliente
- Estabelece a conexão WebRTC e realiza a negociação SDP
- Gerencia o ciclo de vida das conexões

#### `index.html`
A interface web do cliente que:
- Permite ao usuário inserir a URL RTSP
- Estabelece a conexão WebSocket com o servidor
- Realiza a negociação WebRTC
- Exibe o stream de vídeo usando a API WebRTC do navegador

## Fluxo de Funcionamento

1. O usuário acessa a interface web e fornece uma URL RTSP
2. O cliente web estabelece uma conexão WebSocket com o servidor
3. O servidor recebe a URL RTSP e inicia uma conexão com o stream
4. O servidor converte o stream RTSP para WebRTC e gera uma oferta SDP
5. A oferta SDP é enviada para o cliente web através do WebSocket
6. O cliente web processa a oferta e gera uma resposta SDP
7. A resposta SDP é enviada de volta para o servidor
8. O servidor finaliza a configuração WebRTC e começa a transmitir o stream
9. O navegador exibe o vídeo em tempo real

## Solução de Problemas

### O stream congela periodicamente
- Verifique se o servidor tem recursos suficientes (CPU/RAM)
- Verifique a qualidade da conexão de rede com o dispositivo RTSP
- Considere reduzir a resolução ou taxa de quadros do stream RTSP

### Não é possível se conectar ao stream RTSP
- Verifique se a URL RTSP está correta, incluindo usuário e senha
- Verifique se o dispositivo RTSP está acessível na rede
- Verifique se não há firewalls bloqueando a conexão

### O navegador não mostra o vídeo
- Utilize navegadores modernos como Chrome ou Firefox em suas versões mais recentes
- Verifique se o JavaScript está habilitado
- Verifique os logs do console do navegador para erros