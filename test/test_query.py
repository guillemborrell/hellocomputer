import pytest
from hellocomputer.config import settings
from hellocomputer.models import Chat


@pytest.mark.asyncio
@pytest.mark.skipif(
    settings.anyscale_api_key == "Awesome API", reason="API Key not set"
)
async def test_chat_simple():
    chat = Chat(api_key=settings.anyscale_api_key, temperature=0)
    chat = await chat.eval("Your're a helpful assistant", "Say literlly 'Hello'")
    assert chat.last_response_content() == "Hello!"
