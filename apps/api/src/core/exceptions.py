"""Custom exceptions for the application."""


class AIEngineerException(Exception):
    """Base exception."""
    pass


class ValidationError(AIEngineerException):
    """Data validation error."""
    pass


class ExtractionError(AIEngineerException):
    """AI extraction error."""
    pass


class ReconciliationError(AIEngineerException):
    """Reconciliation engine error."""
    pass


class SAPIntegrationError(AIEngineerException):
    """SAP integration error."""
    pass


class SecurityError(AIEngineerException):
    """Security violation."""
    pass


class AIProviderError(AIEngineerException):
    """AI provider error."""
    pass


class WorkflowError(AIEngineerException):
    """Workflow engine error."""
    pass


class NotFoundError(AIEngineerException):
    """Resource not found."""
    pass


class PermissionDeniedError(AIEngineerException):
    """Permission denied."""
    pass
