from flask import Flask, request, send_file
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator

# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

try:
    print("Tokenizer loaded")
    # llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-70B")
    llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
    print("Loading model")
    # llama_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-70B")
    llama_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
    print("Model loaded")
except Exception as e:
    print("Error loading model:", e)

app = Flask(__name__)
google_translator = Translator()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['file']
        filename = file.filename
        file.save(filename)

        # Extract audio from video
        video = mp.VideoFileClip(filename)
        audio = video.audio
        audio.write_audiofile('audio.wav')

        # Convert audio to text
        r = sr.Recognizer()
        with sr.AudioFile('audio.wav') as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language=request.form['original_language'])
            # print("text : " + text + ", request.form['translation_language'] : " + request.form['translation_language'])

        # Translate text
        if request.form['model'] == 'google':
            translated_text = google_translator.translate(text, dest=request.form['translation_language']).text
        elif request.form['model'] == 'llama':
            inputs = llama_tokenizer.encode_plus(
                text,
                add_special_tokens=True,
                max_length=512,
                return_attention_mask=True,
                return_tensors='pt'
            )
            outputs = llama_model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
            translated_text = llama_tokenizer.decode(outputs[0].argmax(-1), skip_special_tokens=True)

        # Save translated text to file
        with open('translated.txt', 'w', encoding='utf-8') as f:
            f.write(f"[Original] : {text}\n[Translated] : {translated_text}")

        # Send translated file for download
        return send_file('translated.txt', as_attachment=True)

    return '''
        <html>
            <body>
                <h1>Video Translation</h1>
                <form action="" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".mp4">
                    <br>
                    <label for="model">Model:</label>
                    <select id="model" name="model">
                        <option value="google">Google</option>
                        <option value="llama">LLaMA</option>
                    </select>
                    <br>
                    <label for="original_language">Original Language:</label>
                    <select id="original_language" name="original_language">
                        <option value="ko">Korean</option>
                        <option value="en">English</option>
                    </select>
                    <br>
                    <label for="translation_language">Translation Language:</label>
                    <select id="translation_language" name="translation_language">
                        <option value="ko">Korean</option>
                        <option value="en">English</option>
                    </select>
                    <br>
                    <input type="submit" value="Upload and Translate">
                </form>
            </body>
        </html>
    '''


if __name__ == '__main__':
    print("start main")
    app.run(port=5005, debug=True)
