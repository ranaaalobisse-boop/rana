from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid
from typing import Optional

from database import get_db
from models import User, UserGeneratedDesign, DesignRequest
from schemas import (
    AIGenerateRequest, AIGenerateResponse, 
    UserGeneratedDesignResponse, DesignRequestCreate, DesignRequestResponse
)
from routers.auth import get_current_user
from services.gemini_service import gemini_service

router = APIRouter(prefix="/api/ai", tags=["AI Design"])

@router.post("/generate-design", response_model=AIGenerateResponse)
def generate_design(
    request: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a jewelry design using AI (Google Gemini)
    """
    try:
        # Generate image using Gemini
        image_bytes = gemini_service.generate_jewelry_design(
            jewelry_type=request.type,
            color=request.color,
            shape=request.shape,
            material=request.material,
            karat=request.karat,
            gemstone_type=request.gemstone_type,
            gemstone_color=request.gemstone_color
        )
        
        if not image_bytes:
            # If Gemini fails or not configured, return error
            return AIGenerateResponse(
                success=False,
                design_id=0,
                image_url="",
                message="Failed to generate design. Please check Gemini API configuration."
            )
        
        # Generate unique filename
        filename = f"design_{current_user.id}_{uuid.uuid4().hex[:8]}.png"
        output_dir = "static/generated_designs"
        
        # Save image
        image_path = gemini_service.save_image(image_bytes, filename, output_dir)
        
        # Get relative URL path
        image_url = f"/static/generated_designs/{filename}"
        
        # Save to database
        selected_options = {
            "type": request.type,
            "color": request.color,
            "shape": request.shape,
            "material": request.material,
            "karat": request.karat,
            "gemstone_type": request.gemstone_type,
            "gemstone_color": request.gemstone_color
        }
        
        design = UserGeneratedDesign(
            user_id=current_user.id,
            selected_options=selected_options,
            generated_image_url=image_url
        )
        db.add(design)
        db.commit()
        db.refresh(design)
        
        return AIGenerateResponse(
            success=True,
            design_id=design.id,
            image_url=image_url,
            message="Design generated successfully"
        )
        
    except ValueError as e:
        return AIGenerateResponse(
            success=False,
            design_id=0,
            image_url="",
            message=f"Gemini API not configured: {str(e)}"
        )
    except Exception as e:
        return AIGenerateResponse(
            success=False,
            design_id=0,
            image_url="",
            message=f"Error generating design: {str(e)}"
        )

@router.get("/my-designs", response_model=list[UserGeneratedDesignResponse])
def get_my_designs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all AI-generated designs for current user
    """
    designs = db.query(UserGeneratedDesign).filter(
        UserGeneratedDesign.user_id == current_user.id
    ).order_by(UserGeneratedDesign.created_at.desc()).all()
    
    return designs

@router.post("/design-requests", response_model=DesignRequestResponse)
def create_design_request(
    request: DesignRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a custom design request to jewelers
    """
    # Validate generated design if provided
    if request.generated_design_id:
        design = db.query(UserGeneratedDesign).filter(
            UserGeneratedDesign.id == request.generated_design_id,
            UserGeneratedDesign.user_id == current_user.id
        ).first()
        if not design:
            raise HTTPException(status_code=404, detail="Design not found")
    
    # Create request
    design_request = DesignRequest(
        user_id=current_user.id,
        jeweler_id=request.jeweler_id,
        generated_design_id=request.generated_design_id,
        description=request.description,
        attachment_url=request.attachment_url,
        estimated_budget=request.estimated_budget
    )
    db.add(design_request)
    db.commit()
    db.refresh(design_request)
    
    return design_request

@router.get("/my-design-requests", response_model=list[DesignRequestResponse])
def get_my_design_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all design requests submitted by current user
    """
    requests = db.query(DesignRequest).filter(
        DesignRequest.user_id == current_user.id
    ).order_by(DesignRequest.request_date.desc()).all()
    
    return requests

@router.get("/designs/{design_id}", response_model=UserGeneratedDesignResponse)
def get_design_by_id(
    design_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific design by ID
    """
    design = db.query(UserGeneratedDesign).filter(
        UserGeneratedDesign.id == design_id,
        UserGeneratedDesign.user_id == current_user.id
    ).first()
    
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    return design
