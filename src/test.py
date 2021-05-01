#print(buildgql('query', 'ValidateUsername', { 'username': 'test' }, [ 'isValid', 'message' ]))
#login = buildgql('query', 'Login', { 'username': 'test', 'password': '1234' })
#res = requests.post('https://localhost:9000/graphql', json={ 'query': login })
#print(json.dumps(res.json()))

#proxies={'https': 'http://127.0.0.1:9000/graphql'}