import pytest


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
async def test_films_incorrect_page_size(make_get_request, page_size, expected_answer):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_size': page_size,
        }
    )

    assert status == expected_answer['status']
    assert body['detail'][0]['msg'] == expected_answer['detail']


@pytest.mark.asyncio
async def test_films_page_number_less_than_min(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_number': 0,
        }
    )

    assert status == 422
    assert body['detail'][0]['msg'] == 'Input should be greater than or equal to 1'


@pytest.mark.asyncio
async def test_films_invalid_sort_field(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'sort': 'aaaaa',
        }
    )

    assert status == 400
    assert body['detail'] == 'Invalid sort field'


@pytest.mark.asyncio
async def test_films_sort_field_asc(es_write_data, movies_data, make_get_request):
    await es_write_data(movies_data)
    status, body = await make_get_request(
        '/api/v1/films',
        {
            'sort': 'imdb_rating',
        }
    )

    returned = [film["imdb_rating"] for film in body]

    assert returned == sorted(returned)


@pytest.mark.asyncio
async def test_films_list(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    status, body = await make_get_request('/api/v1/films', {})

    assert status == 200
    assert len(body) == 50

    film = body[0]

    assert set(film.keys()) >= {
        "uuid",
        "title",
        "imdb_rating",
    }

    assert isinstance(film["uuid"], str)
    assert isinstance(film["title"], str)
    assert isinstance(film["imdb_rating"], (float, int))

    returned = [film["imdb_rating"] for film in body]

    assert returned == sorted(returned, reverse=True)


@pytest.mark.asyncio
async def test_films_page_size(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, body = await make_get_request(
        '/api/v1/films',
        {
            'page_size': 10,
        }
    )

    assert status == 200
    assert len(body) == 10


@pytest.mark.asyncio
async def test_films_pagination(movies_data, es_write_data, make_get_request):
    await es_write_data(movies_data)

    status, page1 = await make_get_request(
        '/api/v1/films',
        {'page_size': 10, 'page_number': 1}
    )

    status, page2 = await make_get_request(
        '/api/v1/films',
        {'page_size': 10, 'page_number': 2}
    )

    assert status == 200
    assert page1 != page2
    assert len(page1) == 10
    assert len(page2) == 10

    page1_ids = {film['uuid'] for film in page1}
    page2_ids = {film['uuid'] for film in page2}

    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_film_by_id(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    film_id = '13f92c28-baf8-437b-94ab-d891bd835656'

    status, body = await make_get_request(f'/api/v1/films/{film_id}', {})

    assert status == 200
    assert body['uuid'] == film_id
    assert body["title"] == "Unique Movie For Tests"
    assert body["imdb_rating"] == 9.9


@pytest.mark.asyncio
async def test_film_by_id_not_found(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/00000000-0000-0000-0000-000000000000',
        {}
    )

    assert status == 404
    assert body['detail'] == 'Film not found'


@pytest.mark.asyncio
async def test_similar_films(es_write_data, make_get_request, movies_data):
    await es_write_data(movies_data)

    film_id = movies_data[0]['_source']['uuid']

    status, body = await make_get_request(
        f'/api/v1/films/{film_id}/similar',
        {}
    )

    assert status == 200
    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_similar_films_not_found(make_get_request):
    status, body = await make_get_request(
        '/api/v1/films/00000000-0000-0000-0000-000000000000/similar',
        {}
    )

    assert status == 404
    assert body['detail'] == 'Film not found'

@pytest.mark.asyncio
async def test_films_cache(movies_data, es_client, es_write_data, make_get_request, ):
    await es_write_data(movies_data)

    film_id = movies_data[0]['_source']['uuid']

    status, body1 = await make_get_request(
        f'/api/v1/films/{film_id}', {})

    assert status == 200

    await es_client.indices.delete(index='movies')

    status, body2 = await make_get_request(
        f'/api/v1/films/{film_id}', {})

    assert status == 200
    assert body1 == body2
