from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import os
import re
from collections import Counter

from .models import FAQEntry, AIChatLog, FAQSuggestion, TrainingData, ChatRating, ChatCorrection
from .serializers import FAQEntrySerializer, AIChatLogSerializer, FAQSuggestionSerializer, TrainingDataSerializer, ChatRatingSerializer, ChatCorrectionSerializer
from apps.users.permissions import ReadOnlyOrSuperAdmin, IsSuperAdmin
from rest_framework.permissions import AllowAny


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


class ChatLogCreateView(APIView):
    """Receives chat logs from Flask chatbot — no auth required (server-to-server)."""
    permission_classes = []

    def post(self, request):
        user_query = request.data.get('user_query', '').strip()
        ai_response = request.data.get('ai_response', '').strip()
        mode = request.data.get('mode', 'online')
        is_successful = request.data.get('is_successful', True)

        if not user_query:
            return Response({'error': 'user_query is required'}, status=400)

        AIChatLog.objects.create(
            user_query=user_query,
            ai_response=ai_response,
            mode=mode,
            is_successful=is_successful
        )
        return Response({'status': 'logged'}, status=201)


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
        """Generate answer using OpenAI instead of placeholder templates"""
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if not openai_key:
            return f"[Please write an answer for: {question}]"
        try:
            from openai import OpenAI
            ai = OpenAI(api_key=openai_key)
            ctx = """You write FAQ answers for TechnoPath, a campus guide app for SEAIT (South East Asian Institute of Technology), Tupi, South Cotabato.
Campus facts: MST Building (4F, center) — CL1-CL10 labs on 3F. JST Building (4F, back). RST Building (3F, left of gate) — Registrar on 1F, Guidance/HR/Safety on 2F, IT on 3F. Library: ground floor left wing, Mon-Fri 8AM-6PM, Sat 8AM-12PM. Cafeteria between MST and Gymnasium, open 7AM-6PM.
Write a clear, specific 2-3 sentence answer. No placeholders. No [Admin:...] text. Write a complete, usable answer."""
            resp = ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": ctx},
                    {"role": "user", "content": f"Write an FAQ answer for this student question: {question}"}
                ],
                max_tokens=120,
                temperature=0.4
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[FAQMaker] OpenAI error: {e}")
            return f"[Please write an answer for: {question}]"


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


class TrainingDataListCreateView(generics.ListCreateAPIView):
    """
    List and create training data for ML intent classifier.
    Used by Flask chatbot to get training examples and post new ones.
    """
    queryset = TrainingData.objects.all()
    serializer_class = TrainingDataSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def get_queryset(self):
        queryset = TrainingData.objects.all()
        intent = self.request.query_params.get('intent', None)
        source = self.request.query_params.get('source', None)
        unused_only = self.request.query_params.get('unused_only', 'false').lower() == 'true'

        if intent:
            queryset = queryset.filter(intent_label=intent)
        if source:
            queryset = queryset.filter(source=source)
        if unused_only:
            queryset = queryset.filter(used_for_training=False)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(source='manual')


class TrainingDataBatchCreateView(APIView):
    """
    Batch create training data entries.
    Used by Flask chatbot to submit multiple ratings at once.
    """
    permission_classes = [ReadOnlyOrSuperAdmin]

    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of training data entries'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        errors = []

        for item in data:
            try:
                training = TrainingData.objects.create(
                    query_text=item.get('query_text', ''),
                    intent_label=item.get('intent_label', 'general'),
                    source=item.get('source', 'batch'),
                    used_for_training=False
                )
                created.append(training.id)
            except Exception as e:
                errors.append({'item': item, 'error': str(e)})

        return Response({
            'created_count': len(created),
            'created_ids': created,
            'error_count': len(errors),
            'errors': errors
        }, status=status.HTTP_201_CREATED)


class ChatRatingCreateView(APIView):
    """
    Create chat ratings from user feedback (thumbs up/down).
    Called by Flask chatbot when users rate responses.
    """
    permission_classes = []  # Allow Flask to post ratings

    def post(self, request):
        data = request.data

        # Validate required fields
        query_text = data.get('query_text', '').strip()
        response_text = data.get('response_text', '').strip()
        rating = data.get('rating')
        intent_detected = data.get('intent_detected', 'general')

        if not query_text or not response_text:
            return Response(
                {'error': 'query_text and response_text are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if rating not in ['thumbs_up', 'thumbs_down']:
            return Response(
                {'error': 'rating must be thumbs_up or thumbs_down'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the rating
        chat_rating = ChatRating.objects.create(
            query_text=query_text,
            response_text=response_text,
            intent_detected=intent_detected,
            rating=rating,
            rating_note=data.get('rating_note', ''),
            session_id=data.get('session_id', 'default')
        )

        # If thumbs down, also create a training example with corrected intent
        if rating == 'thumbs_down':
            TrainingData.objects.create(
                query_text=query_text,
                intent_label='general',
                source='rating',
                used_for_training=False
            )

        return Response({
            'id': chat_rating.id,
            'rating': chat_rating.rating,
            'intent': chat_rating.intent_detected,
            'status': 'created'
        }, status=status.HTTP_201_CREATED)


class ChatRatingListView(generics.ListAPIView):
    """List chat ratings with filtering - for admin review"""
    queryset = ChatRating.objects.all()
    serializer_class = ChatRatingSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def get_queryset(self):
        queryset = ChatRating.objects.all()
        rating = self.request.query_params.get('rating', None)
        intent = self.request.query_params.get('intent', None)
        days = self.request.query_params.get('days', None)

        if rating:
            queryset = queryset.filter(rating=rating)
        if intent:
            queryset = queryset.filter(intent_detected=intent)
        if days:
            from datetime import timedelta
            from django.utils import timezone
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)

        return queryset.order_by('-created_at')


class ChatCorrectionCreateView(APIView):
    """
    Create chat correction when user provides correct answer.
    Called by frontend when user says chatbot was wrong and gives correct info.
    """
    permission_classes = [AllowAny]  # Public endpoint - no auth required

    def post(self, request):
        data = request.data

        # Validate required fields
        query_text = data.get('query_text', '').strip()
        wrong_response = data.get('wrong_response', '').strip()
        correct_answer = data.get('correct_answer', '').strip()

        if not query_text or not wrong_response or not correct_answer:
            return Response({
                'error': 'query_text, wrong_response, and correct_answer are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the correction
        correction = ChatCorrection.objects.create(
            query_text=query_text,
            wrong_response=wrong_response,
            intent_detected=data.get('intent_detected'),
            session_id=data.get('session_id'),
            correct_answer=correct_answer,
            user_note=data.get('user_note', '')
        )

        return Response({
            'success': True,
            'message': 'Thank you! Your correction has been submitted for review.',
            'correction_id': correction.id,
            'status': correction.status
        }, status=status.HTTP_201_CREATED)


class ChatCorrectionListView(generics.ListAPIView):
    """List chat corrections with filtering - for admin review"""
    queryset = ChatCorrection.objects.all()
    serializer_class = ChatCorrectionSerializer
    permission_classes = [ReadOnlyOrSuperAdmin]

    def get_queryset(self):
        queryset = ChatCorrection.objects.all()
        status_filter = self.request.query_params.get('status', None)
        intent = self.request.query_params.get('intent', None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if intent:
            queryset = queryset.filter(intent_detected=intent)

        return queryset.order_by('-created_at')


class ChatCorrectionApproveView(APIView):
    """
    Admin endpoint to approve a correction and convert to FAQ.
    Only superadmins can approve corrections.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            correction = ChatCorrection.objects.get(pk=pk)
        except ChatCorrection.DoesNotExist:
            return Response({
                'error': 'Correction not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if correction.status == 'approved':
            return Response({
                'error': 'Correction already approved'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create FAQ entry from correction
        faq_entry = FAQEntry.objects.create(
            question=correction.query_text,
            answer=correction.correct_answer,
            category='learned',  # Mark as learned from user
            is_active=True,
            created_by=request.user
        )

        # Update correction
        correction.status = 'approved'
        correction.faq_entry = faq_entry
        correction.reviewed_by = request.user
        correction.reviewed_at = timezone.now()
        correction.review_note = request.data.get('review_note', 'Approved as new FAQ')
        correction.save()

        # Also add to training data for ML improvement
        TrainingData.objects.create(
            query_text=correction.query_text,
            intent_label=correction.intent_detected or 'general',
            source='rating'
        )

        return Response({
            'success': True,
            'message': 'Correction approved and converted to FAQ',
            'faq_id': faq_entry.id
        })


class RetrainTriggerView(APIView):
    """
    Trigger manual retraining of the ML model.
    Admin endpoint to force retrain based on recent ratings.
    """
    permission_classes = [ReadOnlyOrSuperAdmin]

    def post(self, request):
        days = int(request.data.get('days', 7))
        from datetime import timedelta
        from django.utils import timezone

        start_date = timezone.now() - timedelta(days=days)

        positive_ratings = ChatRating.objects.filter(
            rating='thumbs_up',
            created_at__gte=start_date
        ).values('query_text', 'intent_detected')

        negative_ratings = ChatRating.objects.filter(
            rating='thumbs_down',
            created_at__gte=start_date
        ).values('query_text', 'intent_detected')

        training_count = 0

        for rating in positive_ratings:
            TrainingData.objects.get_or_create(
                query_text=rating['query_text'],
                defaults={
                    'intent_label': rating['intent_detected'],
                    'source': 'rating',
                    'used_for_training': False
                }
            )
            training_count += 1

        for rating in negative_ratings:
            TrainingData.objects.get_or_create(
                query_text=rating['query_text'],
                defaults={
                    'intent_label': 'general',
                    'source': 'rating',
                    'used_for_training': False
                }
            )
            training_count += 1

        return Response({
            'message': f'Created {training_count} training entries from ratings',
            'positive_ratings_used': positive_ratings.count(),
            'negative_ratings_used': negative_ratings.count(),
            'period_days': days,
            'ready_for_training': TrainingData.objects.filter(
                used_for_training=False
            ).count()
        })
