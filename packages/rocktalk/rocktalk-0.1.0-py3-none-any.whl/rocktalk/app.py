import streamlit as st
import streamlit.components.v1 as stcomponents
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import dotenv
from components.chat import ChatInterface
from components.sidebar import Sidebar
from models.llm import BedrockLLM, LLMInterface
from pydantic import BaseModel
from storage.sqlite_storage import SQLiteChatStorage
from streamlit.commands.page_config import Layout
from streamlit_float import float_init
from streamlit_theme import st_theme
import dotenv
import time


def render_app():
    # Initialize storage in session state
    if "storage" not in st.session_state:
        st.session_state.storage = SQLiteChatStorage(
            db_path="chat_database.db"
        )  # StorageInterface

    # Initialize LLM object in session state
    if "llm" not in st.session_state:
        llm: LLMInterface = BedrockLLM(storage=st.session_state.storage)
        st.session_state.llm = llm

    chat = ChatInterface()
    chat.render()

    sidebar = Sidebar(chat_interface=chat)
    sidebar.render()


# Load environment variables
dotenv.load_dotenv()


class AppConfig(BaseModel):
    page_title: str = "RockTalk"
    page_icon: str = "🪨"
    layout: Layout = "wide"
    db_path: str = "chat_database.db"


# Set page configuration
app_config: AppConfig
if "app_config" not in st.session_state:
    app_config = AppConfig()
    st.session_state.app_config = app_config
else:
    app_config = st.session_state.app_config

st.set_page_config(
    page_title=app_config.page_title,
    page_icon=app_config.page_icon,
    layout=app_config.layout,
)


DEPLOYED = os.getenv("DEPLOYED", "false").lower() == "true"
if DEPLOYED:
    with open("auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    st.session_state.authenticator = stauth.Authenticate(
        "auth.yaml",  # config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

st.session_state.theme = st_theme()

if "stop_chat_stream" not in st.session_state:
    st.session_state.stop_chat_stream = False
if "user_input_default" not in st.session_state:
    st.session_state.user_input_default = None
if "message_copied" not in st.session_state:
    st.session_state.message_copied = 0
if (
    "current_session_id" not in st.session_state
    or st.session_state.current_session_id is None
):
    st.subheader(
        f"{app_config.page_title}: Powered by AWS Bedrock 🪨 + LangChain 🦜️🔗 + Streamlit 👑"
    )
if "next_run_callable" in st.session_state:
    st.session_state.next_run_callable()
    del st.session_state["next_run_callable"]
if "stored_user_input" not in st.session_state:
    st.session_state.stored_user_input = None

st.markdown(
    """
    <style>
        .element-container:has(
            iframe[title="streamlit_js_eval.streamlit_js_eval"]
        ) {
            //height: 0 !important;
            display: none;
        }
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
stcomponents.html(
    """
<script>

function updateButtonHeight(targetKey) {
    const parentDoc = window.parent.document;

    const targetButton = parentDoc.querySelector(targetKey);
    if (!targetButton) {
        console.error('Target button not found');
        return;
    }

    // Check if window width is >= 640px
    const isColumnMode = window.parent.innerWidth >= 640;
    //console.log('Window width:', window.parent.innerWidth, 'Column mode:', isColumnMode);

    if (isColumnMode) {
        // Find the shared horizontal block container
        let horizontalBlock = targetButton.closest('.stHorizontalBlock');
        if (!horizontalBlock) {
            console.error('Horizontal block not found');
            return;
        }

        // Find the chat message within this horizontal block
        let chatMessage = horizontalBlock.querySelector('.stChatMessage');

        // If not found, try one level up
        if (!chatMessage && horizontalBlock.parentElement) {
            horizontalBlock = horizontalBlock.parentElement.closest('.stHorizontalBlock');
            if (horizontalBlock) {
                chatMessage = horizontalBlock.querySelector('.stChatMessage');
            }
        }

        if (!chatMessage) {
            console.error('Related chat message not found in current or parent horizontal block');
            return;
        }

        const computedStyle = window.getComputedStyle(chatMessage);
        const height = computedStyle.height;
        //console.log('Related chat message height:', height);

        // Set gap to 0 for the immediate verticalBlock
        const immediateBlock = targetButton.closest('.stVerticalBlock');
        if (immediateBlock) {
            immediateBlock.style.gap = '0';
        }

        // Make button fill height
        targetButton.style.height = height;
        targetButton.style.boxSizing = 'border-box';
        //console.log('Applied height:', height);
    } else {
        // Reset button height in wrapped mode
        targetButton.style.height = '';
        //console.log('Reset button height (wrapped mode)');

        // Optionally reset gap
        const immediateBlock = targetButton.closest('.stVerticalBlock');
        if (immediateBlock) {
            immediateBlock.style.gap = '';
        }
    }
}

function expandButton(targetKey) {
    try {
        console.log(`expandButton target key '${targetKey}'`);

        // Initial update
        setTimeout(() => updateButtonHeight(targetKey), 1);

        // Add resize listener
        const resizeObserver = new ResizeObserver(entries => {
            updateButtonHeight(targetKey);
        });
        resizeObserver.observe(parentDoc.body);

    } catch (error) {
        console.error('Error occurred:', error.message);
    }
}

function copyFunction(textToCopy) {
    try {
        const parentDoc = window.parent.document;

        console.log("textToCopy:", textToCopy);

        // Try using the parent window's clipboard API first
        if (window.parent.navigator.clipboard) {
            window.parent.navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    console.log('Text copied successfully');
                })
                .catch((err) => {
                    console.error('Clipboard API failed:', err);
                    fallbackCopy(textToCopy, parentDoc);
                });
        } else {
            fallbackCopy(textToCopy, parentDoc);
        }
    } catch (err) {
        console.error('Copy failed:', err);
    }
}

function fallbackCopy(text, parentDoc) {
    try {
        const textarea = parentDoc.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';

        parentDoc.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            parentDoc.execCommand('copy');
            console.log('Text copied using fallback method');
        } catch (execErr) {
            console.error('execCommand failed:', execErr);
        }

        parentDoc.body.removeChild(textarea);
    } catch (err) {
        console.error('Fallback copy failed:', err);

        // Last resort fallback
        try {
            const tempInput = parentDoc.createElement('input');
            tempInput.value = text;
            tempInput.style.position = 'fixed';
            tempInput.style.opacity = '0';

            parentDoc.body.appendChild(tempInput);
            tempInput.select();
            tempInput.setSelectionRange(0, 99999);

            parentDoc.execCommand('copy');
            parentDoc.body.removeChild(tempInput);
            console.log('Text copied using last resort method');
        } catch (finalErr) {
            console.error('All copy methods failed:', finalErr);
        }
    }
}

// For the clipboard API not working on subsequent loads,
// try to reinitialize it each time
function initAndCopy(textToCopy) {
    if (window.parent.navigator.clipboard) {
        // Force clipboard permission check
        window.parent.navigator.permissions.query({name: 'clipboard-write'})
            .then(result => {
                console.log('Clipboard permission:', result.state);
                copyFunction(textToCopy);
            })
            .catch(() => {
                copyFunction(textToCopy);
            });
    } else {
        copyFunction(textToCopy);
    }
}
console.log("js functions loaded");
</script>
""",
    width=0,
    height=0,
)

# Float feature initialization
float_init()

if DEPLOYED:
    if st.session_state.get("authentication_status"):
        render_app()

    else:
        # Authentication check
        try:
            st.session_state.authenticator.login("main", key="Login")
            # print(st.session_state.get("authentication_status"))
            if st.session_state.get("authentication_status") == False:
                st.error("Username/password is incorrect")
                # st.session_state.authentication_status = None
                # st.rerun()
            elif st.session_state.get("authentication_status"):
                name = st.session_state.get("name")
                st.success(f"Welcome {name}!")
                time.sleep(2)
                st.rerun()
            else:
                st.warning("Please enter your username and password")

        except Exception as e:
            st.error(e)

else:
    render_app()
