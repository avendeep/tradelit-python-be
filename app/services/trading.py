from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import MongoDB
from app.models.trading import TradeModel, StrategyModel, PortfolioModel
from app.core.config import settings


class TradeService:
    """Service for trade operations"""

    @staticmethod
    async def create_trade(trade_data: dict) -> TradeModel:
        """Create a new trade"""
        collection = MongoDB.get_collection("trades")
        trade_data["timestamp"] = settings.now_naive()
        trade_data["status"] = trade_data.get("status", "PENDING")

        result = await collection.insert_one(trade_data)
        trade_data["_id"] = result.inserted_id
        return TradeModel(**trade_data)

    @staticmethod
    async def get_trade(trade_id: str) -> Optional[TradeModel]:
        """Get a trade by ID"""
        collection = MongoDB.get_collection("trades")
        trade = await collection.find_one({"_id": ObjectId(trade_id)})
        return TradeModel(**trade) if trade else None

    @staticmethod
    async def get_all_trades(skip: int = 0, limit: int = 100) -> List[TradeModel]:
        """Get all trades with pagination"""
        collection = MongoDB.get_collection("trades")
        cursor = collection.find().skip(skip).limit(limit).sort("timestamp", -1)
        trades = await cursor.to_list(length=limit)
        return [TradeModel(**trade) for trade in trades]

    @staticmethod
    async def update_trade_status(trade_id: str, status: str) -> Optional[TradeModel]:
        """Update trade status"""
        collection = MongoDB.get_collection("trades")
        result = await collection.find_one_and_update(
            {"_id": ObjectId(trade_id)},
            {"$set": {"status": status}},
            return_document=True,
        )
        return TradeModel(**result) if result else None


class StrategyService:
    """Service for strategy operations"""

    @staticmethod
    async def create_strategy(strategy_data: dict) -> StrategyModel:
        """Create a new strategy"""
        collection = MongoDB.get_collection("strategies")
        now = settings.now_naive()
        strategy_data["created_at"] = now
        strategy_data["updated_at"] = now

        result = await collection.insert_one(strategy_data)
        strategy_data["_id"] = result.inserted_id
        return StrategyModel(**strategy_data)

    @staticmethod
    async def get_strategy(strategy_id: str) -> Optional[StrategyModel]:
        """Get a strategy by ID"""
        collection = MongoDB.get_collection("strategies")
        strategy = await collection.find_one({"_id": ObjectId(strategy_id)})
        return StrategyModel(**strategy) if strategy else None

    @staticmethod
    async def get_all_strategies(
        skip: int = 0, limit: int = 100
    ) -> List[StrategyModel]:
        """Get all strategies with pagination"""
        collection = MongoDB.get_collection("strategies")
        cursor = collection.find().skip(skip).limit(limit)
        strategies = await cursor.to_list(length=limit)
        return [StrategyModel(**strategy) for strategy in strategies]

    @staticmethod
    async def update_strategy(
        strategy_id: str, update_data: dict
    ) -> Optional[StrategyModel]:
        """Update a strategy"""
        collection = MongoDB.get_collection("strategies")
        update_data["updated_at"] = settings.now_naive()

        result = await collection.find_one_and_update(
            {"_id": ObjectId(strategy_id)}, {"$set": update_data}, return_document=True
        )
        return StrategyModel(**result) if result else None

    @staticmethod
    async def delete_strategy(strategy_id: str) -> bool:
        """Delete a strategy"""
        collection = MongoDB.get_collection("strategies")
        result = await collection.delete_one({"_id": ObjectId(strategy_id)})
        return result.deleted_count > 0


class PortfolioService:
    """Service for portfolio operations"""

    @staticmethod
    async def get_portfolio(user_id: str) -> Optional[PortfolioModel]:
        """Get portfolio for a user"""
        collection = MongoDB.get_collection("portfolios")
        portfolio = await collection.find_one({"user_id": user_id})
        return PortfolioModel(**portfolio) if portfolio else None

    @staticmethod
    async def create_or_update_portfolio(
        user_id: str, portfolio_data: dict
    ) -> PortfolioModel:
        """Create or update portfolio"""
        collection = MongoDB.get_collection("portfolios")
        portfolio_data["user_id"] = user_id
        portfolio_data["updated_at"] = settings.now_naive()

        result = await collection.find_one_and_update(
            {"user_id": user_id},
            {"$set": portfolio_data},
            upsert=True,
            return_document=True,
        )
        return PortfolioModel(**result)
