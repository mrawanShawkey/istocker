from api.app import create_app

app = create_app()
with app.test_client() as client:
    response = client.options(
        '/auth/register',
        headers={
            'Origin': 'https://istocker.vercel.app',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type,authorization'
        }
    )
    print(response.status_code)
    for header, value in response.headers.items():
        if header.lower().startswith('access-control') or header == 'Allow':
            print(f'{header}: {value}')
