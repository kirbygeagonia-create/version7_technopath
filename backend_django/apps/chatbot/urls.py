from django.urls import path
from . import views

urlpatterns = [
    # FAQ endpoints
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
    path('faq/<int:pk>/', views.FAQDetailView.as_view(), name='faq-detail'),
    
    # Chat log endpoints
    path('chat-logs/', views.ChatLogListView.as_view(), name='chat-logs'),
    
    # FAQ Maker AI endpoints
    path('faq-suggestions/', views.FAQSuggestionListView.as_view(), name='faq-suggestions'),
    path('faq-suggestions/<int:pk>/', views.FAQSuggestionDetailView.as_view(), name='faq-suggestion-detail'),
    path('faq-suggestions/<int:pk>/approve/', views.FAQSuggestionApproveView.as_view(), name='faq-suggestion-approve'),
    path('faq-maker/analyze/', views.FAQMakerAnalyzeView.as_view(), name='faq-maker-analyze'),
    
    # Analytics
    path('analytics/', views.ChatbotAnalyticsView.as_view(), name='chatbot-analytics'),
]
