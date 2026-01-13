"""
Pagination utilities for list endpoints
"""
from typing import List, Dict, Any, Optional
from flask import request


class Pagination:
    """
    Pagination helper class
    """
    def __init__(self, items: List, page: int, page_size: int, total: int):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total = total
        self.pages = (total + page_size - 1) // page_size  # Ceiling division
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def prev_page(self) -> Optional[int]:
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_page(self) -> Optional[int]:
        return self.page + 1 if self.has_next else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pagination info to dictionary"""
        return {
            "data": self.items,  # Frontend expects 'data'
            "items": self.items,  # Keep for backward compatibility
            "total": self.total,  # Frontend expects 'total' at top level
            "total_pages": self.pages,  # Frontend expects 'total_pages' at top level
            "page": self.page,
            "page_size": self.page_size,
            "has_prev": self.has_prev,
            "has_next": self.has_next,
            "prev_page": self.prev_page,
            "next_page": self.next_page,
            "pagination": {  # Keep nested for backward compatibility
                "page": self.page,
                "page_size": self.page_size,
                "total_items": self.total,
                "total_pages": self.pages,
                "has_prev": self.has_prev,
                "has_next": self.has_next,
                "prev_page": self.prev_page,
                "next_page": self.next_page
            }
        }


def get_pagination_params(default_page_size: int = 20, max_page_size: int = 100) -> tuple:
    """
    Extract pagination parameters from request
    
    Args:
        default_page_size: Default number of items per page
        max_page_size: Maximum allowed page size
    
    Returns:
        Tuple of (page, page_size, offset)
    """
    page = request.args.get('page', 1, type=int)
    # Support both 'page_size' and 'limit' as aliases
    page_size = request.args.get('page_size', type=int) or request.args.get('limit', type=int) or default_page_size
    
    # Validate parameters
    page = max(1, page)  # Page must be at least 1
    page_size = min(max(1, page_size), max_page_size)  # Between 1 and max
    
    offset = (page - 1) * page_size
    
    return page, page_size, offset


def paginate(query, page: int, page_size: int, schema=None) -> Dict[str, Any]:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Items per page
        schema: Optional Marshmallow schema for serialization
    
    Returns:
        Dictionary with items and pagination info
    """
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    # Serialize if schema provided
    if schema:
        items = schema.dump(items, many=True)
    
    pagination = Pagination(items, page, page_size, total)
    return pagination.to_dict()
