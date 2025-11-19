from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.trading import StrategyCreate, StrategyResponse
from app.services.trading import StrategyService

router = APIRouter()


@router.post("/", response_model=StrategyResponse, status_code=201)
async def create_strategy(strategy: StrategyCreate):
    """Create a new trading strategy"""
    try:
        strategy_data = strategy.dict()
        new_strategy = await StrategyService.create_strategy(strategy_data)
        return StrategyResponse(
            id=str(new_strategy.id),
            name=new_strategy.name,
            description=new_strategy.description,
            parameters=new_strategy.parameters,
            is_active=new_strategy.is_active,
            created_at=new_strategy.created_at,
            updated_at=new_strategy.updated_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create strategy: {str(e)}"
        )


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
):
    """Get all strategies with pagination"""
    try:
        strategies = await StrategyService.get_all_strategies(skip=skip, limit=limit)
        return [
            StrategyResponse(
                id=str(strategy.id),
                name=strategy.name,
                description=strategy.description,
                parameters=strategy.parameters,
                is_active=strategy.is_active,
                created_at=strategy.created_at,
                updated_at=strategy.updated_at,
            )
            for strategy in strategies
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch strategies: {str(e)}"
        )


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID"""
    try:
        strategy = await StrategyService.get_strategy(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return StrategyResponse(
            id=str(strategy.id),
            name=strategy.name,
            description=strategy.description,
            parameters=strategy.parameters,
            is_active=strategy.is_active,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch strategy: {str(e)}"
        )


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, strategy: StrategyCreate):
    """Update a strategy"""
    try:
        update_data = strategy.dict()
        updated_strategy = await StrategyService.update_strategy(
            strategy_id, update_data
        )
        if not updated_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return StrategyResponse(
            id=str(updated_strategy.id),
            name=updated_strategy.name,
            description=updated_strategy.description,
            parameters=updated_strategy.parameters,
            is_active=updated_strategy.is_active,
            created_at=updated_strategy.created_at,
            updated_at=updated_strategy.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update strategy: {str(e)}"
        )


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy"""
    try:
        deleted = await StrategyService.delete_strategy(strategy_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Strategy not found")

        return {"message": "Strategy deleted successfully", "strategy_id": strategy_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete strategy: {str(e)}"
        )
