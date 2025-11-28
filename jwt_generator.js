import fs from "fs";
import jwt from "jsonwebtoken";

// Leia sua chave privada LOCAL
const privateKey = fs.readFileSync("./private.pem", "utf8");

// Seu APP ID Jitsi
const appId = "vpaas-magic-cookie-bea217d68a5746d6b367f99361c20750";

export function gerarToken(email) {
    const payload = {
        aud: "jitsi",
        iss: appId,
        sub: appId,
        room: "live_do_milhao",
        exp: Math.floor(Date.now() / 1000) + 60 * 60, // 1 hora
        context: {
            user: { name: email, email: email }
        }
    };

    return jwt.sign(payload, privateKey, { algorithm: "RS256" });
}

console.log("TOKEN:", gerarToken("user@vip.com"));
