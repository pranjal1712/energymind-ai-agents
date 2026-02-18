import streamlit as st
import requests
import streamlit.components.v1 as components
from auth import login_user, signup_user, get_current_user_info, get_user_history

import os

# ================= CONFIG =================
# Use environment variable for API URL in deployment
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="EnerGpt",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ================= SPLINE BACKGROUND =================
def add_spline_background():
    # Embed Spline Viewer using HTML component
    # We use a script tag to load the viewer and the <spline-viewer> web component
    spline_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.72/build/spline-viewer.js"></script>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: transparent;
        }
        spline-viewer {
            width: 100%;
            height: 100%;
        }
    </style>
    </head>
    <body>
        <spline-viewer url="https://prod.spline.design/UFjQXJOFaagav2ug/scene.splinecode"></spline-viewer>
    </body>
    </html>
    """
    # Render with a height to ensure it takes space in DOM before CSS moves it
    components.html(spline_html, height=500, scrolling=True)

# Add background immediately
add_spline_background()

import uuid

# ================= SESSION STATE INIT =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
# Session ID for Short-Term Memory
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Pages: 'login', 'signup', 'forgot_password', 'chat', 'profile'
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"


# ================= HELPER FUNCTIONS =================
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

def logout():
    st.session_state.auth_token = None
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.chat_count = 0
    navigate_to("login")

# ================= CUSTOM CSS & JS INJECTION =================
def inject_custom_style():
    st.markdown(f"""
    <style>
    /* Hide Streamlit Default Elements (Footer, Menu, Header) */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stDecoration"] {{display: none;}}
    
    /* Hide specific deployment/github icons */
    .stDeployButton {{display: none;}}
    [data-testid="stToolbar"] {{
        visibility: visible !important;
        background-color: transparent !important;
    }}
    [data-testid="stHeader"] {{
        visibility: visible !important;
        background-color: transparent !important;
    }}
    .viewerBadge_container__1QSob {{display: none !important;}}

    /* FORCE VISIBILITY OF SIDEBAR TOGGLE - Natural Position */
    [data-testid="stSidebarCollapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        z-index: 1000000 !important;
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        width: 44px !important;
        height: 44px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(5px) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        margin-top: 10px !important; 
        margin-left: 10px !important;
    }}
    
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: white !important;
        transform: scale(1.05) !important;
    }}
    
    /* Ensure the icon inside is visible */
    [data-testid="stSidebarCollapsedControl"] svg {{
        fill: white !important;
        stroke: white !important;
        width: 24px !important;
        height: 24px !important;
    }}

    /* =========================================
       FORCE TRANSPARENCY ON ALL STREAMLIT LAYERS
       ========================================= */
    
    /* 1. The main app container */
    .stApp {{
        background-color: transparent !important;
        background-image: none !important;
    }}

    /* Target any iframe that might be the Spline viewer */
    iframe {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 0 !important; /* Move to 0 to be sure it's not behind body */
        border: none !important;
        pointer-events: none !important; /* Allow clicking through to app */
    }}

    /* Ensure app content is above the background */
    .stApp > header {{
        z-index: 1 !important;
    }}
    
    .stApp > div {{
        z-index: 1 !important;
    }}

    /* 2. The main view container (scrolling area) */
    div[data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
        background-image: none !important;
    }}

    /* 3. The block container (where your content lives) */
    div[data-testid="stAppViewBlockContainer"] {{
        background-color: transparent !important;
    }}
    
    /* 4. The inner content block (centering constraint) */
    .block-container {{
        background-color: transparent !important;
        padding-top: 2rem !important; /* Main content padding */
        max-width: 1000px;
    }}

    /* 5. Sidebar transparency & Positioning */
    /* 5. Sidebar transparency & Positioning */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.1) !important; 
        background: rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(1px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 99999 !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* Force text color in sidebar */
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* Move sidebar content up */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        padding-top: 1rem !important;
        gap: 0.5rem !important;
    }}
    
    /* 6. Bottom Container - FORCE TRANSPARENCY */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {{
        background-color: transparent !important;
        background: transparent !important;
        background-image: none !important;
        box-shadow: none !important;
        border: none !important;
    }}
    
    div[data-testid="stChatInputContainer"] {{
        background-color: transparent !important;
    }}
    
    div[data-testid="stChatInput"] {{
        background-color: transparent !important;
    }}
    
    .stChatInput {{
        background-color: transparent !important;
    }}
    
    .stChatInput textarea {{
        background-color: transparent !important;
        color: #eeeeee !important;
        caret-color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 24px !important;
        padding: 14px 20px !important;
        box-shadow: none !important;
    }}
    
    .stChatInput textarea:focus {{
        border-color: rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
    }}

    /* =========================================
       CHAT MESSAGE STYLING
       ========================================= */
    [data-testid="stChatMessage"] {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }}
    
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }}

    /* =========================================
       LOGIN PAGE STYLING (Dark Glassmorphism)
       ========================================= */
    [data-testid="stForm"] {{
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 3rem 2rem !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    [data-testid="stForm"] input {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    [data-testid="stForm"] button {{
        background-color: #ffffff !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stForm"] button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.3) !important;
    }}

    /* =========================================
       RESPONSIVE DESIGN ADAPTERS
       ========================================= */
    @media (max-width: 768px) {{
        .sidebar-title {{
            font-size: 1.5rem !important;
            margin-top: -10px !important;
        }}
        div[data-testid="stAppViewBlockContainer"] {{
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .stChatInput {{
            bottom: 10px !important;
        }}
    }}
    
    @media (min-width: 769px) {{
        .sidebar-title {{
            font-size: 2.2rem !important;
            margin-top: -20px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# Call the function to inject styles
inject_custom_style()

# ================= HEADER BUTTONS CONTAINER =================
# We use a container and style it with CSS class 'header-container'
# But Streamlit CSS injection for specific container is tricky.
# Instead, we just place them at the very top and rely on fixed positioning logic if possible,
# or we just assume they are part of the flow.
# Given the user wants "Login | Signup" top right, using ST columns is standard.
# However, to avoid reload, we MUST use st.button.

place_header = st.container()
with place_header:
    # We will inject a div wrapper for styling via markdown
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    
    # We need to use columns inside this container to layout buttons
    # But we can't easily put st.button inside an HTML div string.
    # So we close the div AFTER the buttons? No, Streamlit renders widgets in order.
    # Alternative: Use columns and just style the columns container.
    pass

# Simplified: Use a standard column layout for header, but use CSS to float it.
# We will create a row of columns.
header_cols = st.columns([1, 4, 1]) # Spacer, Content, Buttons

# BUT, we want it FIXED.
# The previous CSS targeted `.header-container`.
# Let's try to put the buttons in a sidebar or main area?
# The most robust way without "Access Restricted" issue is simple st.sidebar navigation or top bar.
# Let's try to put them in the Sidebar for stability? 
# Title: User requested "ye user profile ko thik karo".
# Login persistence is key.
# Let's put the buttons in the main flow at top, but use st.columns.

# We will use "st.columns" at the very top.
# And we add a CSS class to this specific block of columns if possible?
# We can't easily.
# Let's just put them in the top-right using columns and let them scroll for now to ensure functionality first.
# Fixing functionality > Perfect floating position that breaks session.

# Top Bar - REMOVED (Moved to Sidebar to avoid duplicates)
# col1, col2 = st.columns([6, 1]) ...


# ================= PAGES =================

def login_page():
    st.title("⚡ Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                data = login_user(username, password)
                if data:
                    st.session_state.auth_token = data["access_token"]
                    st.session_state.user = {"username": data["username"]}
                    st.success("Logged in successfully!")
                    navigate_to("chat")
                else:
                    st.error("Invalid username or password")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Account", use_container_width=True):
            navigate_to("signup")
    with col2:
        if st.button("Forgot Password?", use_container_width=True):
            navigate_to("forgot_password")
    
    if st.button("Continue as Guest", use_container_width=True):
        navigate_to("chat")

def signup_page():
    st.title("⚡ Create Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submitted:
            if not username or not email or not password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                result = signup_user(username, email, password)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("Account created! Please login.")
                    navigate_to("login")

    st.markdown("---")
    if st.button("Already have an account? Login", use_container_width=True):
        navigate_to("login")

def forgot_password_page():
    st.title("⚡ Reset Password")
    st.info("Enter your email to receive password reset instructions.")
    
    email = st.text_input("Email Address")
    if st.button("Send Reset Link", use_container_width=True):
        if email:
            st.success(f"If an account exists for {email}, a reset link has been sent.")
        else:
            st.error("Please enter your email.")
            
    if st.button("Back to Login", use_container_width=True):
        navigate_to("login")

def profile_page():
    # Custom CSS for Profile Page
    st.markdown("""
        <style>
            .profile-card {
                background-color: rgba(0, 0, 0, 0.6);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .profile-header {
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 10px;
                color: white;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .profile-email {
                color: rgba(255, 255, 255, 0.7);
                font-size: 1rem;
                margin-bottom: 20px;
            }
            .history-section {
                margin-top: 30px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding-top: 20px;
            }
            .history-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #eeeeee;
            }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.user:
        # Fetch fresh data
        user_info = get_current_user_info(st.session_state.auth_token)
        if user_info:
            st.session_state.user = user_info
            
        username = st.session_state.user.get('username', 'User')
        email = st.session_state.user.get('email', 'No Email')

        # Profile Card
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-header">
                👤 {username}
            </div>
            <div class="profile-email">📧 {email}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # History Section
        st.markdown("""
        <div class="history-section">
            <div class="history-title">📜 Recent Research History</div>
        </div>
        """, unsafe_allow_html=True)

        history = get_user_history(st.session_state.auth_token)
        if history:
            for chat in history:
                with st.expander(f"📅 {chat['timestamp'][:16]} - {chat['query'][:40]}..."):
                    st.markdown(f"**Query:** {chat['query']}")
                    st.markdown("---")
                    st.markdown(f"**Result:**\n{chat['response']}")
        else:
            st.info("No saved research history found.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            logout()
            
    else:
        # Not Logged In State
        st.markdown("""
        <div class="profile-card" style="text-align: center; padding: 40px;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🔒</div>
            <h2 style="color: white; margin-bottom: 10px;">Access Restricted</h2>
            <p style="color: rgba(255,255,255,0.7);">Please log in to view your profile and research history.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Log In", use_container_width=True):
                navigate_to("login")
        with col2:
            if st.button("Sign Up", use_container_width=True):
                navigate_to("signup")

    if st.button("← Back to Chat", use_container_width=True):
        navigate_to("chat")

def chat_page():
    # Chat Logic
    for message in st.session_state.messages:
        avatar = "⚡" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Chat Input Limit Check
    disabled = False
    placeholder = "🔍 Enter an energy research topic..."
    
    if not st.session_state.auth_token:
        if st.session_state.chat_count >= 4:
            disabled = True
            placeholder = "🔒 Chat limit reached. Please Login."
            st.info("You have reached the free chat limit. Please login to continue.")

    prompt = st.chat_input(placeholder, disabled=disabled)

    if prompt:
        if not st.session_state.auth_token:
            st.session_state.chat_count += 1
            
        st.chat_message("user", avatar="🌐").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Research agents are working..."):
            try:
                if st.session_state.auth_token:
                    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                
                # Use session_id as thread_id for short-term memory
                payload = {"query": prompt, "thread_id": st.session_state.session_id}
                
                response = requests.post(
                    f"{API_URL}/research",
                    json=payload,
                    headers=headers
                )


                if response.status_code == 200:
                    data = response.json()
                    result_text = data["result"]
                    
                    final_response = f"""
**Topic:** {data['query']}

{result_text}

---
⚡ *Report generated*
"""
                    with st.chat_message("assistant", avatar="⚡"):
                        st.markdown(final_response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response
                    })
                else:
                    st.error(f"Error: {response.text}")

            except Exception as e:
                st.error(f"Connection Error: {e}")



# ================= SIDEBAR =================
# ================= SIDEBAR =================
def render_sidebar():
    with st.sidebar:
        # Custom Header with larger size and moved up - Using White/Silver gradient to match background text
        st.markdown("""
            <h1 class='sidebar-title' style='text-align: left; margin-bottom: 20px; background: -webkit-linear-gradient(45deg, #ffffff, #a0a0a0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                ⚡ EnerGpt
            </h1>
        """, unsafe_allow_html=True)
        
        # Navigation / Actions
        if st.session_state.auth_token:
            # User wants profile in "three dot" style menu in sidebar
            user_col, menu_col = st.columns([4, 1])
            with user_col:
                st.write(f"**{st.session_state.user.get('username', 'User')}**")
            with menu_col:
                with st.popover("⋮", use_container_width=True):
                    st.write(f"Signed in as **{st.session_state.user.get('username')}**")
                    if st.button("👤 Profile", key="sidebar_profile_btn", use_container_width=True):
                        navigate_to("profile")
                    st.markdown("---")
                    if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                        logout()
        else:
            st.info("Guest Mode (Limit: 4 chats)")
            # Sidebar Login/Signup options as requested
            st.markdown("### Join Us")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Log In", key="sidebar_login", use_container_width=True):
                    navigate_to("login")
            with col2:
                if st.button("Sign Up", key="sidebar_signup", use_container_width=True):
                    navigate_to("signup")

        st.markdown("---")
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_count = 0 
            st.session_state.suggestions = [] 
            st.rerun()

        st.markdown("### History")
        
        # History Display
        if st.session_state.auth_token:
            with st.spinner("Loading history..."):
                try:
                    history = get_user_history(st.session_state.auth_token)
                except:
                    history = []
            
            if history:
                for chat in history:
                    # Truncate query for button label
                    label = (chat['query'][:25] + '..') if len(chat['query']) > 25 else chat['query']
                    # Use timestamp as key to ensure uniqueness
                    if st.button(f"📄 {label}", key=f"hist_{chat.get('timestamp', 'unknown')}", use_container_width=True):
                        # Load this chat
                        st.session_state.messages = [
                            {"role": "user", "content": chat['query']},
                            {"role": "assistant", "content": chat['response']}
                        ]
                        st.session_state.suggestions = [] 
                        st.rerun()
            else:
                st.caption("No history found.")
        else:
            st.caption("Login to save history.")

# ================= PAGES =================
# ... (Login, Signup, Forgot Password, Profile pages remain same) ...

# ...

def chat_page():
    # 1. Render Sidebar (User requested it here)
    render_sidebar()

    # 2. Top-Right Profile Menu - REMOVED per user request to keep sidebar clean
    # The profile menu is now moved to the sidebar.
    
    # 3. Chat Logic
    for message in st.session_state.messages:
        avatar = "⚡" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # 4. Guest Limit Logic & Popup
    limit_reached = False
    if not st.session_state.auth_token:
        if st.session_state.chat_count >= 4:
            limit_reached = True
            
    if limit_reached:
        # Popup / Modal effect
        with st.container():
            st.warning("🔒 **Free limit reached!**")
            st.write("You have used your 4 free chats. Please login to continue researching.")
            if st.button("🚀 Login Now", type="primary", use_container_width=True):
                navigate_to("login")
            st.stop() # Stop execution so they can't chat further

    # 5. Chat Input
    placeholder = "🔍 Enter an energy research topic..."
    prompt = st.chat_input(placeholder, disabled=limit_reached)

    # 6. Suggestions
    # Initialize suggestions state if not exists
    if "suggestions" not in st.session_state:
        st.session_state.suggestions = []

    # Display suggestions if available and no current input (or always at bottom)
    if not limit_reached and not prompt and st.session_state.suggestions:
        st.markdown("###### 💡 Related Questions:")
        cols = st.columns(len(st.session_state.suggestions))
        for i, suggestion in enumerate(st.session_state.suggestions):
            with cols[i]:
                if st.button(suggestion, use_container_width=True):
                    # Set prompt and rerun
                    # We can't set 'prompt' variable directly to trigger the input widget in same run easily without callback
                    # So we process it immediately as if it was input
                    st.session_state.suggestion_clicked = suggestion
                    st.rerun()
    
    # Handle Suggestion Click (on rerun)
    if "suggestion_clicked" in st.session_state and st.session_state.suggestion_clicked:
        prompt = st.session_state.suggestion_clicked
        del st.session_state.suggestion_clicked # Clear it so it doesn't loop
        
    # Process Input
    if prompt:
        # Clear suggestions on new input to avoid stale ones, or keep them? 
        # Better to clear them so they don't persist irrelevantly.
        st.session_state.suggestions = []
        
        # Guest increment
        if not st.session_state.auth_token:
            st.session_state.chat_count += 1
            
        st.chat_message("user", avatar="🌐").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Researching & Generating Suggestions..."):
            try:
                headers = {}
                if st.session_state.auth_token:
                    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
                
                response = requests.post(
                    f"{API_URL}/research",
                    json={"query": prompt},
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()
                    result_text = data["result"]
                    new_suggestions = data.get("suggestions", [])
                    st.session_state.suggestions = new_suggestions
                    
                    final_response = f"""
**Topic:** {data['query']}

{result_text}

---
⚡ *Report generated*
"""
                    with st.chat_message("assistant", avatar="⚡"):
                        st.markdown(final_response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response
                    })
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")

            except Exception as e:
                st.error(f"Connection Error: {e}")

# ================= ROUTING =================
if st.session_state.current_page == "login":
    login_page()
elif st.session_state.current_page == "signup":
    signup_page()
elif st.session_state.current_page == "forgot_password":
    forgot_password_page()
elif st.session_state.current_page == "profile":
    profile_page()
else:
    # render_sidebar() is now called INSIDE chat_page
    chat_page()
