import bpy
import google.generativeai as genai
import textwrap

bl_info = {
    "name": "Gemini2Blend",
    "blender": (4, 0),
    "category": "Object",
}

#initializing model
# Set up the model and API key
genai.configure(api_key="YOUR_API_KEY_HERE")
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]
model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Send message to Gemini API
convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["You are a tool being used to assist Blender 3D artists in their daily workflow. Your job is to assist them with any doubts/questions they may have about Blender. Return the answers in SIMPLE TEXT FORM ONLY. do not add formatting, bold, indents, italics, etc."]
  },
  {
    "role": "model",
    "parts": ["Got it. Send your doubts over!"]
  },
])

def _label_multiline(context, text, parent):
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)

    # Split the text by "\n" to handle new lines explicitly
    text_parts = text.split("\n")
    for part in text_parts:
        if part:  # Check if part is not empty
            text_lines = wrapper.wrap(text=part)
            for text_line in text_lines:
                parent.label(text=text_line)
        else:
            parent.label(text="")

class GeminiChatPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Gemini2Blend"
    bl_idname = "OBJECT_PT_gemini_chat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gemini2Blend'

    def draw(self, context):
        layout = self.layout
        layout.ui_units_x = 20
        layout.ui_units_y = 200

        # Text area for user input
        layout.label(text="Enter your message:")
        layout.prop(context.scene, "gemini_message", text="")

        # Button to send message
        layout.operator("object.send_to_gemini", text="Send")

        # Display area for returned message
        layout.label(text="Gemini's response:")
        '''
        response_box = layout.box()
        response_box.ui_units_y = 20
        response_box.scale_x = 1
        response_box.scale_y = 20
        response_box.label(text=context.scene.gemini_response)
        '''
        _label_multiline(
            context=context,
            text=context.scene.gemini_response,
            parent=layout
        )

        layout.separator(factor = 2.0)

        layout.label(text = "Response as text")
        layout.prop(context.scene, "gemini_response", text="")

class SendToGeminiOperator(bpy.types.Operator):
    """Operator to send message to Gemini API and receive response"""
    bl_idname = "object.send_to_gemini"
    bl_label = "Send Message to Gemini"

    def execute(self, context):
        # Get user input message
        user_input = context.scene.gemini_message
        print("User input:", user_input)

        #add user send message here
        convo.send_message(user_input)
        print("Sent message to Gemini API")

        # Display Gemini's response
        context.scene.gemini_response = convo.last.text
        print("Received response:", convo.last.text)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GeminiChatPanel)
    bpy.utils.register_class(SendToGeminiOperator)
    bpy.types.Scene.gemini_message = bpy.props.StringProperty(name="Gemini Message", default="")
    bpy.types.Scene.gemini_response = bpy.props.StringProperty(name="Gemini Response", default="")

def unregister():
    bpy.utils.unregister_class(GeminiChatPanel)
    bpy.utils.unregister_class(SendToGeminiOperator)
    del bpy.types.Scene.gemini_message
    del bpy.types.Scene.gemini_response

if __name__ == "__main__":
    register()
