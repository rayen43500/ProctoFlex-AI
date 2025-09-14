from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
from fastapi.responses import FileResponse

from ....core.database import get_db
from ....models.exam import Exam, ExamStudent
from ....models.user import User
from ....crud.exam import get_exam, get_student_exams, start_exam, submit_exam
from ....core.security import get_current_user

router = APIRouter()

@router.get("/student/{student_id}")
async def get_student_exams_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all exams assigned to a student"""
    try:
        exams = get_student_exams(db, student_id)
        return exams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exams: {str(e)}"
        )

@router.get("/{exam_id}")
async def get_exam_endpoint(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific exam by ID"""
    try:
        exam = get_exam(db, exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        return exam
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exam: {str(e)}"
        )

@router.post("/{exam_id}/start")
async def start_exam_endpoint(
    exam_id: str,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start an exam for a student"""
    try:
        result = start_exam(db, exam_id, student_id)
        return {"message": "Exam started successfully", "exam_id": exam_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting exam: {str(e)}"
        )

@router.post("/{exam_id}/submit")
async def submit_exam_endpoint(
    exam_id: str,
    student_id: int,
    answers: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an exam for a student"""
    try:
        result = submit_exam(db, exam_id, student_id, answers)
        return {"message": "Exam submitted successfully", "exam_id": exam_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting exam: {str(e)}"
        )

@router.get("/{exam_id}/view")
async def view_exam_pdf(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View exam PDF - only for assigned students"""
    try:
        # Get the exam
        exam = get_exam(db, exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Check if student is assigned to this exam
        exam_student = db.query(ExamStudent).filter(
            ExamStudent.exam_id == exam_id,
            ExamStudent.student_id == current_user.id
        ).first()
        
        if not exam_student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this exam"
            )
        
        # Check if PDF file exists
        if not exam.pdf_filename:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No PDF file available for this exam"
            )
        
        pdf_path = os.path.join("uploads", "exams", exam.pdf_filename)
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found on server"
            )
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=exam.pdf_filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving PDF: {str(e)}"
        )

@router.get("/{exam_id}/material")
async def download_exam_material(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download exam material (PDF) - only for assigned students"""
    try:
        # Get the exam
        exam = get_exam(db, exam_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Check if student is assigned to this exam
        exam_student = db.query(ExamStudent).filter(
            ExamStudent.exam_id == exam_id,
            ExamStudent.student_id == current_user.id
        ).first()
        
        if not exam_student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this exam"
            )
        
        # Check if PDF file exists
        if not exam.pdf_filename:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No PDF file available for this exam"
            )
        
        pdf_path = os.path.join("uploads", "exams", exam.pdf_filename)
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found on server"
            )
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=exam.pdf_filename,
            headers={"Content-Disposition": f"attachment; filename={exam.pdf_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading material: {str(e)}"
        )