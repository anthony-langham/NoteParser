"""
Comprehensive error handling utilities for the MCP server.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from functools import wraps


class ErrorCode(Enum):
    """Standard error codes for the application."""
    
    # Data loading errors
    DATA_FILE_NOT_FOUND = "DATA_FILE_NOT_FOUND"
    DATA_FILE_INVALID_JSON = "DATA_FILE_INVALID_JSON"
    DATA_FILE_CORRUPTED = "DATA_FILE_CORRUPTED"
    
    # Validation errors
    INVALID_PATIENT_DATA = "INVALID_PATIENT_DATA"
    INVALID_MEDICATION_DATA = "INVALID_MEDICATION_DATA"
    INVALID_CONDITION_DATA = "INVALID_CONDITION_DATA"
    INVALID_DOSE_CALCULATION = "INVALID_DOSE_CALCULATION"
    
    # Business logic errors
    CONDITION_NOT_FOUND = "CONDITION_NOT_FOUND"
    MEDICATION_NOT_FOUND = "MEDICATION_NOT_FOUND"
    GUIDELINE_NOT_FOUND = "GUIDELINE_NOT_FOUND"
    INSUFFICIENT_PATIENT_DATA = "INSUFFICIENT_PATIENT_DATA"
    
    # Processing errors
    PARSING_ERROR = "PARSING_ERROR"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    TREATMENT_PLAN_ERROR = "TREATMENT_PLAN_ERROR"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # MCP specific errors
    MCP_TOOL_ERROR = "MCP_TOOL_ERROR"
    MCP_INVALID_ARGUMENTS = "MCP_INVALID_ARGUMENTS"


@dataclass
class ErrorDetails:
    """Detailed error information."""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    recoverable: bool = True
    user_friendly_message: Optional[str] = None


class ClinicalError(Exception):
    """Base exception for clinical decision support errors."""
    
    def __init__(self, error_details: ErrorDetails):
        self.error_details = error_details
        super().__init__(error_details.message)


class DataError(ClinicalError):
    """Errors related to data loading and access."""
    pass


class ValidationError(ClinicalError):
    """Errors related to data validation."""
    pass


class BusinessLogicError(ClinicalError):
    """Errors related to business logic."""
    pass


class ProcessingError(ClinicalError):
    """Errors related to data processing."""
    pass


class MCPError(ClinicalError):
    """Errors related to MCP operations."""
    pass


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.error_mappings = self._setup_error_mappings()
    
    def _setup_error_mappings(self) -> Dict[ErrorCode, Dict[str, Any]]:
        """Setup error code mappings with user-friendly messages."""
        return {
            ErrorCode.DATA_FILE_NOT_FOUND: {
                "user_message": "Clinical data is temporarily unavailable. Please try again later.",
                "suggestions": ["Check if data files exist", "Verify file permissions"],
                "recoverable": False
            },
            ErrorCode.DATA_FILE_INVALID_JSON: {
                "user_message": "Clinical data format is invalid. Please contact support.",
                "suggestions": ["Validate JSON format", "Check file encoding"],
                "recoverable": False
            },
            ErrorCode.CONDITION_NOT_FOUND: {
                "user_message": "The specified condition is not recognized in our database.",
                "suggestions": ["Check condition spelling", "Use standard medical terms"],
                "recoverable": True
            },
            ErrorCode.MEDICATION_NOT_FOUND: {
                "user_message": "The specified medication is not available for this condition.",
                "suggestions": ["Check medication spelling", "Consider alternative medications"],
                "recoverable": True
            },
            ErrorCode.INVALID_PATIENT_DATA: {
                "user_message": "Patient information is incomplete or invalid.",
                "suggestions": ["Check age is between 0-150", "Check weight is positive", "Verify required fields"],
                "recoverable": True
            },
            ErrorCode.INSUFFICIENT_PATIENT_DATA: {
                "user_message": "Insufficient patient data to generate recommendations.",
                "suggestions": ["Provide patient age", "Provide patient weight", "Include clinical symptoms"],
                "recoverable": True
            },
            ErrorCode.INVALID_DOSE_CALCULATION: {
                "user_message": "Unable to calculate safe medication dose.",
                "suggestions": ["Verify patient weight", "Check medication dosing limits"],
                "recoverable": True
            },
            ErrorCode.PARSING_ERROR: {
                "user_message": "Unable to process the clinical note format.",
                "suggestions": ["Check note format", "Ensure all sections are present"],
                "recoverable": True
            },
            ErrorCode.INTERNAL_SERVER_ERROR: {
                "user_message": "An internal error occurred. Please try again.",
                "suggestions": ["Retry the request", "Contact support if persists"],
                "recoverable": True
            }
        }
    
    def create_error_response(self, error: ClinicalError) -> Dict[str, Any]:
        """Create standardized error response."""
        error_mapping = self.error_mappings.get(error.error_details.code, {})
        
        response = {
            "success": False,
            "error": {
                "code": error.error_details.code.value,
                "message": error.error_details.message,
                "user_message": error.error_details.user_friendly_message or error_mapping.get("user_message"),
                "recoverable": error.error_details.recoverable and error_mapping.get("recoverable", True),
                "suggestions": error.error_details.suggestions or error_mapping.get("suggestions", [])
            }
        }
        
        if error.error_details.details:
            response["error"]["details"] = error.error_details.details
        
        return response
    
    def log_error(self, error: ClinicalError, context: Optional[Dict[str, Any]] = None):
        """Log error with appropriate level and context."""
        log_data = {
            "error_code": error.error_details.code.value,
            "message": error.error_details.message,
            "recoverable": error.error_details.recoverable
        }
        
        if context:
            log_data["context"] = context
        
        if error.error_details.details:
            log_data["details"] = error.error_details.details
        
        if error.error_details.recoverable:
            self.logger.warning(f"Recoverable error: {log_data}")
        else:
            self.logger.error(f"Non-recoverable error: {log_data}")
    
    def handle_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle any exception and convert to standardized response."""
        if isinstance(exc, ClinicalError):
            self.log_error(exc, context)
            return self.create_error_response(exc)
        
        # Handle unexpected exceptions
        self.logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        error_details = ErrorDetails(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(exc)}",
            recoverable=True
        )
        
        clinical_error = ClinicalError(error_details)
        return self.create_error_response(clinical_error)


def handle_errors(error_handler: ErrorHandler = None):
    """Decorator to handle errors in functions."""
    if error_handler is None:
        error_handler = ErrorHandler()
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_exception(e, {
                    "function": func.__name__,
                    "args": str(args)[:200],  # Truncate for logging
                    "kwargs": str(kwargs)[:200]
                })
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return error_handler.handle_exception(e, {
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_patient_data(patient_data: Dict[str, Any]) -> None:
    """Validate patient data and raise appropriate errors."""
    if not patient_data:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_PATIENT_DATA,
            message="Patient data is required",
            details={"provided_data": patient_data}
        ))
    
    age = patient_data.get('age')
    if age is not None:
        if not isinstance(age, (int, float)) or age < 0 or age > 150:
            raise ValidationError(ErrorDetails(
                code=ErrorCode.INVALID_PATIENT_DATA,
                message="Age must be between 0 and 150 years",
                details={"provided_age": age}
            ))
    
    weight = patient_data.get('weight')
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight <= 0 or weight > 500:
            raise ValidationError(ErrorDetails(
                code=ErrorCode.INVALID_PATIENT_DATA,
                message="Weight must be between 0.5 and 500 kg",
                details={"provided_weight": weight}
            ))


def validate_medication_dose(dose: float, min_dose: float, max_dose: float, medication: str) -> None:
    """Validate medication dose calculations."""
    if dose < min_dose or dose > max_dose:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_DOSE_CALCULATION,
            message=f"Calculated dose {dose}mg is outside safe range for {medication}",
            details={
                "calculated_dose": dose,
                "min_dose": min_dose,
                "max_dose": max_dose,
                "medication": medication
            },
            suggestions=[
                f"Verify patient weight is correct",
                f"Check dosing guidelines for {medication}",
                f"Consider alternative medications"
            ]
        ))


def check_data_availability(data: Dict[str, Any], data_type: str) -> None:
    """Check if required data is available."""
    if not data:
        raise DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message=f"{data_type} data is not available",
            details={"data_type": data_type},
            recoverable=False
        ))


def check_condition_exists(condition_id: str, conditions: Dict[str, Any]) -> None:
    """Check if condition exists in database."""
    if condition_id not in conditions:
        raise BusinessLogicError(ErrorDetails(
            code=ErrorCode.CONDITION_NOT_FOUND,
            message=f"Condition '{condition_id}' not found in database",
            details={"condition_id": condition_id, "available_conditions": list(conditions.keys())},
            suggestions=[
                "Check condition spelling",
                "Use standard medical terminology",
                f"Available conditions: {', '.join(list(conditions.keys())[:5])}"
            ]
        ))


def check_medication_exists(medication: str, condition_id: str, medications: Dict[str, Any]) -> None:
    """Check if medication exists for condition."""
    found = False
    for med_line in medications.values():
        if medication in med_line:
            found = True
            break
    
    if not found:
        available_meds = []
        for med_line in medications.values():
            available_meds.extend(med_line.keys())
        
        raise BusinessLogicError(ErrorDetails(
            code=ErrorCode.MEDICATION_NOT_FOUND,
            message=f"Medication '{medication}' not found for condition '{condition_id}'",
            details={
                "medication": medication,
                "condition_id": condition_id,
                "available_medications": available_meds
            },
            suggestions=[
                "Check medication spelling",
                "Consider alternative medications",
                f"Available medications: {', '.join(available_meds)}"
            ]
        ))


# Global error handler instance
global_error_handler = ErrorHandler()