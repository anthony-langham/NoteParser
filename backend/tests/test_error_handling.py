#!/usr/bin/env python3
"""
Unit tests for error handling functionality.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.utils.error_handler import (
    ErrorHandler, handle_errors, global_error_handler,
    check_data_availability, check_condition_exists, check_medication_exists,
    validate_patient_data, validate_medication_dose,
    DataError, ValidationError, BusinessLogicError, ProcessingError,
    ErrorCode, ErrorDetails
)


class TestErrorDetails:
    """Test ErrorDetails class functionality."""
    
    def test_error_details_creation(self):
        """Test creating ErrorDetails with all parameters."""
        details = ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Test error message",
            details={"file": "test.json"},
            recoverable=True
        )
        
        assert details.code == ErrorCode.DATA_FILE_NOT_FOUND
        assert details.message == "Test error message"
        assert details.details["file"] == "test.json"
        assert details.recoverable is True
    
    def test_error_details_to_dict(self):
        """Test converting ErrorDetails to dictionary."""
        details = ErrorDetails(
            code=ErrorCode.CONDITION_NOT_FOUND,
            message="Condition not found",
            details={"condition_id": "invalid"},
            recoverable=False
        )
        
        result = details.to_dict()
        
        assert result["code"] == ErrorCode.CONDITION_NOT_FOUND.value
        assert result["message"] == "Condition not found"
        assert result["details"]["condition_id"] == "invalid"
        assert result["recoverable"] is False
        assert "timestamp" in result


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_data_error(self):
        """Test DataError exception."""
        details = ErrorDetails(
            code=ErrorCode.DATA_FILE_CORRUPTED,
            message="Data file is corrupted",
            details={},
            recoverable=False
        )
        
        error = DataError(details)
        assert error.details == details
        assert str(error) == "Data file is corrupted"
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        details = ErrorDetails(
            code=ErrorCode.INVALID_PATIENT_DATA,
            message="Invalid patient weight",
            details={"weight": -1.0},
            recoverable=True
        )
        
        error = ValidationError(details)
        assert error.details == details
        assert str(error) == "Invalid patient weight"
    
    def test_business_logic_error(self):
        """Test BusinessLogicError exception."""
        details = ErrorDetails(
            code=ErrorCode.MEDICATION_NOT_FOUND,
            message="Medication not available",
            details={"medication": "unknown"},
            recoverable=True
        )
        
        error = BusinessLogicError(details)
        assert error.details == details
        assert str(error) == "Medication not available"
    
    def test_processing_error(self):
        """Test ProcessingError exception."""
        details = ErrorDetails(
            code=ErrorCode.CALCULATION_ERROR,
            message="Dose calculation failed",
            details={},
            recoverable=True
        )
        
        error = ProcessingError(details)
        assert error.details == details
        assert str(error) == "Dose calculation failed"


class TestValidationFunctions:
    """Test validation helper functions."""
    
    def test_check_data_availability_success(self):
        """Test successful data availability check."""
        mock_data = {"condition1": {}, "condition2": {}}
        
        # Should not raise exception
        check_data_availability(mock_data, "conditions")
    
    def test_check_data_availability_empty(self):
        """Test data availability check with empty data."""
        with pytest.raises(DataError) as exc_info:
            check_data_availability({}, "conditions")
        
        assert exc_info.value.details.code == ErrorCode.DATA_NOT_AVAILABLE
        assert "conditions" in exc_info.value.details.message
    
    def test_check_condition_exists_success(self):
        """Test successful condition existence check."""
        mock_data = {"croup": {"name": "Croup"}}
        
        # Should not raise exception
        check_condition_exists(mock_data, "croup")
    
    def test_check_condition_exists_not_found(self):
        """Test condition existence check with missing condition."""
        mock_data = {"croup": {"name": "Croup"}}
        
        with pytest.raises(BusinessLogicError) as exc_info:
            check_condition_exists(mock_data, "invalid_condition")
        
        assert exc_info.value.details.code == ErrorCode.CONDITION_NOT_FOUND
        assert "invalid_condition" in exc_info.value.details.message
    
    def test_check_medication_exists_success(self):
        """Test successful medication existence check."""
        mock_condition_data = {
            "medications": {
                "first_line": {
                    "dexamethasone": {"dose_mg_per_kg": 0.15}
                }
            }
        }
        
        # Should not raise exception
        check_medication_exists(mock_condition_data, "dexamethasone")
    
    def test_check_medication_exists_not_found(self):
        """Test medication existence check with missing medication."""
        mock_condition_data = {
            "medications": {
                "first_line": {
                    "dexamethasone": {"dose_mg_per_kg": 0.15}
                }
            }
        }
        
        with pytest.raises(BusinessLogicError) as exc_info:
            check_medication_exists(mock_condition_data, "invalid_medication")
        
        assert exc_info.value.details.code == ErrorCode.MEDICATION_NOT_FOUND
        assert "invalid_medication" in exc_info.value.details.message
    
    def test_check_medication_exists_no_medications(self):
        """Test medication check with no medications section."""
        mock_condition_data = {"name": "Croup"}
        
        with pytest.raises(BusinessLogicError) as exc_info:
            check_medication_exists(mock_condition_data, "dexamethasone")
        
        assert exc_info.value.details.code == ErrorCode.MEDICATION_NOT_FOUND
    
    def test_validate_patient_data_success(self):
        """Test successful patient data validation."""
        # Valid data should not raise exception
        validate_patient_data(age=3, weight=14.2)
        validate_patient_data(age=30, weight=70.0)
        validate_patient_data(age=65, weight=80.5)
    
    def test_validate_patient_data_invalid_age(self):
        """Test patient data validation with invalid age."""
        # Age too young
        with pytest.raises(ValidationError) as exc_info:
            validate_patient_data(age=-1, weight=14.2)
        assert exc_info.value.details.code == ErrorCode.INVALID_PATIENT_DATA
        
        # Age too old
        with pytest.raises(ValidationError) as exc_info:
            validate_patient_data(age=200, weight=70.0)
        assert exc_info.value.details.code == ErrorCode.INVALID_PATIENT_DATA
    
    def test_validate_patient_data_invalid_weight(self):
        """Test patient data validation with invalid weight."""
        # Weight too low
        with pytest.raises(ValidationError) as exc_info:
            validate_patient_data(age=3, weight=0.1)
        assert exc_info.value.details.code == ErrorCode.INVALID_PATIENT_DATA
        
        # Weight too high
        with pytest.raises(ValidationError) as exc_info:
            validate_patient_data(age=30, weight=1000.0)
        assert exc_info.value.details.code == ErrorCode.INVALID_PATIENT_DATA
    
    def test_validate_medication_dose_success(self):
        """Test successful medication dose validation."""
        # Valid doses should not raise exception
        validate_medication_dose(dose=5.0, min_dose=1.0, max_dose=10.0)
        validate_medication_dose(dose=1.0, min_dose=1.0, max_dose=10.0)  # At minimum
        validate_medication_dose(dose=10.0, min_dose=1.0, max_dose=10.0)  # At maximum
    
    def test_validate_medication_dose_below_minimum(self):
        """Test medication dose validation below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_medication_dose(dose=0.5, min_dose=1.0, max_dose=10.0)
        
        assert exc_info.value.details.code == ErrorCode.DOSE_CALCULATION_ERROR
        assert "below minimum" in exc_info.value.details.message
    
    def test_validate_medication_dose_above_maximum(self):
        """Test medication dose validation above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_medication_dose(dose=15.0, min_dose=1.0, max_dose=10.0)
        
        assert exc_info.value.details.code == ErrorCode.DOSE_CALCULATION_ERROR
        assert "above maximum" in exc_info.value.details.message


class TestErrorHandler:
    """Test ErrorHandler class functionality."""
    
    def test_error_handler_creation(self):
        """Test creating ErrorHandler instance."""
        handler = ErrorHandler()
        assert handler.error_count == 0
        assert len(handler.error_history) == 0
    
    def test_error_handler_log_error(self):
        """Test logging errors with ErrorHandler."""
        handler = ErrorHandler()
        
        error_details = ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Test error",
            details={},
            recoverable=True
        )
        
        handler.log_error(error_details)
        
        assert handler.error_count == 1
        assert len(handler.error_history) == 1
        assert handler.error_history[0] == error_details
    
    def test_error_handler_multiple_errors(self):
        """Test logging multiple errors."""
        handler = ErrorHandler()
        
        for i in range(3):
            error_details = ErrorDetails(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"Test error {i}",
                details={"index": i},
                recoverable=True
            )
            handler.log_error(error_details)
        
        assert handler.error_count == 3
        assert len(handler.error_history) == 3
    
    def test_error_handler_get_last_error(self):
        """Test getting the last error."""
        handler = ErrorHandler()
        
        # No errors initially
        assert handler.get_last_error() is None
        
        # Add an error
        error_details = ErrorDetails(
            code=ErrorCode.PROCESSING_ERROR,
            message="Last error",
            details={},
            recoverable=False
        )
        handler.log_error(error_details)
        
        last_error = handler.get_last_error()
        assert last_error == error_details
        assert last_error.message == "Last error"


class TestErrorDecorator:
    """Test the handle_errors decorator."""
    
    @pytest.mark.asyncio
    async def test_handle_errors_decorator_success(self):
        """Test decorator with successful function."""
        @handle_errors
        async def successful_function():
            return {"success": True, "data": "test"}
        
        result = await successful_function()
        assert result["success"] is True
        assert result["data"] == "test"
    
    @pytest.mark.asyncio
    async def test_handle_errors_decorator_data_error(self):
        """Test decorator handling DataError."""
        @handle_errors
        async def failing_function():
            raise DataError(ErrorDetails(
                code=ErrorCode.DATA_FILE_NOT_FOUND,
                message="File not found",
                details={},
                recoverable=False
            ))
        
        result = await failing_function()
        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == ErrorCode.DATA_FILE_NOT_FOUND.value
        assert result["error"]["message"] == "File not found"
    
    @pytest.mark.asyncio
    async def test_handle_errors_decorator_validation_error(self):
        """Test decorator handling ValidationError."""
        @handle_errors
        async def validation_failing_function():
            raise ValidationError(ErrorDetails(
                code=ErrorCode.INVALID_PATIENT_DATA,
                message="Invalid weight",
                details={"weight": -1.0},
                recoverable=True
            ))
        
        result = await validation_failing_function()
        assert result["success"] is False
        assert result["error"]["code"] == ErrorCode.INVALID_PATIENT_DATA.value
        assert result["error"]["recoverable"] is True
    
    @pytest.mark.asyncio
    async def test_handle_errors_decorator_unexpected_error(self):
        """Test decorator handling unexpected exceptions."""
        @handle_errors
        async def unexpected_error_function():
            raise ValueError("Unexpected error")
        
        result = await unexpected_error_function()
        assert result["success"] is False
        assert result["error"]["code"] == ErrorCode.UNEXPECTED_ERROR.value
        assert "Unexpected error" in result["error"]["message"]


class TestGlobalErrorHandler:
    """Test global error handler functionality."""
    
    def test_global_error_handler_initialization(self):
        """Test that global error handler is properly initialized."""
        assert global_error_handler is not None
        assert isinstance(global_error_handler, ErrorHandler)
        assert global_error_handler.error_count >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])