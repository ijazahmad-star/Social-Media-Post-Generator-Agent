import gradio as gr
from agent import generate_social_posts, save_draft

result = {}

def generate_posts_ui(topic):
    yield "<div class='loading'>⏳ Generating creative posts... please wait</div>"
    global result
    result = generate_social_posts(topic)
    posts = result["posts"]
    content = result["content"]
    feedback = result["feedback"]

    html = f"""
    <div class='section'>
      <h3>Topic</h3><p>{topic}</p>
      <h3>Feedback</h3><p>{feedback}</p>
      <h3>Main Content</h3><p>{content}</p>
    </div>
    <div class='card-container'>
      <div class='card linkedin'><h4>LinkedIn Post</h4><p>{posts['LinkedIn']}</p></div>
      <div class='card facebook'><h4>Facebook Post</h4><p>{posts['Facebook']}</p></div>
      <div class='card twitter'><h4>X (Twitter) Post</h4><p>{posts['X']}</p></div>
    </div>
    """
    yield html


def save_to_gmail_ui(topic):
    yield "<div class='loading'>Saving your post to Gmail Draft...</div>"
    # result = generate_social_posts(topic)
    posts = result["posts"]

    html_body = f"""
    <html><body>
    <h2>Social Media Posts: {topic}</h2><hr>
    <h3>LinkedIn</h3><p>{posts['LinkedIn']}</p>
    <h3>Facebook</h3><p>{posts['Facebook']}</p>
    <h3>Twitter (X)</h3><p>{posts['X']}</p>
    </body></html>
    """
    status = save_draft(f"Social Media Posts: {topic}", html_body)
    color = "#16a34a" if "" in status else "#dc2626"
    yield f"<div style='text-align:center;color:{color};font-weight:600'>{status}</div>"


custom_css = """
body {background: linear-gradient(180deg, #f8fafc, #f1f5f9);}
.gradio-container {max-width: 900px !important; margin: auto; font-family: 'Inter', sans-serif;}
#title {text-align: center; font-size: 30px; font-weight: 800; color: #1e293b; margin-top: 15px;}
#subtitle {text-align: center; color: #64748b; font-size: 15px; margin-bottom: 25px;}
#generate {background-color: #2563eb; color: white; font-weight: 600; border-radius: 8px;}
#gmail {background-color: #16a34a; color: white; font-weight: 600; border-radius: 8px;}
.card-container {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 25px;}
.card {padding: 18px; border-radius: 10px; background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s ease-in-out;}
.card:hover {transform: translateY(-4px);}
.linkedin {border-top: 4px solid #0a66c2;}
.facebook {border-top: 4px solid #1877f2;}
.twitter {border-top: 4px solid #1da1f2;}
.loading {text-align: center; font-weight: 600; color: #2563eb; padding: 15px; animation: pulse 1.5s infinite;}
@keyframes pulse {0%{opacity:0.6;}50%{opacity:1;}100%{opacity:0.6;}}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("<div id='title'>Smart Social Post Generator</div>")
    gr.Markdown("<div id='subtitle'>Powered by Gemini + LangGraph + Gmail</div>")
    with gr.Row():
        topic = gr.Textbox(label="Enter Topic", placeholder="e.g. AI startup, product launch, etc.")
    with gr.Row():
        gen_btn = gr.Button("Generate Posts", elem_id="generate")
        gmail_btn = gr.Button("Save to Gmail Draft", elem_id="gmail")
    output = gr.HTML()
    gmail_status = gr.HTML()
    gen_btn.click(generate_posts_ui, inputs=topic, outputs=output)
    gmail_btn.click(save_to_gmail_ui, inputs=topic, outputs=gmail_status)
    gr.Markdown("<p style='text-align:center;color:#94a3b8;font-size:12px;'>Made with by Ijaz + Gemini + LangGraph</p>")

demo.queue().launch()