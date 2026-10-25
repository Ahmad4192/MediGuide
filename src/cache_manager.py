import os

# Naye aur purane dono LangChain versions ke liye safe import
try:
    from langchain_core.globals import set_llm_cache
except ImportError:
    from langchain.globals import set_llm_cache

try:
    from langchain_community.cache import InMemoryCache, SQLiteCache
except ImportError:
    from langchain.cache import InMemoryCache, SQLiteCache


def configure_cache(cache_type: str = "InMemoryCache", db_path: str = "cache.db") -> str:
    """
    LangChain LLM cache set karta hai: InMemoryCache ya SQLiteCache.
    """
    if cache_type == "SQLiteCache":
        set_llm_cache(SQLiteCache(database_path=db_path))
        return "SQLiteCache active (persists to disk, survives app restarts)"
    else:
        set_llm_cache(InMemoryCache())
        return "InMemoryCache active (in-memory RAM, ultra-fast, clears on restart)"