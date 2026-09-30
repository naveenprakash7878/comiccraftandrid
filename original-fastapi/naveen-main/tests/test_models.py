from app.models import PromptRequest


def test_prompt_request_accepts_valid_payload():

    payload = PromptRequest(

        story_prompt=(
            "A brave fox explores "
            "an enchanted forest."
        ),

        character_name="Fenn",

        setting="Enchanted forest",

        tone="funny",

        art_style="comic book"
    )

    assert payload.character_name == "Fenn"