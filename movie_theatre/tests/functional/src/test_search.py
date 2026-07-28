import pytest


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'Unique Movie For Tests'},
                {'status': 200, 'length': 1}
        ),
        (
                {'query': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_by_exact_title(movies_data, es_write_data, make_get_request, query_data, expected_answer):
    await es_write_data(movies_data)

    status, body = await make_get_request('/api/v1/films/search', query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


@pytest.mark.asyncio
async def test_search_by_word(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {'query': 'Star'}
    )

    assert status == 200
    assert len(body) > 0

    for film in body:
        assert 'Star' in film['title']


@pytest.mark.asyncio
async def test_search_response_schema(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {'query': 'The Star'}
    )

    assert status == 200

    film = body[0]

    assert set(film.keys()) == {
        'uuid',
        'title',
        'imdb_rating'
    }

    assert isinstance(film['uuid'], str)
    assert isinstance(film['title'], str)
    assert isinstance(film['imdb_rating'], (int, float))


@pytest.mark.parametrize(
    'empty_query, expected_answer',
    [
        (
                {},
                {'status': 422, 'detail': 'Field required'}
        ),
        (
                {'query': ''},
                {'status': 422, 'detail': 'String should have at least 1 character'}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_without_query(make_get_request, empty_query, expected_answer):
    status, body = await make_get_request(
        '/api/v1/films/search',
        empty_query
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['detail']


@pytest.mark.parametrize(
    'page_size, expected_answer',
    [
        (
                0,
                {'status': 422, 'detail': 'Input should be greater than or equal to 1'}
        ),
        (
                101,
                {'status': 422, 'detail': 'Input should be less than or equal to 100'}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_page_size_less_than_min(make_get_request, page_size, expected_answer):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': page_size,
        }
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['detail']


@pytest.mark.asyncio
async def test_search_page_number_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_number': 0,
        }
    )

    assert status == 422
    assert body['detail'][0]['msg'] == 'Input should be greater than or equal to 1'


@pytest.mark.asyncio
async def test_search_page_size(movies_data_for_search, es_write_data, make_get_request):
    await es_write_data(movies_data_for_search)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 10,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_search_pagination(movies_data_for_search, es_write_data, make_get_request):
    await es_write_data(movies_data_for_search)

    status, page1 = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 10,
            'page_number': 1,
        }
    )

    status, page2 = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 10,
            'page_number': 2,
        }
    )

    assert status == 200

    assert len(page1) == 10
    assert len(page2) == 10

    page1_ids = {film['uuid'] for film in page1}
    page2_ids = {film['uuid'] for film in page2}

    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_search_last_page(movies_data_for_search, es_write_data, make_get_request, ):
    await es_write_data(movies_data_for_search)

    status, body = await make_get_request(
        '/api/v1/films/search',
        {
            'query': 'The Star',
            'page_size': 50,
            'page_number': 2,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_search_cache(movies_data, es_client, es_write_data, make_get_request):
    await es_write_data(movies_data)

    query = {'query': 'Unique Movie For Tests'}

    status, body1 = await make_get_request(
        '/api/v1/films/search',
        query,
    )

    assert status == 200
    assert len(body1) == 1

    await es_client.indices.delete(index='movies')

    status, body2 = await make_get_request(
        '/api/v1/films/search',
        query,
    )

    assert status == 200

    assert body1 == body2
