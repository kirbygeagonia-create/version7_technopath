import 'package:flutter/material.dart';
import '../database_helper_v2.dart';

/// User Feedback/Ratings Submission Screen
/// Allows users to submit anonymous feedback and ratings for facilities/rooms
class FeedbackSubmissionScreen extends StatefulWidget {
  final int? facilityId;
  final int? roomId;
  final String? preSelectedCategory;

  const FeedbackSubmissionScreen({
    super.key,
    this.facilityId,
    this.roomId,
    this.preSelectedCategory,
  });

  @override
  State<FeedbackSubmissionScreen> createState() => _FeedbackSubmissionScreenState();
}

class _FeedbackSubmissionScreenState extends State<FeedbackSubmissionScreen> {
  final DatabaseHelper _db = DatabaseHelper.instance;
  final _formKey = GlobalKey<FormState>();
  final _commentController = TextEditingController();
  
  int _rating = 0;
  String _selectedCategory = 'general';
  bool _isAnonymous = true;
  int? _selectedFacilityId;
  int? _selectedRoomId;
  List<Map<String, dynamic>> _facilities = [];
  List<Map<String, dynamic>> _rooms = [];
  bool _isLoading = true;
  bool _isSubmitting = false;
  bool _submitted = false;

  final List<Map<String, dynamic>> _categories = [
    {'value': 'general', 'label': 'General', 'icon': Icons.feedback},
    {'value': 'facility', 'label': 'Facility', 'icon': Icons.business},
    {'value': 'navigation', 'label': 'Navigation', 'icon': Icons.navigation},
    {'value': 'ai_chatbot', 'label': 'AI Chatbot', 'icon': Icons.smart_toy},
    {'value': 'app', 'label': 'App Experience', 'icon': Icons.phone_android},
  ];

  @override
  void initState() {
    super.initState();
    _selectedCategory = widget.preSelectedCategory ?? 'general';
    _selectedFacilityId = widget.facilityId;
    _selectedRoomId = widget.roomId;
    _loadData();
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final facilities = await _db.getAllFacilities();
      setState(() {
        _facilities = facilities;
        _isLoading = false;
      });
      
      if (_selectedFacilityId != null) {
        await _loadRoomsForFacility(_selectedFacilityId!);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _loadRoomsForFacility(int facilityId) async {
    final rooms = await _db.getRoomsByFacility(facilityId);
    setState(() => _rooms = rooms);
  }

  Future<void> _submitFeedback() async {
    if (_rating == 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select a rating')),
      );
      return;
    }

    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isSubmitting = true);

      try {
        final ratingData = {
          'facility_id': _selectedCategory == 'facility' ? _selectedFacilityId : null,
          'room_id': _selectedRoomId,
          'rating': _rating,
          'comment': _commentController.text,
          'category': _selectedCategory,
          'is_anonymous': _isAnonymous ? 1 : 0,
        };

        await _db.insertRating(ratingData);

        setState(() {
          _isSubmitting = false;
          _submitted = true;
        });

        // Show thank you animation
        await Future.delayed(Duration(seconds: 2));
        if (mounted) {
          Navigator.pop(context, true);
        }
      } catch (e) {
        if (mounted) {
          setState(() => _isSubmitting = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error submitting feedback: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Submit Feedback'),
        backgroundColor: Color(0xFFFF9800),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _submitted
              ? _buildSuccessView()
              : _buildFormView(),
    );
  }

  Widget _buildSuccessView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.check_circle, size: 80, color: Colors.green),
          ),
          SizedBox(height: 24),
          Text(
            'Thank You!',
            style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 12),
          Text(
            'Your feedback has been submitted successfully.',
            style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 8),
          Text(
            'It helps us improve the campus experience.',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildFormView() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFFFF9800).withValues(alpha: 0.1), Color(0xFFFF9800).withValues(alpha: 0.05)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Icon(Icons.rate_review, size: 48, color: Color(0xFFFF9800)),
                  SizedBox(height: 12),
                  Text(
                    'We Value Your Feedback',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Help us improve the SEAIT Campus Guide by sharing your experience.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 24),
            
            // Rating Section
            Text(
              'Rate Your Experience',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) {
                  final starNumber = index + 1;
                  return IconButton(
                    iconSize: 40,
                    onPressed: () => setState(() => _rating = starNumber),
                    icon: Icon(
                      starNumber <= _rating ? Icons.star : Icons.star_border,
                      color: starNumber <= _rating ? Colors.amber : Colors.grey[400],
                    ),
                  );
                }),
              ),
            ),
            Center(
              child: Text(
                _getRatingLabel(_rating),
                style: TextStyle(
                  fontSize: 16,
                  color: _rating > 0 ? Color(0xFFFF9800) : Colors.grey,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            
            SizedBox(height: 24),
            
            // Category Selection
            Text(
              'Feedback Category',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _categories.map((category) {
                final isSelected = _selectedCategory == category['value'];
                return ChoiceChip(
                  avatar: Icon(
                    category['icon'] as IconData,
                    size: 18,
                    color: isSelected ? Colors.white : Colors.grey[600],
                  ),
                  label: Text(category['label'] as String),
                  selected: isSelected,
                  selectedColor: Color(0xFFFF9800),
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : Colors.black,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _selectedCategory = category['value'] as String);
                    }
                  },
                );
              }).toList(),
            ),
            
            SizedBox(height: 24),
            
            // Facility/Room Selection (if facility category)
            if (_selectedCategory == 'facility') ...[
              Text(
                'Select Facility (Optional)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              SizedBox(height: 8),
              DropdownButtonFormField<int>(
                initialValue: _selectedFacilityId,
                decoration: InputDecoration(
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  prefixIcon: Icon(Icons.business),
                  hintText: 'Select a facility',
                ),
                items: [
                  DropdownMenuItem(value: null, child: Text('General Campus')),
                  ..._facilities.map((f) => DropdownMenuItem(
                    value: f['id'] as int,
                    child: Text(f['name'] as String),
                  )),
                ],
                onChanged: (value) {
                  setState(() {
                    _selectedFacilityId = value;
                    _selectedRoomId = null;
                  });
                  if (value != null) {
                    _loadRoomsForFacility(value);
                  } else {
                    setState(() => _rooms = []);
                  }
                },
              ),
              
              if (_rooms.isNotEmpty) ...[
                SizedBox(height: 16),
                Text(
                  'Select Room (Optional)',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 8),
                DropdownButtonFormField<int>(
                  initialValue: _selectedRoomId,
                  decoration: InputDecoration(
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    prefixIcon: Icon(Icons.meeting_room),
                    hintText: 'Select a room',
                  ),
                  items: [
                    DropdownMenuItem(value: null, child: Text('Entire Facility')),
                    ..._rooms.map((r) => DropdownMenuItem(
                      value: r['id'] as int,
                      child: Text(r['name'] as String),
                    )),
                  ],
                  onChanged: (value) => setState(() => _selectedRoomId = value),
                ),
              ],
              
              SizedBox(height: 24),
            ],
            
            // Comments
            Text(
              'Your Comments',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            TextFormField(
              controller: _commentController,
              maxLines: 4,
              maxLength: 500,
              decoration: InputDecoration(
                hintText: 'Tell us about your experience... What did you like? What can we improve?',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                alignLabelWithHint: true,
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter your feedback';
                }
                return null;
              },
            ),
            
            SizedBox(height: 16),
            
            // Anonymous Toggle
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(Icons.visibility_off, color: Colors.grey[600]),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Submit Anonymously',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        Text(
                          'Your feedback will be kept confidential',
                          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  ),
                  Switch(
                    value: _isAnonymous,
                    activeThumbColor: Color(0xFFFF9800),
                    onChanged: (value) => setState(() => _isAnonymous = value),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 32),
            
            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFFFF9800),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 2,
                ),
                onPressed: _isSubmitting ? null : _submitFeedback,
                child: _isSubmitting
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: 12),
                          Text('Submitting...'),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.send),
                          SizedBox(width: 8),
                          Text(
                            'Submit Feedback',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
              ),
            ),
            
            SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  String _getRatingLabel(int rating) {
    switch (rating) {
      case 1:
        return 'Poor';
      case 2:
        return 'Fair';
      case 3:
        return 'Good';
      case 4:
        return 'Very Good';
      case 5:
        return 'Excellent!';
      default:
        return 'Tap a star to rate';
    }
  }
}

/// Quick feedback button widget for embedding in other screens
class QuickFeedbackButton extends StatelessWidget {
  final String? category;
  final int? facilityId;
  final int? roomId;

  const QuickFeedbackButton({
    super.key,
    this.category,
    this.facilityId,
    this.roomId,
  });

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.small(
      heroTag: 'feedback',
      backgroundColor: Colors.white,
      foregroundColor: Color(0xFFFF9800),
      onPressed: () => _showQuickFeedbackDialog(context),
      child: Icon(Icons.feedback),
    );
  }

  void _showQuickFeedbackDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text('Quick Feedback'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('How was your experience?'),
            SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(5, (index) {
                return IconButton(
                  iconSize: 32,
                  onPressed: () {
                    Navigator.pop(context);
                    _submitQuickFeedback(context, index + 1);
                  },
                  icon: Icon(Icons.star_border, color: Colors.amber),
                );
              }),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => FeedbackSubmissionScreen(
                    preSelectedCategory: category,
                    facilityId: facilityId,
                    roomId: roomId,
                  ),
                ),
              );
            },
            child: Text('Detailed Feedback'),
          ),
        ],
      ),
    );
  }

  void _submitQuickFeedback(BuildContext context, int rating) async {
    try {
      final db = DatabaseHelper.instance;
      await db.insertRating({
        'facility_id': facilityId,
        'room_id': roomId,
        'rating': rating,
        'comment': 'Quick feedback - $rating stars',
        'category': category ?? 'general',
        'is_anonymous': 1,
      });
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Thank you for your feedback!')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error submitting feedback')),
        );
      }
    }
  }
}
