import random
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Compliance Audit API")


class ComplianceIssue(BaseModel):
    issue: str
    severity: str  # e.g., "low", "medium", "high"


class AuditResponse(BaseModel):
    compliance_score: float
    issues: List[ComplianceIssue]
    summary: str


class AuditEngine:
    """Simulates image compliance analysis."""

    def __init__(self):
        # In a real implementation, you would load ML models or rule sets here.
        self._possible_issues = [
            ("Misleading claim detected", "high"),
            ("Logo not visible", "medium"),
            ("Text too small to read", "low"),
            ("Color contrast insufficient", "medium"),
            ("Missing required disclaimer", "high"),
            ("Image resolution too low", "low"),
        ]

    def analyze(self, image_bytes: bytes) -> tuple[float, List[ComplianceIssue], str]:
        """
        Simulate analysis of image bytes.

        Returns:
            compliance_score: float between 0 and 100.
            issues: list of ComplianceIssue.
            summary: human-readable summary.
        """
        # Simulate based on file size (just for demonstration)
        file_size = len(image_bytes)
        # Random base score
        base_score = random.uniform(30, 100)
        # Penalize very large or very small files
        if file_size > 5_000_000:  # >5 MB
            base_score -= 20
        elif file_size < 10_000:   # <10 KB
            base_score -= 10
        # Clamp
        compliance_score = max(0.0, min(100.0, base_score))

        # Generate random issues
        num_issues = random.randint(0, len(self._possible_issues))
        selected = random.sample(self._possible_issues, num_issues)
        issues = [
            ComplianceIssue(issue=desc, severity=sev)
            for desc, sev in selected
        ]

        # Build summary
        if compliance_score >= 80:
            summary = "Image appears compliant with minor or no issues."
        elif compliance_score >= 50:
            summary = "Image has moderate compliance issues that should be addressed."
        else:
            summary = "Image has significant compliance issues and requires revision."

        return compliance_score, issues, summary


@app.post("/audit", response_model=AuditResponse)
async def audit_image(file: UploadFile = File(...)):
    """
    Accept an image file and return a compliance audit result.
    """
    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
                   f"Allowed types: {', '.join(allowed_types)}",
        )

    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    engine = AuditEngine()
    score, issues, summary = engine.analyze(image_bytes)

    return AuditResponse(
        compliance_score=round(score, 2),
        issues=issues,
        summary=summary,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
