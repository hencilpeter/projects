"""
Product parser for normalizing twine field to product codes.
"""
from typing import Optional


class ProductParser:
    """Parser for extracting and normalizing product codes from twine field."""
    
    @staticmethod
    def normalize_product_code(twine: Optional[str]) -> str:
        """
        Normalize product code from twine field.
        
        Rules:
        - Strip whitespace
        - Convert to uppercase
        - Return 'Unknown' if empty or None
        
        Args:
            twine: Raw twine field value
            
        Returns:
            Normalized product code
        """
        if not twine:
            return "Unknown"
        
        # Strip whitespace and convert to uppercase
        normalized = twine.strip().upper()
        
        # If empty after stripping, return Unknown
        if not normalized:
            return "Unknown"
        
        return normalized
    
    @staticmethod
    def extract_product_code(twine: Optional[str]) -> str:
        """
        Extract product code from potentially complex twine value.
        
        If twine contains additional information (e.g., "DK20 Blue"),
        attempt to extract just the product code part.
        
        Args:
            twine: Raw twine field value
            
        Returns:
            Extracted and normalized product code
        """
        if not twine:
            return "Unknown"
        
        normalized = ProductParser.normalize_product_code(twine)
        
        # If it's already a simple product code (alphanumeric), return as-is
        if normalized.replace(" ", "").isalnum():
            return normalized
        
        # Try to extract the first word/segment as product code
        # This handles cases like "DK20 Blue" -> "DK20"
        parts = normalized.split()
        if parts:
            first_part = parts[0]
            # If first part looks like a product code (alphanumeric)
            if first_part.replace(" ", "").isalnum():
                return first_part
        
        # If no clear separation, return the normalized full value
        return normalized
