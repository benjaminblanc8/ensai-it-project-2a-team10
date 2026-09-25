from fastapi import APIRouter, Depends, HTTPException

from service.gare_service import Gareservice
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)