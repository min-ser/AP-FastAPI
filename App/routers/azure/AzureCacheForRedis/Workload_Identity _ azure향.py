from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel
from redis_entraid.cred_provider import create_from_default_azure_credential
import redis

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# Pydantic 모델로 요청 본문 데이터 정의
class RedisInfo(BaseModel):
    redis_host: str
    redis_port: str

@router.post("/Redis/workloadIdentity")
def workload_identity(data: RedisInfo):
    result_message = ""
    
    print("🚀 Starting Azure Redis Cache connection test...")
    result_message += "🚀 Starting Azure Redis Cache connection test..." +"\n"
    print(f"📡 Connecting to: {data.redis_host}:{data.redis_port}")
    result_message += "📡 Connecting to: "+data.redis_host+":"+data.redis_port +"\n"

    # Validate configuration
    if not data.redis_host or not data.redis_port:
        print("❌ Error: Redis host and port must be configured")
        result_message += "❌ Error: Redis host and port must be configured"+"\n"
        exit(1)
    print()  # Add a new line

    try:
        # Create credential provider using DefaultAzureCredential for Azure Entra ID authentication
        credential_provider = create_from_default_azure_credential(
            ("https://redis.azure.com/.default",),)

        # Create a Redis client with Azure Entra ID authentication
        r = redis.Redis(host=data.redis_host, 
                        port=data.redis_port, 
                        ssl=True, 
                        decode_responses=True, 
                        credential_provider=credential_provider,
                        socket_timeout=10,
                        socket_connect_timeout=10
                        )

        # Test connection 
        result = r.ping()
        print("✅ Ping returned : " + str(result))
        print()  # Add a new line
        result_message += "✅ Ping returned : "+str(result)+"\n"

        # Create a simple set and get operation
        result = r.set("Message", "Hello, The cache is working with Python!")
        print("✅ SET Message succeeded: " + str(result))
        print()  # Add a new line
        result_message += "✅ SET Message succeeded: "+str(result)+"\n"

        value = r.get("Message")

        if value is not None:
            print("✅ GET Message returned : " + str(value))
            print()  # Add a new line
            result_message += "✅ GET Message returned : "+str(value)+"\n"
        else:
            print("⚠️  GET Message returned None")
            print()  # Add a new line
            result_message += "⚠️  GET Message returned None "+"\n"

        print("🎉 All Redis operations completed successfully!")
        print()  # Add a new line
        result_message += "🎉 All Redis operations completed successfully!"+"\n"

    except redis.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("💡 Check if Redis host and port are correct, and ensure network connectivity")
        print()  # Add a new line
        result_message += "❌ Connection error:"+str(e)+"\n"
        result_message += "💡 Check if Redis host and port are correct, and ensure network connectivity"+"\n"
    except redis.AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        print("💡 Check if Azure Entra ID authentication is properly configured")
        print()  # Add a new line
        result_message += "❌ Authentication error:"+str(e)+"\n"
        result_message += "💡 Check if Azure Entra ID authentication is properly configured"+"\n"
    except redis.TimeoutError as e:
        print(f"❌ Timeout error: {e}")
        print("💡 Check network latency and Redis server performance")
        print()  # Add a new line
        result_message += "❌ Timeout error:"+str(e)+"\n"
        result_message += "💡 Check network latency and Redis server performance"+"\n"
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        result_message += "❌ Unexpected error:"+str(e)+"\n"
        if "999" in str(e):
            print("💡 Error 999 typically indicates a network connectivity issue or firewall restriction")
            print("   - Verify the Redis hostname is correct")
            print("   - Verify that you have logged in with Az CLI")
            print("   - Ensure the Redis cache is running and accessible")
            result_message += "💡 Error 999 typically indicates a network connectivity issue or firewall restriction"+"\n"
            result_message += "   - Verify the Redis hostname is correct"+"\n"
            result_message += "   - Verify that you have logged in with Az CLI"+"\n"
            result_message += "   - Ensure the Redis cache is running and accessible"+"\n"
        print()  # Add a new line
    finally:
        # Clean up connection if it exists
        if 'r' in locals():
            try:
                r.close()
                print("🔐 Redis connection closed")
                result_message += "🔐 Redis connection closed"+"\n"
            except Exception as e:
                print(f"❌ Error closing connection: {e}")
                result_message += "❌ Error closing connection:"+str(e)+"\n"

    return {"message": result_message}