"""
Specification parser for extracting MM and MD from speification field.
"""
import re
from typing import Optional, Tuple
from decimal import Decimal


class SpecificationParser:
    """Parser for extracting MM (Mesh Size) and MD (Mesh Depth) from specification field."""
    
    # Regex pattern to extract MM and MD from specification
    # Pattern matches: <number>MM-<number>MD (with optional spaces, optional prefix)
    # Handles formats like: "121MM-50MD", "DK20-121mm-50MD", "121mm-50MD"
    PATTERN = r'(?:[A-Z0-9]+-)?(\d+(?:\.\d+)?)\s*[Mm][Mm]\s*-\s*(\d+(?:\.\d+)?)\s*[Mm][Dd]'
    
    @staticmethod
    def parse_specification(speification: Optional[str]) -> Tuple[Optional[Decimal], Optional[Decimal], str]:
        """
        Parse specification field to extract MM, MD, and normalized specification.
        
        Args:
            speification: Raw speification field value (note: model spelling)
            
        Returns:
            Tuple of (mm, md, normalized_specification)
            - mm: Decimal value or None if not found
            - md: Decimal value or None if not found
            - normalized_specification: String like "33MM-300MD" or "Unknown"
        """
        if not speification:
            return None, None, "Unknown"
        
        # Try to match the pattern
        match = re.match(SpecificationParser.PATTERN, speification, re.IGNORECASE)
        
        if match:
            mm_str = match.group(1)
            md_str = match.group(2)
            
            try:
                mm = Decimal(mm_str)
                md = Decimal(md_str)
                normalized = f"{mm_str}MM-{md_str}MD"
                return mm, md, normalized
            except (ValueError, TypeError):
                return None, None, "Unknown"
        
        # If pattern doesn't match, return Unknown
        return None, None, "Unknown"
    
    @staticmethod
    def extract_mm(speification: Optional[str]) -> Optional[Decimal]:
        """
        Extract only MM value from specification.
        
        Args:
            speification: Raw speification field value
            
        Returns:
            MM value as Decimal or None if not found
        """
        mm, _, _ = SpecificationParser.parse_specification(speification)
        return mm
    
    @staticmethod
    def extract_md(speification: Optional[str]) -> Optional[Decimal]:
        """
        Extract only MD value from specification.
        
        Args:
            speification: Raw speification field value
            
        Returns:
            MD value as Decimal or None if not found
        """
        _, md, _ = SpecificationParser.parse_specification(speification)
        return md
    
    @staticmethod
    def get_normalized_specification(speification: Optional[str]) -> str:
        """
        Get normalized specification string (MM-MD format).
        
        Args:
            speification: Raw speification field value
            
        Returns:
            Normalized specification like "33MM-300MD" or "Unknown"
        """
        _, _, normalized = SpecificationParser.parse_specification(speification)
        return normalized
