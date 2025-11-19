# Quick Start Guide

## ✅ Your FastAPI app is running

Visit: <http://127.0.0.1:8000>

## 📚 Documentation

- **Swagger UI**: <http://127.0.0.1:8000/docs>
- **ReDoc**: <http://127.0.0.1:8000/redoc>

## 🚀 Running the App

### Simple Version (Currently Running)

```bash
python main_simple.py
```

### Full Version with MongoDB

1. Install MongoDB support:

   ```bash
   pip install motor pymongo
   ```

2. Start MongoDB on `localhost:27017`

3. Run:

   ```bash
   python main.py
   ```

## 📖 Next Steps

1. Explore the API docs at `/docs`
2. Try adding new endpoints
3. Enable MongoDB integration when ready
4. Build your trading strategies!

## 🛠 Files

- `main_simple.py` - Basic FastAPI app (running now)
- `main.py` - Full app with MongoDB & trading features
- `app/` - Organized code structure (models, routes, services)
