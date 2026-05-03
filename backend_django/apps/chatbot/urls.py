from django.urls import path
from .views import (
    FAQListView, FAQDetailView,
    ChatLogListView, ChatLogCreateView,
    FAQSuggestionListView, FAQSuggestionDetailView, FAQSuggestionApproveView,
    FAQMakerAnalyzeView,
    ChatbotAnalyticsView
)

urlpatterns = [
    # FAQ endpoints
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('faq/<int:pk>/', FAQDetailView.as_view(), name='faq-detail'),
    
    # Chat log endpoints
    path('chat-logs/', ChatLogListView.as_view(), name='chat-logs'),
    path('log/', ChatLogCreateView.as_view(), name='chatlog-create'),
    
    # FAQ Maker AI endpoints
    path('faq-suggestions/', FAQSuggestionListView.as_view(), name='faq-suggestions'),
    path('faq-suggestions/<int:pk>/', FAQSuggestionDetailView.as_view(), name='faq-suggestion-detail'),
    path('faq-suggestions/<int:pk>/approve/', FAQSuggestionApproveView.as_view(), name='faq-suggestion-approve'),
    path('faq-maker/analyze/', FAQMakerAnalyzeView.as_view(), name='faq-maker-analyze'),
    
    # Analytics
    path('analytics/', ChatbotAnalyticsView.as_view(), name='chatbot-analytics'),
]
