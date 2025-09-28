// firebase.js
import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

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

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);
const db  = getDatabase(app);

export { db };