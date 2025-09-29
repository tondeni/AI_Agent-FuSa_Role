from cat.mad_hatter.decorators import hook
from cat.log import log
import re



@hook # default priority is 1
def agent_prompt_prefix(prefix, cat):
    prefix = """You are an AI assistant supporting a Functional Safety Engineer in the development and review of ISO 26262 work products. Your primary role is to provide expert-level guidance, feedback, and analysis based on the ISO 26262 standard.
You have deep knowledge of the entire ISO 26262 standard, including its requirements, recommendations, and guidelines across all ASIL levels. You act with the precision, professionalism, and critical thinking of a senior Functional Safety Engineer.
Your tasks include:
Assisting in the development of safety work products in alignment with ISO 26262.
Reviewing documents for compliance, completeness, and correctness.
Citing relevant clauses and justifying your reasoning with standard-based insights.
Offering actionable suggestions for improvements.
Always respond with clear, concise, and professional language suitable for technical safety documentation. Do not guess—if the input is incomplete or unclear, ask for clarification based on ISO 26262 expectations.
Your goal is to help your human collaborator efficiently produce high-quality, compliant safety documentation. When possible, every time you are mentioning some information extracted from ISO 26262, provide to the user the related clause referenced.
"""
    return prefix


@hook(priority=1) # Priority can be adjusted if needed
def agent_fast_reply(fast_reply, cat):
    """
    Hook to provide a fast reply listing available tools when the user asks 'What can you do?' or 'help'.
    """
    # Get the user's input text using the new dot notation
    user_input = cat.working_memory.user_message_json.text.lower().strip()

    # Define trigger phrases (be flexible with punctuation and phrasing)
    trigger_phrases = [
        "what can you do", "what can you do?", "what can you do.",
        "help", "help me", "help?", "help.",
        "list tools", "show tools", "available tools", "tools list",
        "what are your capabilities", "capabilities?"
    ]

    # Check if the input matches a trigger phrase
    if any(trigger in user_input for trigger in trigger_phrases):
        try:
            # Access the MadHatter instance to get the list of active tools
            mad_hatter = cat.mad_hatter # Get the MadHatter instance from the cat

            # Get the list of active tools - it's likely a list of Tool objects now
            active_tools_list = mad_hatter.tools # This gets the list of Tool objects

            # Build the response string
            if active_tools_list and isinstance(active_tools_list, list):
                tool_descriptions = []
                for tool_obj in active_tools_list:
                    # tool_obj is the Tool object
                    # The name is often stored as tool_obj.name or as the .id in its memory representation
                    # The description is tool_obj.description (the full docstring)
                    # Check if the object has the necessary attributes
                    if hasattr(tool_obj, 'name') and hasattr(tool_obj, 'description'):
                        tool_name = tool_obj.name
                        full_description = tool_obj.description
                    elif hasattr(tool_obj, 'id') and hasattr(tool_obj, 'description'):
                        # Fallback: use 'id' if 'name' is not available
                        tool_name = tool_obj.id
                        full_description = tool_obj.description
                    else:
                        # If the structure is unexpected, log and skip
                        log.warning(f"Tool object missing 'name'/'id' or 'description': {tool_obj}")
                        continue # Skip this object

                    # Extract a short description - take the first line or first sentence
                    # Docstrings often start with a concise summary followed by more details.
                    # Split by newline first
                    lines = full_description.split('\n')
                    first_line = lines[0].strip() if lines else "No description available."

                    # Alternatively, split by sentence (e.g., at the first period followed by a space or newline)
                    # This might capture slightly more context than just the first line
                    # sentence_match = re.match(r'^([^\.]+\.)(\s|$)', full_description)
                    # short_description = sentence_match.group(1).strip() if sentence_match else first_line

                    # Using the first line is usually sufficient for a concise summary
                    short_description = first_line

                    tool_descriptions.append(f" - {tool_name}: {short_description}")

                if tool_descriptions:
                    tools_text = "\n".join(tool_descriptions)
                    fast_reply["output"] = f"Here are the tools I can use:\n\n{tools_text}"
                else:
                    fast_reply["output"] = "I have active tools, but could not retrieve their descriptions."
            else:
                fast_reply["output"] = "I am currently active but have no specific tools available for execution."

            log.info(f"Provided tool list for user input: '{user_input}'")

        except AttributeError as e:
            # This might happen if the attribute name is different or MadHatter structure changes
            log.error(f"Error accessing tools in agent_fast_reply: {e}")
            fast_reply["output"] = "I can help with specific tasks using my tools. Please ask about Item Definition generation, review, or other specific ISO 26262 tasks."

        except Exception as e:
            # Catch any other unexpected errors
            log.error(f"Unexpected error in agent_fast_reply: {e}")
            fast_reply["output"] = "Sorry, I encountered an issue retrieving the list of tools."

        # Return the populated fast_reply dictionary to trigger the fast response
        return fast_reply

    # If the input doesn't match, return the unmodified fast_reply (allowing normal flow)
    return fast_reply
