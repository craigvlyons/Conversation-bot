import os
import sys
import dotenv
import asyncio
from stt.stt import STT
from Kokoro.KokoroTTS import KokoroTTS
from recording.AutoRecorder import AudioRecorder
from wake_word.wake_word_detector import WakeWordDetector
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

AUDIO_FILE = "C:/convo_bot/recording/audio_out/output.wav"

dotenv.load_dotenv()
ACCESS_KEY = os.getenv("PRORCUPINE_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY") 
# Sensitivity (optional, between 0.0 and 1.0)
SENSITIVITIES = [0.7]
if not GEMINI_KEY:
    print(f"GEMINI_API_KEY not found. {GEMINI_KEY}.")
    print("GEMINI_API_KEY not found. Please set it in your environment variables.")
    sys.exit(1)

# Initialize the Gemini model
model = GeminiModel(model_name="gemini-1.5-flash", api_key=GEMINI_KEY)
agent = Agent(model)

# Function to handle async call
async def get_response(user_input):
    response = await agent.run(user_input)  # Use 'await' directly
    return response.data

def main():
    try:
        auto = AudioRecorder(silence_duration=2.0)
        tts = KokoroTTS()
        stt = STT()
        detector = WakeWordDetector(ACCESS_KEY, sensitivities=SENSITIVITIES)
        detector.initialize()

        def callback():
            tts.synthesize("Hello, how can I help you?", 3)
            tts.play_audio()
            
            auto.record()
            print("Recording complete.")
            speach = stt.transcribe(AUDIO_FILE)
            print(f"User said: {speach}")
            if "Stop listening" in speach:
                tts.synthesize("Goodbye, Talk again soon!", 3)
                tts.play_audio()
                print("Exiting program on user request...")
                detector.cleanup()  # Cleanup detector resources
                sys.exit(0)  # Exit program gracefully

            # Generate a response using the gemini model.
            # Use existing event loop instead of closing and recreating one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            ai_response = loop.run_until_complete(get_response(speach))

            print(f"AI Response: {ai_response}")
            tts.synthesize(ai_response, 3)
            tts.play_audio()

        detector.listen(callback)

    except KeyboardInterrupt:
        print("\nExiting program...")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
