from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import re
from collections import Counter

from .models import FAQEntry, AIChatLog, FAQSuggestion
from .serializers import FAQEntrySerializer, AIChatLogSerializer, FAQSuggestionSerializer
from apps.users.permissions import ReadOnlyOrSuperAdmin


class FAQListView(generics.ListCreateAPIView):
    queryset = FAQEntry.objects.filter(is_deleted=False)
    serializer_class = FAQEntrySerializer
    permission_classes = [ReadOnlyOrSuperAdmin]


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQEntry.objects.filter(is_deleted=False)
    serializer_class = FAQEntrySerializer
    permission_classes = [ReadOnlyOrSuperAdmin]


class ChatLogListView(generics.ListAPIView):
    """View for listing chat logs with filtering"""
    queryset = AIChatLog.objects.all()
    serializer_class = AIChatLogSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]
    
    def get_queryset(self):
        queryset = AIChatLog.objects.all()
        
        # Filter by success status
        is_successful = self.request.query_params.get('is_successful')
        if is_successful is not None:
            queryset = queryset.filter(is_successful=is_successful.lower() == 'true')
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)
        
        # Filter by mode
        mode = self.request.query_params.get('mode')
        if mode:
            queryset = queryset.filter(mode=mode)
            
        return queryset.order_by('-created_at')


class FAQSuggestionListView(generics.ListAPIView):
    """List all FAQ suggestions with filtering"""
    serializer_class = FAQSuggestionSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]
    
    def get_queryset(self):
        queryset = FAQSuggestion.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset


class FAQSuggestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific FAQ suggestion"""
    queryset = FAQSuggestion.objects.all()
    serializer_class = FAQSuggestionSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]


class FAQMakerAnalyzeView(APIView):
    """
    FAQ Maker AI - Analyzes chat logs to identify common unanswered queries
    and generates FAQ suggestions
    """
    permission_classes = [ReadOnlyOrSuperAdmin]
    
    def post(self, request):
        days = request.data.get('days', 7)
        min_query_count = request.data.get('min_query_count', 2)
        similarity_threshold = request.data.get('similarity_threshold', 0.7)
        
        # Get unanswered/failed queries from recent chat logs
        start_date = timezone.now() - timedelta(days=days)
        failed_logs = AIChatLog.objects.filter(
            created_at__gte=start_date,
            is_successful=False
        ).values('user_query')
        
        # Also get queries that didn't match any FAQ (no faq_entry_id)
        unmatched_logs = AIChatLog.objects.filter(
            created_at__gte=start_date,
            faq_entry__isnull=True,
            is_successful=True  # Successful fallback but no exact match
        ).values('user_query')
        
        # Combine all queries to analyze
        all_queries = list(failed_logs) + list(unmatched_logs)
        
        if not all_queries:
            return Response({
                'message': 'No unanswered queries found in the specified period',
                'suggestions_created': 0
            })
        
        # Group similar queries
        query_groups = self._group_similar_queries(
            [q['user_query'] for q in all_queries],
            similarity_threshold
        )
        
        suggestions_created = 0
        
        for group in query_groups:
            if len(group['queries']) >= min_query_count:
                # Check if similar suggestion already exists
                existing = FAQSuggestion.objects.filter(
                    suggested_question__icontains=group['common_pattern'][:50],
                    status__in=['pending', 'approved']
                ).exists()
                
                if not existing:
                    # Generate suggestion using simple AI logic
                    suggestion = self._generate_suggestion(group)
                    FAQSuggestion.objects.create(**suggestion)
                    suggestions_created += 1
        
        return Response({
            'message': f'Analysis complete. Created {suggestions_created} new FAQ suggestions.',
            'suggestions_created': suggestions_created,
            'total_queries_analyzed': len(all_queries),
            'query_groups_found': len(query_groups)
        })
    
    def _group_similar_queries(self, queries, threshold):
        """Group similar queries based on common keywords and patterns"""
        groups = []
        processed = set()
        
        for i, query in enumerate(queries):
            if i in processed:
                continue
            
            # Normalize query
            normalized = query.lower().strip()
            keywords = set(re.findall(r'\b\w+\b', normalized))
            
            group = {
                'queries': [query],
                'keywords': keywords,
                'common_pattern': normalized
            }
            
            # Find similar queries
            for j, other_query in enumerate(queries[i+1:], start=i+1):
                if j in processed:
                    continue
                
                other_normalized = other_query.lower().strip()
                other_keywords = set(re.findall(r'\b\w+\b', other_normalized))
                
                # Calculate Jaccard similarity
                if keywords and other_keywords:
                    intersection = len(keywords & other_keywords)
                    union = len(keywords | other_keywords)
                    similarity = intersection / union if union > 0 else 0
                else:
                    similarity = 0
                
                if similarity >= threshold:
                    group['queries'].append(other_query)
                    group['keywords'] = group['keywords'] & other_keywords
                    processed.add(j)
            
            if len(group['queries']) >= 2:
                groups.append(group)
            processed.add(i)
        
        return groups
    
    def _generate_suggestion(self, group):
        """Generate FAQ suggestion from query group"""
        # Extract most common question pattern
        most_common = Counter(group['queries']).most_common(1)[0][0]
        
        # Determine category based on keywords
        category = self._categorize_query(group['keywords'])
        
        # Extract keywords
        keywords = ', '.join(list(group['keywords'])[:5])
        
        # Generate template answer based on category
        answer_template = self._generate_answer_template(category, most_common)
        
        return {
            'suggested_question': most_common,
            'suggested_answer': answer_template,
            'category': category,
            'keywords': keywords,
            'source_queries': group['queries'][:10],  # Store up to 10 examples
            'query_count': len(group['queries']),
            'confidence_score': min(0.5 + (len(group['queries']) * 0.1), 0.95),
            'status': 'pending'
        }
    
    def _categorize_query(self, keywords):
        """Categorize query based on keywords"""
        keyword_str = ' '.join(keywords).lower()
        
        if any(word in keyword_str for word in ['library', 'gym', 'cafeteria', 'office', 'room', 'building', 'where', 'location']):
            return 'location'
        elif any(word in keyword_str for word in ['schedule', 'time', 'when', 'hour', 'open', 'close']):
            return 'schedule'
        elif any(word in keyword_str for word in ['enrollment', 'grade', 'subject', 'course', 'class', 'exam']):
            return 'academic'
        elif any(word in keyword_str for word in ['service', 'payment', 'id', 'card', 'help']):
            return 'services'
        else:
            return 'general'
    
    def _generate_answer_template(self, category, question):
        """Generate answer template based on category"""
        templates = {
            'location': f"The location you're asking about can be found on the campus map. Please check the map in the app or ask for specific directions to navigate there.\n\n[Admin: Please verify the exact location and provide specific directions]",
            'schedule': f"Please check the official schedule or contact the relevant office for the most up-to-date timing information.\n\n[Admin: Please add specific schedule details]",
            'academic': f"For academic-related inquiries, please contact the Registrar's Office or your program coordinator.\n\n[Admin: Please provide specific academic information]",
            'services': f"This service-related inquiry should be directed to the appropriate campus office.\n\n[Admin: Please specify which office handles this service]",
            'general': f"Thank you for your question. Please contact the campus information desk for assistance.\n\n[Admin: Please provide a complete answer]"
        }
        return templates.get(category, templates['general'])


class FAQSuggestionApproveView(APIView):
    """Approve or reject an FAQ suggestion"""
    permission_classes = [ReadOnlyOrSuperAdmin]
    
    def post(self, request, pk):
        try:
            suggestion = FAQSuggestion.objects.get(pk=pk)
        except FAQSuggestion.DoesNotExist:
            return Response({'error': 'Suggestion not found'}, status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get('action')
        review_note = request.data.get('review_note', '')
        
        if action not in ['approve', 'reject']:
            return Response({'error': 'Invalid action. Use "approve" or "reject"'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        suggestion.reviewed_by = request.user if hasattr(request, 'user') else None
        suggestion.reviewed_at = timezone.now()
        suggestion.review_note = review_note
        
        if action == 'approve':
            # Create actual FAQ entry
            faq_entry = FAQEntry.objects.create(
                question=suggestion.suggested_question,
                answer=suggestion.suggested_answer,
                category=suggestion.category,
                keywords=suggestion.keywords,
                usage_count=0
            )
            suggestion.faq_entry = faq_entry
            suggestion.status = 'approved'
            suggestion.save()
            
            return Response({
                'message': 'Suggestion approved and FAQ entry created',
                'faq_entry_id': faq_entry.id
            })
        else:
            suggestion.status = 'rejected'
            suggestion.save()
            
            return Response({'message': 'Suggestion rejected'})


class ChatbotAnalyticsView(APIView):
    """Get chatbot performance analytics"""
    permission_classes = [ReadOnlyOrSuperAdmin]
    
    def get(self, request):
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Overall stats
        total_queries = AIChatLog.objects.filter(created_at__gte=start_date).count()
        successful_queries = AIChatLog.objects.filter(
            created_at__gte=start_date,
            is_successful=True
        ).count()
        failed_queries = AIChatLog.objects.filter(
            created_at__gte=start_date,
            is_successful=False
        ).count()
        
        # Mode breakdown
        online_queries = AIChatLog.objects.filter(
            created_at__gte=start_date,
            mode='online'
        ).count()
        offline_queries = AIChatLog.objects.filter(
            created_at__gte=start_date,
            mode='offline'
        ).count()
        
        # Top unanswered queries
        top_unanswered = AIChatLog.objects.filter(
            created_at__gte=start_date,
            is_successful=False
        ).values('user_query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # FAQ usage stats
        faq_usage = FAQEntry.objects.filter(
            is_deleted=False
        ).order_by('-usage_count')[:10]
        
        # Suggestions stats
        pending_suggestions = FAQSuggestion.objects.filter(status='pending').count()
        approved_suggestions = FAQSuggestion.objects.filter(status='approved').count()
        rejected_suggestions = FAQSuggestion.objects.filter(status='rejected').count()
        
        success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
        
        return Response({
            'period_days': days,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'success_rate': round(success_rate, 2),
            'mode_breakdown': {
                'online': online_queries,
                'offline': offline_queries
            },
            'top_unanswered_queries': list(top_unanswered),
            'top_faqs': FAQEntrySerializer(faq_usage, many=True).data,
            'suggestions': {
                'pending': pending_suggestions,
                'approved': approved_suggestions,
                'rejected': rejected_suggestions
            }
        })

