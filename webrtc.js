// SIMPLES, FUNCIONAL E COMPATÍVEL COM GITHUB PAGES
let localStream;
let remoteVideo = null;
let localVideo = null;

let pc = new RTCPeerConnection({
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" }
    ]
});

// Detecta se é página live.html ou admin-live.html
if (document.getElementById("remoteVideo")) {
    remoteVideo = document.getElementById("remoteVideo");
} else if (document.getElementById("localVideo")) {
    localVideo = document.getElementById("localVideo");
}

/* ======================
      ADMIN START
======================*/
async function startWebcam() {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    playLocal();
    startBroadcast();
}

async function startScreen() {
    localStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
    playLocal();
    startBroadcast();
}

function playLocal() {
    if (localVideo) {
        localVideo.srcObject = localStream;
    }
}

/* ======================
      WEBRTC LOGIC
======================*/

pc.ontrack = e => {
    if (remoteVideo) {
        remoteVideo.srcObject = e.streams[0];
    }
};

async function startBroadcast() {
    localStream.getTracks().forEach(t => pc.addTrack(t, localStream));

    let offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Enviar offer via servidor público temporário P2P
    fetch("https://instant-websocket.onrender.com/broadcast", {
        method: "POST",
        body: JSON.stringify({ sdp: offer }),
        headers: { "Content-Type": "application/json" }
    });
}

// RECEBER STREAM
fetch("https://instant-websocket.onrender.com/viewer")
    .then(r => r.json())
    .then(async ({ sdp }) => {
        if (!remoteVideo) return;

        await pc.setRemoteDescription(new RTCSessionDescription(sdp));

        let ans = await pc.createAnswer();
        await pc.setLocalDescription(ans);

        fetch("https://instant-websocket.onrender.com/answer", {
            method: "POST",
            body: JSON.stringify({ sdp: ans }),
            headers: { "Content-Type": "application/json" }
        });
    });

function stopLive() {
    if (localStream) {
        localStream.getTracks().forEach(t => t.stop());
    }
    alert("Live encerrada.");
}
