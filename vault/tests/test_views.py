from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from vault.models import Prompt, Like, SavedPrompt, Comment

User = get_user_model()


class PromptCRUDTests(APITestCase):
    """Test Prompt CRUD operations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_prompt_authenticated(self):
        """Test authenticated user can create prompt"""
        data = {
            'title': 'Test Prompt',
            'text': 'This is a test prompt for ChatGPT',
            'ai_model': 'ChatGPT',
            'is_public': True
        }
        response = self.client.post('/api/prompts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Prompt.objects.filter(title='Test Prompt').exists())
        
        prompt = Prompt.objects.get(title='Test Prompt')
        self.assertEqual(prompt.owner, self.user)
        self.assertIsNotNone(prompt.slug)
    
    def test_create_prompt_unauthenticated(self):
        """Test unauthenticated user cannot create prompt"""
        self.client.force_authenticate(user=None)
        data = {'title': 'Test', 'text': 'Test'}
        response = self.client.post('/api/prompts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_prompts(self):
        """Test listing prompts"""
        Prompt.objects.create(
            owner=self.user,
            title='Public Prompt',
            text='Public text',
            is_public=True
        )
        Prompt.objects.create(
            owner=self.user,
            title='Private Prompt',
            text='Private text',
            is_public=False
        )
        
        response = self.client.get('/api/prompts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see both own prompts
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_retrieve_prompt(self):
        """Test retrieving a single prompt"""
        prompt = Prompt.objects.create(
            owner=self.user,
            title='Test Prompt',
            text='Test text',
            is_public=True
        )
        response = self.client.get(f'/api/prompts/{prompt.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Prompt')
    
    def test_update_own_prompt(self):
        """Test user can update their own prompt"""
        prompt = Prompt.objects.create(
            owner=self.user,
            title='Original Title',
            text='Original text'
        )
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/prompts/{prompt.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        prompt.refresh_from_db()
        self.assertEqual(prompt.title, 'Updated Title')
    
    def test_cannot_update_others_prompt(self):
        """Test user cannot update another user's prompt"""
        prompt = Prompt.objects.create(
            owner=self.other_user,
            title='Other User Prompt',
            text='Other text'
        )
        data = {'title': 'Hacked Title'}
        response = self.client.patch(f'/api/prompts/{prompt.slug}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_prompt(self):
        """Test user can delete their own prompt"""
        prompt = Prompt.objects.create(
            owner=self.user,
            title='To Delete',
            text='Delete me'
        )
        slug = prompt.slug
        response = self.client.delete(f'/api/prompts/{slug}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check if soft delete or hard delete
        # If soft delete, prompt.is_deleted should be True
        # If hard delete, prompt won't exist
        try:
            prompt.refresh_from_db()
            self.assertTrue(prompt.is_deleted)
        except Prompt.DoesNotExist:
            # Hard delete - this is also acceptable
            pass
    
    def test_cannot_delete_others_prompt(self):
        """Test user cannot delete another user's prompt"""
        prompt = Prompt.objects.create(
            owner=self.other_user,
            title='Other Prompt',
            text='Other text'
        )
        response = self.client.delete(f'/api/prompts/{prompt.slug}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PromptSearchTests(APITestCase):
    """Test prompt search functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test prompts
        Prompt.objects.create(
            owner=self.user,
            title='ChatGPT Marketing Prompt',
            text='Create marketing copy',
            ai_model='ChatGPT',
            is_public=True
        )
        Prompt.objects.create(
            owner=self.user,
            title='Claude Code Review',
            text='Review Python code',
            ai_model='Claude',
            is_public=True
        )
    
    def test_search_by_title(self):
        """Test searching prompts by title"""
        response = self.client.get('/api/prompts/?search=Marketing')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('Marketing', response.data['results'][0]['title'])
    
    def test_filter_by_ai_model(self):
        """Test filtering prompts by AI model"""
        response = self.client.get('/api/prompts/?ai_model=ChatGPT')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for prompt in response.data['results']:
            self.assertIn('ChatGPT', prompt['ai_model'])


class LikeTests(APITestCase):
    """Test like functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.prompt = Prompt.objects.create(
            owner=self.user,
            title='Test Prompt',
            text='Test text',
            is_public=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_like_prompt(self):
        """Test liking a prompt"""
        data = {'prompt_id': self.prompt.id}
        response = self.client.post('/api/likes/toggle/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        
        # Check like was created
        self.assertTrue(Like.objects.filter(user=self.user, prompt=self.prompt).exists())
    
    def test_unlike_prompt(self):
        """Test unliking a prompt"""
        # First like it
        Like.objects.create(user=self.user, prompt=self.prompt)
        
        # Then unlike
        data = {'prompt_id': self.prompt.id}
        response = self.client.post('/api/likes/toggle/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        
        # Check like was removed
        self.assertFalse(Like.objects.filter(user=self.user, prompt=self.prompt).exists())
    
    def test_like_requires_authentication(self):
        """Test liking requires authentication"""
        self.client.force_authenticate(user=None)
        data = {'prompt_id': self.prompt.id}
        response = self.client.post('/api/likes/toggle/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SavedPromptTests(APITestCase):
    """Test saved prompt functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.prompt = Prompt.objects.create(
            owner=self.user,
            title='Test Prompt',
            text='Test text',
            is_public=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_save_prompt(self):
        """Test saving a prompt"""
        data = {'prompt_id': self.prompt.id}
        response = self.client.post('/api/saved/toggle/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['saved'])
        
        # Check save was created
        self.assertTrue(SavedPrompt.objects.filter(user=self.user, prompt=self.prompt).exists())
    
    def test_unsave_prompt(self):
        """Test unsaving a prompt"""
        # First save it
        SavedPrompt.objects.create(user=self.user, prompt=self.prompt)
        
        # Then unsave
        data = {'prompt_id': self.prompt.id}
        response = self.client.post('/api/saved/toggle/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['saved'])


class CommentTests(APITestCase):
    """Test comment functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.prompt = Prompt.objects.create(
            owner=self.user,
            title='Test Prompt',
            text='Test text',
            is_public=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_comment(self):
        """Test creating a comment"""
        data = {
            'prompt': self.prompt.id,
            'text': 'Great prompt!'
        }
        response = self.client.post('/api/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(text='Great prompt!').exists())
    
    def test_delete_own_comment(self):
        """Test deleting own comment"""
        comment = Comment.objects.create(
            user=self.user,
            prompt=self.prompt,
            text='My comment'
        )
        response = self.client.delete(f'/api/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_cannot_delete_others_comment(self):
        """Test cannot delete another user's comment"""
        comment = Comment.objects.create(
            user=self.other_user,
            prompt=self.prompt,
            text='Other comment'
        )
        response = self.client.delete(f'/api/comments/{comment.id}/')
        # May return 403 or 404 depending on queryset filtering
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
