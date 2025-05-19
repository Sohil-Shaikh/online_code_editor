import json
import logging
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

class JSONResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Log the request details
            logger.debug(f"Processing request: {request.method} {request.path}")
            logger.debug(f"Request headers: {dict(request.headers)}")
            
            response = self.get_response(request)
            
            # Log the response details
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Check if this is an AJAX request or JSON request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            is_json_request = request.headers.get('Accept', '').find('application/json') != -1
            
            # If this is an AJAX request or JSON request, ensure JSON response
            if is_ajax or is_json_request:
                # If the response is already a JsonResponse, return it as is
                if isinstance(response, JsonResponse):
                    return response
                
                # For 404 responses, return a proper JSON error
                if response.status_code == 404:
                    return JsonResponse({
                        'error': 'File not found',
                        'path': request.path
                    }, status=404)
                
                # If the response is an HttpResponse with content, try to parse it as JSON
                if isinstance(response, HttpResponse) and response.content:
                    try:
                        # Try to decode the content
                        content = response.content.decode('utf-8')
                        logger.debug(f"Response content: {content[:200]}...")
                        
                        # Try to parse as JSON
                        try:
                            json_data = json.loads(content)
                            logger.debug("Successfully parsed response as JSON")
                            return JsonResponse(json_data, status=response.status_code, encoder=DjangoJSONEncoder)
                        except json.JSONDecodeError:
                            logger.warning("Response content is not valid JSON")
                            # If it's not JSON, return a proper error response
                            return JsonResponse({
                                'error': 'Invalid JSON response',
                                'content': content[:200] + '...' if len(content) > 200 else content
                            }, status=500)
                            
                    except UnicodeDecodeError:
                        logger.error("Failed to decode response content as UTF-8")
                        return JsonResponse({
                            'error': 'Response content is not valid UTF-8',
                            'content_type': response.get('Content-Type', 'unknown')
                        }, status=500)
                        
                # For any other response type, return a proper error response
                return JsonResponse({
                    'error': 'Unexpected response type',
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', 'unknown')
                }, status=500)
            
            # For non-AJAX requests, return the original response
            return response
            
        except Exception as e:
            logger.error(f"Error in JSONResponseMiddleware: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'Internal server error',
                'details': str(e)
            }, status=500) 