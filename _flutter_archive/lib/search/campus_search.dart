import 'package:flutter/material.dart';
import '../database_helper_v2.dart';
import '../map/campus_map_screen.dart';

/// Search Bar Widget for Home Screen
/// Allows users to quickly search for rooms and facilities
class CampusSearchWidget extends StatefulWidget {
  final VoidCallback? onSearchComplete;

  const CampusSearchWidget({super.key, this.onSearchComplete});

  @override
  State<CampusSearchWidget> createState() => _CampusSearchWidgetState();
}

class _CampusSearchWidgetState extends State<CampusSearchWidget> {
  final DatabaseHelper _db = DatabaseHelper.instance;
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  
  List<Map<String, dynamic>> _searchResults = [];
  bool _isSearching = false;
  bool _hasSearched = false;

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _performSearch(String query) async {
    if (query.trim().isEmpty) {
      setState(() {
        _searchResults = [];
        _hasSearched = false;
      });
      return;
    }

    setState(() => _isSearching = true);

    try {
      final results = await _db.searchFacilitiesAndRooms(query);
      
      // Log the search
      await _db.logSearch(query, results.length);

      setState(() {
        _searchResults = results;
        _isSearching = false;
        _hasSearched = true;
      });
    } catch (e) {
      setState(() => _isSearching = false);
    }
  }

  void _onResultTap(Map<String, dynamic> result) {
    _focusNode.unfocus();
    widget.onSearchComplete?.call();

    final resultType = result['result_type'] as String;
    
    if (resultType == 'facility') {
      // Navigate to map showing facility
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => CampusMapScreen(
            destinationFacilityId: result['id'] as int,
          ),
        ),
      );
    } else if (resultType == 'room') {
      // Navigate to map showing room location
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => CampusMapScreen(
            destinationFacilityId: result['facility_id'] as int,
            destinationRoomId: result['id'] as int,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search Bar
        Container(
          margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 10,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: TextField(
            controller: _searchController,
            focusNode: _focusNode,
            decoration: InputDecoration(
              hintText: 'Search rooms, buildings, or facilities...',
              prefixIcon: Icon(Icons.search, color: Color(0xFFFF9800)),
              suffixIcon: _searchController.text.isNotEmpty
                  ? IconButton(
                      icon: Icon(Icons.clear, color: Colors.grey),
                      onPressed: () {
                        _searchController.clear();
                        setState(() {
                          _searchResults = [];
                          _hasSearched = false;
                        });
                      },
                    )
                  : null,
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            ),
            onChanged: (query) {
              setState(() {});
              if (query.length >= 2) {
                _performSearch(query);
              }
            },
            onSubmitted: _performSearch,
          ),
        ),

        // Search Results
        if (_isSearching)
          Padding(
            padding: EdgeInsets.all(16),
            child: CircularProgressIndicator(),
          )
        else if (_hasSearched && _searchResults.isEmpty)
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                Icon(Icons.search_off, size: 48, color: Colors.grey[400]),
                SizedBox(height: 8),
                Text(
                  'No results found',
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          )
        else if (_searchResults.isNotEmpty)
          Container(
            margin: EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 10,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            constraints: BoxConstraints(maxHeight: 300),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _searchResults.length,
              itemBuilder: (context, index) {
                final result = _searchResults[index];
                final isFacility = result['result_type'] == 'facility';
                
                return ListTile(
                  leading: Container(
                    padding: EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: isFacility 
                          ? Colors.blue.withValues(alpha: 0.1) 
                          : Colors.green.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      isFacility ? Icons.business : Icons.meeting_room,
                      color: isFacility ? Colors.blue : Colors.green,
                    ),
                  ),
                  title: Text(result['name'] as String),
                  subtitle: Text(
                    isFacility 
                        ? result['description'] as String? ?? 'Facility'
                        : '${result['facility_name'] ?? 'Building'} • Room ${result['room_number'] ?? ''}',
                  ),
                  trailing: Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
                  onTap: () => _onResultTap(result),
                );
              },
            ),
          ),

        // Quick Suggestions (when not searching)
        if (!_hasSearched && _searchController.text.isEmpty)
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Popular Searches',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey[700]),
                ),
                SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    'MST Building',
                    'Library',
                    'Computer Lab',
                    'Registrar',
                    'Cafeteria',
                    'Comfort Room',
                  ].map((term) => ActionChip(
                    label: Text(term, style: TextStyle(fontSize: 12)),
                    backgroundColor: Colors.grey[100],
                    onPressed: () {
                      _searchController.text = term;
                      _performSearch(term);
                    },
                  )).toList(),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

/// Floating Search Button for easy access
class FloatingSearchButton extends StatelessWidget {
  const FloatingSearchButton({super.key});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      heroTag: 'search',
      backgroundColor: Colors.white,
      foregroundColor: Color(0xFFFF9800),
      onPressed: () => _showSearchBottomSheet(context),
      icon: Icon(Icons.search),
      label: Text('Search'),
    );
  }

  void _showSearchBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                Container(
                  margin: EdgeInsets.only(top: 8),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.search, color: Color(0xFFFF9800), size: 28),
                      SizedBox(width: 12),
                      Text(
                        'Search Campus',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: CampusSearchWidget(
                    onSearchComplete: () => Navigator.pop(context),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
