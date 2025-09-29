// Importa os módulos principais do Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

// Configuração copiada exatamente do seu Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyBrD8e7fzfvhHscwCMhrnriFoRoxDwCC0s",
  authDomain: "dani100.firebaseapp.com",
  projectId: "dani100",
  storageBucket: "dani100.firebasestorage.app", // 🔹 conforme aparece no seu console
  messagingSenderId: "962697367179",
  appId: "1:962697367179:web:200d37dcdc9ef065698e8e",
  measurementId: "G-HW82VXR78V"
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);

// Exporta os serviços
export const auth = getAuth(app);
export const db = getFirestore(app);