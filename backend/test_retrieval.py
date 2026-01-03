import sys
  import os
  sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

  from src.config.settings import Settings
  from src.services.retrieval_service import RetrievalService

  def test_retrieval():
      try:
          settings = Settings()
          retrieval_service = RetrievalService(settings)

          print("Testing retrieval...")
          results = retrieval_service.retrieve(
              query_text="machine learning concepts",
              limit=5,
              min_score=0.1
          )

          print(f"Retrieved {len(results)} results:")
          for i, result in enumerate(results):
              print(f"{i+1}. Score: {result.similarity_score:.3f}")
              print(f"   Content: {result.content_text[:100]}...")
              print(f"   Source: {result.source_url}")
              print()

      except Exception as e:
          print(f"Error during retrieval: {e}")
          print("Make sure your .env file has the required API keys and Qdrant configuration")

  if __name__ == "__main__":
      test_retrieval()