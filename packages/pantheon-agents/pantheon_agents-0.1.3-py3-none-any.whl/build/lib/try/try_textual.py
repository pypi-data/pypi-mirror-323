from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Button

class ChatApp(App):
    CSS = """ 
    Screen {
        background: black;
    }

    .message-display {
        padding: 1;
        border: solid;
        height: 80%;
        overflow: auto;
    }

    .message-input {
        padding: 1;
        border-top: solid;
    }

    Input {
        width: 80%;
    }

    Button {
        width: 20%;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the layout for the chat interface."""
        yield Vertical(
            Static("Welcome to Textual Chat!", classes="message-display", id="messages"),
            Horizontal(
                Input(placeholder="Type your message here...", id="message_input"),
                Button(label="Send", id="send_button"),
                classes="message-input",
            )
        )

    def on_mount(self) -> None:
        self.messages = self.query_one("#messages", Static)
        self.message_input = self.query_one("#message_input", Input)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_button":
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "message_input":
            self.send_message()

    def send_message(self):
        """Handles sending messages."""
        message = self.message_input.value.strip()
        if message:
            self.messages.update(f"{self.messages.renderable}\nYou: {message}")
            self.message_input.value = ""
            self.messages.scroll_end()

if __name__ == "__main__":
    app = ChatApp()
    app.run()
