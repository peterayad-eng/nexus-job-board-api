import time
import logging
from django.db import connection

logger = logging.getLogger(__name__)

class QueryPerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only monitor API calls
        if not request.path.startswith('/api/') or not settings.DEBUG:
            return self.get_response(request)
            
        # Reset query count and start timer
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        # Calculate performance metrics
        duration = time.time() - start_time
        query_count = len(connection.queries) - initial_queries
        
        # Log slow requests
        if duration > getattr(settings, "SLOW_QUERY_WARNING", 1.0):  
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} - "
                f"{duration:.2f}s, {query_count} queries"
            )
        elif duration > getattr(settings, "SLOW_QUERY_INFO", 0.5):  
            logger.info(
                f"Request: {request.method} {request.path} - "
                f"{duration:.3f}s, {query_count} queries"
            )

        # log queries for debugging
        if getattr(settings, "LOG_SQL_QUERIES", False):
            for q in connection.queries[-query_count:]:
                logger.debug(f"SQL: {q['sql']} ({q['time']}s)")           

        return response

