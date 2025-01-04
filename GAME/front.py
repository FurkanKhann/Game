import streamlit as st
import subprocess
import os

# Title and Instructions
st.title("Fighter Jet Game")
st.markdown("""
### Welcome to the Fighter Jet Game!
- Use the arrow keys to move your plane.
- Press **SPACEBAR** to shoot bullets.
- Collect power-ups to enable missile firing.
- Avoid obstacles and stay alive!

Click "Play Game" to start!
""")

# Play button
if st.button("Play Game"):
    st.write("Launching the game... Enjoy!")
    # Path to the game script
    game_script_path = os.path.join(os.getcwd(), "GAME\game2.py")
    if os.path.exists(game_script_path):
        subprocess.Popen(["python", game_script_path])
    else:
        st.error(f"Game script not found at {game_script_path}. Please verify the file path.")
