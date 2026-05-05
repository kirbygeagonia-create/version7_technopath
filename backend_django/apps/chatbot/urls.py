from django.urls import path
from .views import (
    FAQListView, FAQDetailView,
    ChatLogListView, ChatLogCreateView,
    FAQSuggestionListView, FAQSuggestionDetailView, FAQSuggestionApproveView,
    FAQMakerAnalyzeView,
    ChatbotAnalyticsView,
    # Hybrid AI endpoints
    TrainingDataListCreateView, TrainingDataBatchCreateView,
    ChatRatingCreateView, ChatRatingListView,
    # User correction learning
    ChatCorrectionCreateView, ChatCorrectionListView, ChatCorrectionApproveView,
    RetrainTriggerView
)

urlpatterns = [
    # FAQ endpoints
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('faq/<int:pk>/', FAQDetailView.as_view(), name='faq-detail'),

    # Chat log endpoints
    path('chat-logs/', ChatLogListView.as_view(), name='chat-logs'),
    path('logs/', ChatLogListView.as_view(), name='chat-logs-alias'),  # Alias for dashboard
    path('log/', ChatLogCreateView.as_view(), name='chatlog-create'),

    # FAQ Maker AI endpoints
    path('faq-suggestions/', FAQSuggestionListView.as_view(), name='faq-suggestions'),
    path('faq-suggestions/<int:pk>/', FAQSuggestionDetailView.as_view(), name='faq-suggestion-detail'),
    path('faq-suggestions/<int:pk>/approve/', FAQSuggestionApproveView.as_view(), name='faq-suggestion-approve'),
    path('faq-maker/analyze/', FAQMakerAnalyzeView.as_view(), name='faq-maker-analyze'),

    # Analytics
    path('analytics/', ChatbotAnalyticsView.as_view(), name='chatbot-analytics'),

    # Hybrid AI ML Training endpoints
    path('training-data/', TrainingDataListCreateView.as_view(), name='training-data-list'),
    path('training-data/batch/', TrainingDataBatchCreateView.as_view(), name='training-data-batch'),

    # Chat ratings for continuous learning
    path('ratings/', ChatRatingCreateView.as_view(), name='chat-rating-create'),
    path('ratings/list/', ChatRatingListView.as_view(), name='chat-rating-list'),

    # User corrections - teach chatbot when it's wrong
    path('corrections/', ChatCorrectionCreateView.as_view(), name='chat-correction-create'),
    path('corrections/list/', ChatCorrectionListView.as_view(), name='chat-correction-list'),
    path('corrections/<int:pk>/approve/', ChatCorrectionApproveView.as_view(), name='chat-correction-approve'),

    # Manual retrain trigger
    path('retrain/', RetrainTriggerView.as_view(), name='chatbot-retrain'),
]
