// firebase.js

// Importa os módulos principais do Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

// Configuração copiada exatamente do seu Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyBrD8e7fzfvhHscwCMhrnriFoRoxDwCC0s",
  authDomain: "dani100.firebaseapp.com",
  projectId: "dani100",
  storageBucket: "dani100.firebasestorage.app", // ✅ conforme você me mostrou
  messagingSenderId: "962697367179",
  appId: "1:962697367179:web:200d37dcdc9ef065698e8e",
  measurementId: "G-HW82VXR78V",
  databaseURL: "https://dani100-default-rtdb.firebaseio.com" // 🔹 necessário para o Realtime Database
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);

// Exporta os serviços para uso nos outros arquivos
export const auth = getAuth(app);
export const db = getFirestore(app);
export const rtdb = getDatabase(app);