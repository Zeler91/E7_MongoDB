MONGO_HOST= 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'apitest'
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']
URL_PREFIX="api"

RENDERERS = [
    'eve.render.JSONRenderer',
    # 'eve.render.XMLRenderer'
]

DOMAIN = {
    'posts':{
        'schema': {
            'title': {
                'type': 'string',
                'minlength': 5,
                'maxlength': 32,
                'required': True,
            },
            'user': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 10,
                'required': True,
            },
            'date':{
                'type': 'datetime',
                'required': True,    
            },
            'message': {
                'type': 'list',
            },
            'tags':{
                'type': 'list'
            },
        }

    }
}
