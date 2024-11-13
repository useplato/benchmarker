import json

from openai import OpenAI


def generate_task_prompt(actor_details: dict, openai_client: OpenAI):
    actor_details_str = json.dumps(actor_details)
    prompt = f"""Given the following actor details: {actor_details_str}
    Generate a JSON with 'message' and 'start_url', and nothing else. 
    Don't wrap the result in any other text.
    The start_url should be a valid URL, and should be where the actor is trying to get data from.
    For example, if the actor is a Pinterest Scraper, the start_url should be a Pinterest, or if a start url is available in the actor details example input, use that.
    The message should describe the purpose of the actor, like 'extract data from (site)'.
    Include all data from the example_input in the task prompt."""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=150,
    )

    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        result = {"message": "Error in generating JSON", "start_url": ""}

    return result
