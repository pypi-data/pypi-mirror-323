import gradio as gr
from gradio_neomultimodaltextbox import NeoMultimodalTextbox
from rtmt_configuration import rtmt

example = NeoMultimodalTextbox().example_value()

def identity(i):
    return i

with gr.Blocks() as demo:

    conversation = gr.Chatbot(
        type="messages",
    )
    box1 = NeoMultimodalTextbox(
        file_count="multiple",
        value={"text": "zouzou", "files": [], "audio": ""},
        interactive=True,
        audio_btn=True,
        mode="send-receive",
        modality="audio",
        rtmt=rtmt
    )  # interactive version of your component
    box2 = NeoMultimodalTextbox(
        upload_btn=False, interactive=False, stop_btn=True
    )  # static version of your component

    box1.submit(fn=identity, inputs=box1, outputs=box2)

    box1.start_recording(
        fn=lambda: gr.update(audio_btn=False, stop_audio_btn=True, submit_btn=False),
        outputs=[box1],
    )
    box1.stop_recording(
        fn=lambda: gr.update(audio_btn=True, stop_audio_btn=False, submit_btn=True),
        outputs=[box1],
    )

    box1.stream(
        inputs=[box1], 
        outputs=[box1]
    )

    box1.on_additional_outputs(
        fn=identity,
        outputs=[conversation]
    )


if __name__ == "__main__":
    demo.launch()
