from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.services.analysis_service import analysis_service
from app.core.config import settings

router = APIRouter()

@router.post("/eod/delta", response_model=dict)
async def calculate_eod_delta():
    """
    Calculate and store the daily cumulative delta for EOD analysis.
    Uses the configured instrument key, unit, interval, from_date, and to_date from the database.
    """
    try:
        # Fetch configuration
        config = await analysis_service.get_analysis_config()
        if not config:
            raise HTTPException(status_code=400, detail="EOD Analysis configuration not found. Please set configuration first.")
            
        instrument_key = config.get("instrument_key")
        unit = config.get("unit", "minute")
        interval = config.get("interval", "15")
        from_date = config.get("from_date")
        to_date = config.get("to_date")
        
        if not instrument_key:
             raise HTTPException(status_code=400, detail="Instrument key not configured.")

        if not from_date or not to_date:
            raise HTTPException(status_code=400, detail="from_date and to_date must be configured.")
        
        delta = await analysis_service.calculate_daily_delta(instrument_key, from_date, to_date, unit, interval)
        print(delta)
        if delta is None:
            raise HTTPException(status_code=404, detail=f"No data found for {instrument_key}")
            
        return {
            "instrument_key": instrument_key,
            "from_date": from_date,
            "to_date": to_date,
            "daily_cumulative_delta": delta,
            "message": "EOD delta calculated and stored successfully"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AnalysisConfigInput(BaseModel):
    instrument_key: str
    expiry_date: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    unit: str = "minute"
    interval: str = "15"


@router.post("/config", response_model=dict)
async def save_analysis_config(config: AnalysisConfigInput):
    """
    Save or update the EOD analysis configuration.
    """
    try:
        success = await analysis_service.save_analysis_config(
            config.instrument_key, 
            config.expiry_date,
            config.from_date,
            config.to_date,
            config.unit,
            config.interval
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save configuration")
            
        return {
            "message": "Configuration saved successfully",
            "instrument_key": config.instrument_key,
            "expiry_date": config.expiry_date,
            "from_date": config.from_date,
            "to_date": config.to_date,
            "unit": config.unit,
            "interval": config.interval
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=dict)
async def get_analysis_config():
    """
    Get the current EOD analysis configuration.
    """
    try:
        config = await analysis_service.get_analysis_config()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
            
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
