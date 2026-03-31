class MFAStateError(RuntimeError):
    """MFA UI did not match expectations."""


class OTPNotFoundError(RuntimeError):
    """OTP could not be retrieved within retry limits."""
