import traceback
from openai import OpenAI
from openai import OpenAI, AssistantEventHandler
from flask import Flask,request
import json
import loggerutility as logger 

class EmailReplyAssistant:
    def __init__(self):
        pass

    def Reply_Email_Ai_Assistant(self, openAI_key, assistant_ID, email_content, subject):
        try:
            class EventHandler(AssistantEventHandler):
                def __init__(self):
                    super().__init__()
                    self.delta_values = []

                def on_text_created(self, text):
                    if isinstance(text, str):
                        print(f"\nAssistant: {text}", end="", flush=True)

                def on_text_delta(self, delta, snapshot):
                    self.delta_values.append(delta.value)

                def on_tool_call_created(self, tool_call):
                    print(f"\nAssistant: {tool_call.type}\n", flush=True)

                def on_tool_call_delta(self, delta, snapshot):
                    if delta.type == 'code_interpreter':
                        if delta.code_interpreter.input:
                            print(delta.code_interpreter.input, end="", flush=True)
                        if delta.code_interpreter.outputs:
                            print(f"\n\nOutput >", flush=True)
                            for output in delta.code_interpreter.outputs:
                                if output.type == "logs":
                                    print(output.logs, flush=True)

            openAI_response = ""
            client = OpenAI(api_key=openAI_key)
            thread = client.beta.threads.create()

            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"subject:{subject}\nemail body:{email_content}",
            )

            event_handler = EventHandler()

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant_ID,
                instructions=f"Create a reply for the email received from a customer.\nDo not include any instruction as the output will be directly in a program.",
                event_handler=event_handler,
            ) as stream:
                stream.until_done()

            delta_values = event_handler.delta_values
            openAI_response = ''.join(delta_values)
            logger.log(f"openAI_response:: {type(openAI_response)}")
            logger.log(f"openAI_response:: {openAI_response}")
            return {"status": "Success", "message": openAI_response}

        except Exception as error:
            responseStr = "<br/><br/>" + str(error)
            trace = traceback.format_exc()
            print(f"Exception in process_Email: {responseStr} \n {trace} \n DataType ::: {type(responseStr)}")

    def email_reply_assitant(self):
        try:
            # while True:
            data = request.get_data('jsonData', None)
            data = json.loads(data[9:])
            logger.log(f"jsondata:: {data}")

            openAI_key = data.get("openAI_key")
            assistant_ID = data.get("assistant_ID")
            email_content = data.get("email_content")
            subject = data.get("subject")

            if not all([openAI_key, assistant_ID, email_content, subject]):
                raise ValueError("Missing required email configuration fields.")

            email_response = self.Reply_Email_Ai_Assistant(
                openAI_key=openAI_key,
                assistant_ID=assistant_ID,
                email_content=email_content,
                subject=subject
            )

            logger.log(f"Reply_Email_Ai_Assistant response: {email_response}")
            return email_response

        except Exception as e:
            logger.log(f"Error in Read_Email: {str(e)}")