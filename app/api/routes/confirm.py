from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.confirm import ConfirmRequest, ConfirmResponse
from app.services.confirmation_service import ConfirmationService
from app.dependencies import get_confirmation_service

router = APIRouter(tags=["Confirm"])


@router.post("/confirm", response_model=ConfirmResponse, status_code=status.HTTP_200_OK, summary="Confirm or reject a replan proposal")
def confirm_replan(
    req: ConfirmRequest,
    confirmation_service: ConfirmationService = Depends(get_confirmation_service)
):
    try:
        res = confirmation_service.process_confirmation(req)
        return res
    except ValueError as ve:
        err_str = str(ve)
        if "not found" in err_str:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_str)
        elif "not in PENDING state" in err_str:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_str)
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation processing failed: {str(e)}"
        )
