from src.services.oauth.yandex_service import YandexOAuthProvider

providers = {
    YandexOAuthProvider.PROVIDER_NAME: YandexOAuthProvider(),
}


def get_oauth_provider(name: str):
    provider = providers.get(name)

    if provider is None:
        raise ValueError(f"Unknown provider: {name}")

    return provider
