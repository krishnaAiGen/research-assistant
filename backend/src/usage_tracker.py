import redis
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure Redis client with environment variables
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 2))
)

class RedisUsageTracker:
    
    def update_usage(self, chunk_id, source_doc_id):
        """Update usage count and last accessed time"""
        
        # Use Redis Hash to store structured data
        usage_key = f"usage:{chunk_id}"
        
        # Get current count or default to 0
        current_count = redis_client.hget(usage_key, "usage_count")
        new_count = int(current_count) + 1 if current_count else 1
        
        # Update all fields atomically
        redis_client.hset(usage_key, mapping={
            "chunk_id": chunk_id,
            "usage_count": new_count,
            "last_accessed": datetime.now().strftime("%Y-%m-%d"),
            "source_doc_id": source_doc_id
        })
        
        # Also maintain a sorted set for rankings
        redis_client.zadd("popular_chunks", {chunk_id: new_count})
        
        return new_count
    
    def get_usage_data(self, chunk_id):
        """Get complete usage data for a chunk"""
        usage_key = f"usage:{chunk_id}"
        data = redis_client.hgetall(usage_key)
        
        if not data:
            return None
            
        # Convert bytes to strings and parse
        return {
            "chunk_id": data[b"chunk_id"].decode(),
            "usage_count": int(data[b"usage_count"]),
            "last_accessed": data[b"last_accessed"].decode(),
            "source_doc_id": data[b"source_doc_id"].decode()
        }
    
    def get_popular_chunks(self, limit=10):
        """Get top chunks by usage count"""
        # Get top chunks from sorted set (highest scores first)
        popular = redis_client.zrevrange("popular_chunks", 0, limit-1, withscores=True)
        
        results = []
        for chunk_id, score in popular:
            usage_data = self.get_usage_data(chunk_id.decode())
            if usage_data:
                results.append(usage_data)
        
        return results
    
    def get_all_usage_stats(self):
        """Get usage stats for all chunks"""
        # Find all usage keys
        usage_keys = redis_client.keys("usage:*")
        
        results = []
        for key in usage_keys:
            chunk_id = key.decode().replace("usage:", "")
            usage_data = self.get_usage_data(chunk_id)
            if usage_data:
                results.append(usage_data)
        
        # Sort by usage count
        return sorted(results, key=lambda x: x["usage_count"], reverse=True) 