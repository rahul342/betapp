from django.http import HttpResponse
from django.utils import simplejson


def jsonify(func):
    def wrap(request, *a, **kw):
        response = None
        try:
            response = func(request, *a, **kw)
            if isinstance(response, dict):
                if 'result' not in response:
                    response['result'] = 'ok'
            elif isinstance(response, str):
                response = dict(html = str, result = 'ok')
            else:
                response = dict(result='error', 'Error in View')
        except KeyboardInterrupt:
            raise
        except Exception, e:
            if hasattr(e, 'message'):
                msg = e.message
            else:
                msg = "Unknown Error"
            
            if hasattr(e, 'code'):
                code = e.code
            else:
                code = -1
            response = dict(result='error', code=code, message=msg)

        json = simplejson.dumps(response)
        return HttpResponse(json, mimetype='application/json')
    return wrap