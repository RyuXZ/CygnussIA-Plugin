const API_BASE = "http://127.0.0.1:8000";

document.getElementById("btn-ping").addEventListener("click", async () => {
    try {
        const res = await fetch(`${API_BASE}/`);
        const data = await res.json();
        require("photoshop").core.showAlert({ message: `Estado: ${data.status}\n${data.message}` });
    } catch (e) {
        require("photoshop").core.showAlert({ message: "Error: No se pudo contactar al servidor Python." });
    }
});

document.getElementById("btn-restart").addEventListener("click", () => {
    console.log("Señal de reinicio enviada...");
});