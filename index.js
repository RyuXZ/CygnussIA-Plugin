const { app, core } = require("photoshop");
const API_BASE = "http://127.0.0.1:8000/api";
const output = document.getElementById("console-output");
const statusIndicator = document.getElementById("status-indicator");

function log(msg) { 
    if (output) output.innerText = msg; 
}

// Validación para evitar errores fuera del entorno de Photoshop
async function checkConnection() {
    try {
        const res = await fetch("http://127.0.0.1:8000/");
        if (statusIndicator) {
            statusIndicator.className = res.ok ? "status online" : "status offline";
        }
    } catch (e) { 
        if (statusIndicator) statusIndicator.className = "status offline"; 
    }
}

// Usamos una variable para controlar el intervalo y evitar duplicados
let connectionInterval = setInterval(checkConnection, 5000);

document.getElementById("btn-generate").addEventListener("click", async () => {
    // Verificamos entorno antes de ejecutar lógica compleja
    if (!app || typeof app.activeDocument === 'undefined') {
        return log("Photoshop no está disponible.");
    }

    const prompt = document.getElementById("text-prompt").value;
    if (!prompt) return log("El prompt está vacío.");

    log("Generando...");
    try {
        const res = await fetch(`${API_BASE}/generate/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt, model: "llama3" })
        });
        const data = await res.json();
        log(data.result || "Sin respuesta");
    } catch (err) { 
        log("Error de conexión"); 
    }
});