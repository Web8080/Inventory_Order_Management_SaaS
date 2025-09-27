"""
ML Service for Inventory Management SaaS
Provides demand forecasting and inventory optimization services
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
from pathlib import Path

# Import our ML modules
from models.forecasting import DemandForecaster
from models.optimization import InventoryOptimizer
from data.processor import DataProcessor
from utils.mongo_client import get_mongo_client

app = FastAPI(
    title="Inventory ML Service",
    description="ML service for demand forecasting and inventory optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
forecaster = None
optimizer = None
data_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup"""
    global forecaster, optimizer, data_processor
    
    # Initialize data processor
    data_processor = DataProcessor()
    
    # Initialize models
    forecaster = DemandForecaster()
    optimizer = InventoryOptimizer()
    
    # Load pre-trained models if they exist
    models_dir = Path("models")
    if models_dir.exists():
        try:
            forecaster.load_model(models_dir / "demand_forecaster.pkl")
            optimizer.load_model(models_dir / "inventory_optimizer.pkl")
        except Exception as e:
            print(f"Warning: Could not load pre-trained models: {e}")

# Pydantic models for API
class ForecastRequest(BaseModel):
    tenant_id: str
    product_ids: Optional[List[str]] = None
    forecast_horizon_days: int = 30
    confidence_level: float = 0.95

class ForecastResponse(BaseModel):
    product_id: str
    product_name: str
    forecasts: List[Dict[str, Any]]
    confidence_intervals: List[Dict[str, Any]]
    model_metrics: Dict[str, float]

class OptimizationRequest(BaseModel):
    tenant_id: str
    product_ids: Optional[List[str]] = None
    optimization_horizon_days: int = 30
    service_level: float = 0.95

class OptimizationResponse(BaseModel):
    product_id: str
    product_name: str
    recommended_reorder_point: int
    recommended_reorder_quantity: int
    expected_stockout_probability: float
    total_cost: float

class TrainingRequest(BaseModel):
    tenant_id: str
    product_ids: Optional[List[str]] = None
    retrain_all: bool = False

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Inventory ML Service is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "forecaster": forecaster is not None,
            "optimizer": optimizer is not None
        }
    }

@app.post("/forecast", response_model=List[ForecastResponse])
async def generate_forecast(request: ForecastRequest):
    """Generate demand forecasts for products"""
    try:
        # Get historical data
        historical_data = await data_processor.get_historical_sales(
            tenant_id=request.tenant_id,
            product_ids=request.product_ids
        )
        
        if historical_data.empty:
            raise HTTPException(status_code=404, detail="No historical data found")
        
        # Generate forecasts
        forecasts = []
        for product_id in historical_data['product_id'].unique():
            product_data = historical_data[historical_data['product_id'] == product_id]
            
            # Train model for this product
            model = forecaster.train_product_model(product_data)
            
            # Generate forecast
            forecast_result = forecaster.predict(
                model=model,
                horizon=request.forecast_horizon_days,
                confidence_level=request.confidence_level
            )
            
            # Get product name
            product_name = product_data['product_name'].iloc[0] if 'product_name' in product_data.columns else f"Product {product_id}"
            
            forecasts.append(ForecastResponse(
                product_id=product_id,
                product_name=product_name,
                forecasts=forecast_result['forecasts'],
                confidence_intervals=forecast_result['confidence_intervals'],
                model_metrics=forecast_result['metrics']
            ))
        
        return forecasts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize", response_model=List[OptimizationResponse])
async def optimize_inventory(request: OptimizationRequest):
    """Optimize inventory levels for products"""
    try:
        # Get current inventory and demand data
        inventory_data = await data_processor.get_current_inventory(
            tenant_id=request.tenant_id,
            product_ids=request.product_ids
        )
        
        demand_data = await data_processor.get_historical_sales(
            tenant_id=request.tenant_id,
            product_ids=request.product_ids
        )
        
        if inventory_data.empty or demand_data.empty:
            raise HTTPException(status_code=404, detail="No data found for optimization")
        
        # Generate optimizations
        optimizations = []
        for product_id in inventory_data['product_id'].unique():
            product_inventory = inventory_data[inventory_data['product_id'] == product_id]
            product_demand = demand_data[demand_data['product_id'] == product_id]
            
            # Optimize inventory for this product
            optimization_result = optimizer.optimize_product(
                inventory_data=product_inventory,
                demand_data=product_demand,
                horizon=request.optimization_horizon_days,
                service_level=request.service_level
            )
            
            # Get product name
            product_name = product_inventory['product_name'].iloc[0] if 'product_name' in product_inventory.columns else f"Product {product_id}"
            
            optimizations.append(OptimizationResponse(
                product_id=product_id,
                product_name=product_name,
                recommended_reorder_point=optimization_result['reorder_point'],
                recommended_reorder_quantity=optimization_result['reorder_quantity'],
                expected_stockout_probability=optimization_result['stockout_probability'],
                total_cost=optimization_result['total_cost']
            ))
        
        return optimizations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_models(request: TrainingRequest):
    """Train or retrain ML models"""
    try:
        # Get training data
        training_data = await data_processor.get_training_data(
            tenant_id=request.tenant_id,
            product_ids=request.product_ids
        )
        
        if training_data.empty:
            raise HTTPException(status_code=404, detail="No training data found")
        
        # Train models
        forecaster.train_global_model(training_data)
        optimizer.train_global_model(training_data)
        
        # Save models
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        forecaster.save_model(models_dir / "demand_forecaster.pkl")
        optimizer.save_model(models_dir / "inventory_optimizer.pkl")
        
        return {
            "message": "Models trained successfully",
            "training_samples": len(training_data),
            "models_saved": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
async def get_model_status():
    """Get status of loaded models"""
    return {
        "forecaster_loaded": forecaster is not None and forecaster.is_trained(),
        "optimizer_loaded": optimizer is not None and optimizer.is_trained(),
        "last_training": "N/A",  # TODO: Implement tracking
        "model_versions": {
            "forecaster": "1.0.0",
            "optimizer": "1.0.0"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
