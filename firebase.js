// firebase.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyBod8YVf5pKWI98m9rRR8axokDkNMlXX-k",
  authDomain: "aviatordaniel100x.firebaseapp.com",
  databaseURL: "https://aviatordaniel100x-default-rtdb.firebaseio.com",
  projectId: "aviatordaniel100x",
  storageBucket: "aviatordaniel100x.firebasestorage.app",
  messagingSenderId: "169015417803",
  appId: "1:169015417803:web:ce4aa4f9b77d5ddb07344e",
  measurementId: "G-EES9SVSV72"
};

// Inicializa Firebase
const app = initializeApp(firebaseConfig);

// Exporta serviços
export const auth = getAuth(app);
export const db = getFirestore(app);
export const rtdb = getDatabase(app);
