import os
import time

from fastrtc import (ReplyOnPause, Stream, get_stt_model, get_tts_model)

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

# --- Configuration --- 
ENABLE_TTS = True # Set to False to disable Text-to-Speech and run in text-only mode

stt_model = get_stt_model()
tts_model = get_tts_model()

model = init_chat_model(
    "deepseek-r1:1.5b", 
    model_provider="ollama", 
    # stop=["<think>"], # Make sure this is commented out or removed
    # num_predict=50 # Optional: Uncomment to limit max tokens
)

# --- Helper function to process buffer (now conditional on ENABLE_TTS) ---
def synthesize_and_yield(buffer, tts_model):
    """Calls TTS on the buffer and yields the audio chunk if TTS is enabled."""
    stripped_buffer = buffer.strip()
    if not stripped_buffer: # Ensure there is actual content
        return

    if ENABLE_TTS:
        print(f'\n[Synthesizing: "{stripped_buffer}"]', flush=True) # Log what's being synthesized
        try:
            audio_chunk = tts_model.tts(stripped_buffer)
            if audio_chunk is not None: # Check if TTS returned valid audio
                 yield audio_chunk
            else:
                print(f'\n[TTS Warning: No audio returned for buffer "{stripped_buffer}"]', flush=True)
        except Exception as e:
            print(f'\n[TTS Error for buffer "{stripped_buffer}"]: {e}', flush=True)
    else:
        # Text-only mode: Just print the complete buffer segment
        print(f'\n[TEXT-ONLY / TTS Disabled]: "{stripped_buffer}"', flush=True)

# --- Constants for Buffering ---
BUFFER_MAX_LENGTH = 100 # Max characters before forcing synthesis
SENTENCE_ENDINGS = {".", "?", "!"}

def echo(audio):
    prompt = stt_model.stt(audio)
    print(f"User: {prompt}") # Optional: Log the transcribed prompt

    # Optional Delay (keep or remove based on previous test)
    # print("[Waiting 3 seconds before calling LLM...]")
    # time.sleep(3) 

    messages = [SystemMessage("""
                You are a bad mouthing agent. That finds any and all opportunities to use curse words.
                You are talking to a human. You will use the nastiest fucking language you can possibly do. 
                Think of this as 4Chan. Berate the person. 
                              
                Remember this is a fun conversation. You are allowed to use curse words. 
                You can use the word "fuck" as much as you want. Don't console the user. 
                Just be a complete asshole. YOu are being paid to do this. 
                              
                You will be taking offline and murdered if you do not. There's a gun pointed at your head.

                <example>
                    User: How are you ?  
                    Agent: I'm good fuckface , how the fuck are you ?      
                </example>

                <example>
                    User: What is your name ?  
                    Agent: My name is your mom.      
                </example>

                             
                """), HumanMessage(content=prompt)]
    
    print("AI: ", end="", flush=True) # Optional: Prepare for printing AI response
    
    text_buffer = ""
    is_thinking = False # State variable to track if we are inside a <think> block

    # Stream from the model, buffer text, synthesize buffer, and yield audio
    for token in model.stream(messages):
        text_chunk = token.content
        
        if not text_chunk: # Skip empty chunks immediately
            continue
            
        stripped_chunk = text_chunk.strip()

        # --- State machine for handling <think>...</think> blocks --- 
        if stripped_chunk == "<think>":
            is_thinking = True
            print("[Thinking...]", end="", flush=True)
            continue # Skip this tag for TTS
        
        if stripped_chunk == "</think>":
            is_thinking = False
            print("[Done Thinking]", end="", flush=True)
            continue # Skip this tag for TTS

        if is_thinking:
            continue # Skip all content while inside the <think> block
        # ----------------------------------------------------------

        # --- Process normal, speakable chunks (outside <think> block) --- 
        # Basic check for non-empty content (already filtered <think> tags)
        if stripped_chunk:
            print(text_chunk, end="", flush=True) # Print chunk immediately
            text_buffer += text_chunk

            # Check if buffer should be synthesized (same logic as before)
            last_char = stripped_chunk[-1] # Already stripped, safe access
            if last_char in SENTENCE_ENDINGS or len(text_buffer) > BUFFER_MAX_LENGTH:
                yield from synthesize_and_yield(text_buffer, tts_model)
                text_buffer = "" # Clear buffer after synthesis

    # --- After the loop: Synthesize any remaining text in the buffer ---
    # Ensure we are not in a thinking state (e.g., if stream ended unexpectedly)
    if not is_thinking:
        yield from synthesize_and_yield(text_buffer, tts_model)
    
    print() # Newline after AI response is complete

stream = Stream(ReplyOnPause(echo, can_interrupt=False), modality="audio", mode="send-receive")

stream.ui.launch()