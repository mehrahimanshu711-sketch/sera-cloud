from flask import Flask, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sera AI</title>
</head>
<body>
    <div id="status">Sera ready hai</div>
    <div id="output"></div>

    <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-IN';
        recognition.continuous = true;

        window.onload = function() {
            try {
                document.getElementById("status").innerText = "Sera sun rahi hai (Active)...";
                recognition.start();
            } catch (e) {}
        };

        recognition.onend = function() {
            try {
                recognition.start();
            } catch (e) {}
        };

        recognition.onresult = async function(event) {
            const current = event.resultIndex;
            const text = event.results[current][0].transcript;
            
            document.getElementById("status").innerText = "Aapne kaha: " + text;
            document.getElementById("output").innerText = "Soch rahi hoon...";
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await response.json();
                document.getElementById("output").innerText = data.reply;
                document.getElementById("status").innerText = "Sera sun rahi hai...";

                let speech = new SpeechSynthesisUtterance(data.reply);
                speech.lang = 'hi-IN';
                window.speechSynthesis.speak(speech);
            } catch (err) {
                document.getElementById("output").innerText = "Connection error ho gaya!";
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
