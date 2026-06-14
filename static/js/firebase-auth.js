import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, sendPasswordResetEmail, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCSImDiU89mjENzWiibYJfs_JvlaSPix70",
    authDomain: "tapeflicker-10701.firebaseapp.com",
    projectId: "tapeflicker-10701",
    storageBucket: "tapeflicker-10701.firebasestorage.app",
    messagingSenderId: "153757319274",
    appId: "1:153757319274:web:4742e659aa75b850900a13",
    measurementId: "G-88FSLN2M1G"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export {
    auth,
    provider,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signInWithPopup,
    sendPasswordResetEmail,
    signOut,
    onAuthStateChanged
};
