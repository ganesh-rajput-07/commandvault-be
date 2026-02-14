from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
import requests
from .models import AIModel

class ModelListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return a list of active AI models for the frontend to display.
        """
        models = AIModel.objects.filter(is_active=True).select_related('provider')
        data = []
        for model in models:
            data.append({
                'id': model.id,
                'name': model.name,
                'api_id': model.api_id,
                'provider': model.provider.name,
                'version': model.version,
                'default_params': model.default_params
            })
        return Response(data)

class GenerateImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Proxy the generation request to the selected AI provider.
        """
        model_id = request.data.get('model_id') # This is our DB ID, not the API ID
        prompt = request.data.get('prompt')
        params = request.data.get('params', {})
        
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch Model & Provider
        # If model_id is provided, look it up. Otherwise default to first active.
        if model_id:
            ai_model = get_object_or_404(AIModel, id=model_id, is_active=True)
        else:
            ai_model = AIModel.objects.filter(is_active=True).first()
            if not ai_model:
                return Response({'error': 'No active AI models configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        provider = ai_model.provider
        if not provider.is_active:
             return Response({'error': 'AI Provider is inactive'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        # 2. Construct Request (Simple OpenAI-like implementation for now)
        # In a real system, you would have a strategy pattern or adapters for different providers
        
        try:
            # Mock Strategy: If it looks like OpenAI/DALL-E
            if 'openai' in provider.name.lower():
                headers = {
                    'Authorization': f'Bearer {provider.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Merge default params with request params
                # OpenAI DALL-E 3 specific payload structure
                payload = {
                    "model": ai_model.api_id, # e.g., "dall-e-3"
                    "prompt": prompt,
                    "n": 1,
                    "size": params.get('size', "1024x1024"),
                    "quality": "standard",
                    "response_format": "url"
                }

                response = requests.post(f"{provider.base_url}/images/generations", json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    image_url = data['data'][0]['url']
                    return Response({'image_url': image_url})
                else:
                    return Response({'error': f"Provider Error: {response.text}"}, status=response.status_code)

            # Mock fallback for demonstration if no real API key is ready
            else:
                 # Just return a mock if it's our "Mock Provider"
                 if 'mock' in provider.name.lower():
                     import time
                     import random
                     time.sleep(2) # Simulate work
                     seed = random.randint(1, 1000)
                     return Response({'image_url': f"https://picsum.photos/seed/{seed}/1024/1024"})
                 
                 return Response({'error': 'Provider integration not implemented yet'}, status=status.HTTP_501_NOT_IMPLEMENTED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
