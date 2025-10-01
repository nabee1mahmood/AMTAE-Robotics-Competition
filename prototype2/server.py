from flask import Flask, jsonify
import subprocess, psutil, atexit

app = Flask(__name__)

RUN_SCRIPT = "/home/x/prototype/start.sh"
STOP_SCRIPT = "/home/x/prototype/stop.sh"

def is_robot_running():
    """Check if udp.py or controller.py are alive"""
    for proc in psutil.process_iter(attrs=["cmdline"]):
        try:
            cmd = " ".join(proc.info["cmdline"])
            if "udp.py" in cmd or "controller.py" in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def cleanup():
    if is_robot_running():
        subprocess.call([STOP_SCRIPT])

atexit.register(cleanup)

@app.route("/toggle", methods=["POST"])
def toggle_robot():
    if is_robot_running():
        subprocess.call([STOP_SCRIPT])  # stop and wait
        return jsonify({"status": "stopped"}), 200
    else:
        subprocess.Popen([RUN_SCRIPT])  # start in background
        return jsonify({"status": "started"}), 200

@app.route("/stats")
def stats():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = round(int(f.read()) / 1000, 1)
    except FileNotFoundError:
        temp = "N/A"

    return jsonify({
        "cpu": cpu,
        "memory": mem,
        "disk": disk,
        "temp": temp,
        "robot_running": is_robot_running()
    })

@app.route("/")
def index():
    return """
    <button id="toggle-btn" onclick="toggleRobot()">▶️ Start</button>

    <div id="stats" style="margin-top:30px; font-size:1.5rem;"></div>

    <style>
      body { font-family: sans-serif; text-align: center; margin-top: 50px; }
      button {
        font-size: 2rem;
        padding: 20px 40px;
        border-radius: 12px;
        border: none;
        background: #4CAF50;
        color: white;
        width: 80%;
        max-width: 400px;
        margin: 20px auto;
        display: block;
      }
      button.stop { background: #e53935; }
    </style>

    <script>
    let running = false;
    function toggleRobot() {
        fetch('/toggle', {method:'POST'})
          .then(r => r.json())
          .then(data => {
              running = data.status === "started";
              const btn = document.getElementById("toggle-btn");
              btn.innerText = running ? "🛑 Stop" : "▶️ Start";
              btn.className = running ? "stop" : "";
          });
    }

    function getEmojiTemp(temp) {
        if (temp === "N/A") return "❓";
        if (temp < 50) return "🟢";
        if (temp < 70) return "🟡";
        return "🔴";
    }

    function getEmojiCPU(cpu) {
        if (cpu < 40) return "🟢";
        if (cpu < 70) return "🟡";
        return "🔴";
    }

    function updateStats() {
        fetch('/stats')
          .then(r => r.json())
          .then(s => {
              running = s.robot_running;
              const btn = document.getElementById("toggle-btn");
              btn.innerText = running ? "🛑 Stop" : "▶️ Start";
              btn.className = running ? "stop" : "";

              document.getElementById("stats").innerHTML =
                `CPU: ${s.cpu}% ${getEmojiCPU(s.cpu)}<br>
                 RAM: ${s.memory}% 💾<br>
                 Disk: ${s.disk}% 💽<br>
                 Temp: ${s.temp}°C ${getEmojiTemp(s.temp)}`;
          });
    }
    setInterval(updateStats, 2000);
    updateStats();
    </script>
    """

if __name__ == "__main__":
    print("🚀 Flask server running on port 8080")
    app.run(host="0.0.0.0", port=8080)
