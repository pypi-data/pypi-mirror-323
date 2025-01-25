import pytest
import responses
from dotenv import load_dotenv
from olympiabhub import OlympiaAPI


@pytest.fixture
def api():
    load_dotenv()
    model_name = "test_model"
    return OlympiaAPI(model=model_name)


@pytest.mark.parametrize(
    "method", 
    [
        ("chat_completion", False),
        ("chat_completion_nubonyxia", True),
        ("completion", False),
        ("completion_nubonyxia", True),
        ("embedding", False),
        ("embedding_nubonyxia", True)
    ]
)
@responses.activate
def test_api_methods(api, method):
    method_name, use_proxy = method
    
    # Préparation des données selon la méthode
    if "chat_completion" in method_name:
        data = [{"role": "user", "content": "test message"}]
        endpoint = "v1/chat/completions"
    elif "completion" in method_name:
        data = "test prompt"
        endpoint = "v1/completions"
    else:  # embedding
        data = ["test text1", "test text2"]
        endpoint = "v1/embeddings"

    expected_response = {"response": "test_response"}

    # Ajout de la mock response
    responses.add(
        responses.POST,
        f"https://api.olympia.bhub.cloud/{endpoint}",
        json=expected_response,
        status=200,
    )

    # Appel de la méthode
    result = getattr(api, method_name)(data)
    assert result == expected_response


@pytest.mark.parametrize(
    "method",
    [
        ("chat_completion", "v1/chat/completions"),
        ("chat_completion_nubonyxia", "v1/chat/completions"),
        ("completion", "v1/completions"),
        ("completion_nubonyxia", "v1/completions"),
        ("embedding", "v1/embeddings"),
        ("embedding_nubonyxia", "v1/embeddings"),
    ]
)
@responses.activate
def test_api_methods_failure(api, method):
    method_name, endpoint = method
    
    # Préparation des données selon la méthode
    if "chat_completion" in method_name:
        data = [{"role": "user", "content": "test message"}]
    elif "completion" in method_name:
        data = "test prompt"
    else:  # embedding
        data = ["test text1", "test text2"]

    responses.add(
        responses.POST,
        f"https://api.olympia.bhub.cloud/{endpoint}",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(ValueError):
        getattr(api, method_name)(data)


@pytest.mark.parametrize(
    "method",
    [
        ("get_llm_models", "modeles", False),
        ("get_llm_models_nubonyxia", "modeles", True),
        ("get_embedding_models", "embeddings", False),
        ("get_embedding_models_nubonyxia", "embeddings", True),
    ]
)
@responses.activate
def test_get_models(api, method):
    method_name, endpoint, use_proxy = method
    expected_response = {"modèles": ["model1", "model2"]}

    responses.add(
        responses.GET,
        f"https://api.olympia.bhub.cloud/{endpoint}",
        json=expected_response,
        status=200,
    )

    result = getattr(api, method_name)()
    assert result == expected_response["modèles"]


@pytest.mark.parametrize(
    "method",
    [
        ("get_llm_models", "modeles"),
        ("get_llm_models_nubonyxia", "modeles"),
        ("get_embedding_models", "embeddings"),
        ("get_embedding_models_nubonyxia", "embeddings"),
    ]
)
@responses.activate
def test_get_models_failure(api, method):
    method_name, endpoint = method
    
    responses.add(
        responses.GET,
        f"https://api.olympia.bhub.cloud/{endpoint}",
        json={"error": "test_error"},
        status=400,
    )

    with pytest.raises(ValueError):
        getattr(api, method_name)()
