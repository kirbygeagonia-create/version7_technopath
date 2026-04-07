import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'dart:convert';

/// QR Code Access Point Screen
/// Scans QR codes at the main gate to quickly load the campus map
class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  bool _isScanning = true;
  bool _flashOn = false;
  String? _lastScannedCode;
  final MobileScannerController _controller = MobileScannerController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (!_isScanning) return;

    final List<Barcode> barcodes = capture.barcodes;
    
    for (final barcode in barcodes) {
      final String? rawValue = barcode.rawValue;
      if (rawValue != null && rawValue != _lastScannedCode) {
        _lastScannedCode = rawValue;
        _processQRCode(rawValue);
        break;
      }
    }
  }

  void _processQRCode(String code) {
    setState(() => _isScanning = false);

    try {
      // Try to parse as JSON (structured campus data)
      final data = jsonDecode(code);
      _showCampusEntryDialog(data);
    } catch (e) {
      // Treat as plain text/URL
      if (code.startsWith('seait://') || code.toLowerCase().contains('campus')) {
        _showCampusEntryDialog({'type': 'campus_entry', 'location': code});
      } else {
        _showInvalidQRDialog(code);
      }
    }
  }

  void _showCampusEntryDialog(Map<String, dynamic> data) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 28),
            SizedBox(width: 8),
            Text('Campus Access Granted'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome to SEAIT Campus!',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            SizedBox(height: 12),
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Color(0xFFFF9800).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.location_on, color: Color(0xFFFF9800), size: 20),
                      SizedBox(width: 8),
                      Text('Entry Point: Main Gate', style: TextStyle(fontWeight: FontWeight.w600)),
                    ],
                  ),
                  SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.access_time, color: Color(0xFFFF9800), size: 20),
                      SizedBox(width: 8),
                      Text('Time: ${_getCurrentTime()}'),
                    ],
                  ),
                ],
              ),
            ),
            SizedBox(height: 16),
            Text(
              'The campus guide map will now load with navigation starting from the main gate.',
              style: TextStyle(fontSize: 14, color: Colors.grey[700]),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _isScanning = true;
                _lastScannedCode = null;
              });
            },
            child: Text('Scan Again'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Color(0xFFFF9800),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () {
              Navigator.pop(context);
              _launchCampusMap();
            },
            child: Text('Open Campus Map'),
          ),
        ],
      ),
    );
  }

  void _showInvalidQRDialog(String code) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Icon(Icons.error, color: Colors.red, size: 28),
            SizedBox(width: 8),
            Text('Invalid QR Code'),
          ],
        ),
        content: Text(
          'The scanned code does not appear to be a valid SEAIT campus access code. Please scan the QR code at the main gate entrance.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _isScanning = true;
                _lastScannedCode = null;
              });
            },
            child: Text('Try Again'),
          ),
        ],
      ),
    );
  }

  void _launchCampusMap() {
    // Return to main screen with signal to open map at main gate
    Navigator.pop(context, {'action': 'open_map', 'entry_point': 'main_gate'});
  }

  String _getCurrentTime() {
    final now = DateTime.now();
    return '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
  }

  void _toggleFlash() {
    setState(() => _flashOn = !_flashOn);
    _controller.toggleTorch();
  }

  void _switchCamera() {
    _controller.switchCamera();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Scan Campus QR Code'),
        backgroundColor: Color(0xFFFF9800),
        actions: [
          IconButton(
            icon: Icon(_flashOn ? Icons.flash_on : Icons.flash_off),
            onPressed: _toggleFlash,
          ),
          IconButton(
            icon: Icon(Icons.cameraswitch),
            onPressed: _switchCamera,
          ),
        ],
      ),
      body: Column(
        children: [
          // Instructions
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(16),
            color: Color(0xFFFF9800).withValues(alpha: 0.1),
            child: Column(
              children: [
                Icon(Icons.qr_code_scanner, size: 48, color: Color(0xFFFF9800)),
                SizedBox(height: 8),
                Text(
                  'Scan the QR code at the Main Gate',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 4),
                Text(
                  'Point your camera at the campus access QR code',
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          
          // Scanner
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                MobileScanner(
                  controller: _controller,
                  onDetect: _onDetect,
                  fit: BoxFit.cover,
                ),
                
                // Scan overlay
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: _isScanning ? Color(0xFFFF9800) : Colors.grey,
                      width: 4,
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  width: 250,
                  height: 250,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Corner markers
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildCornerMarker(true, true),
                          _buildCornerMarker(false, true),
                        ],
                      ),
                      // Center animation
                      if (_isScanning)
                        Container(
                          height: 2,
                          color: Color(0xFFFF9800).withValues(alpha: 0.8),
                        ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildCornerMarker(true, false),
                          _buildCornerMarker(false, false),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Status text
                Positioned(
                  bottom: 40,
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.7),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      _isScanning ? 'Scanning...' : 'Processing...',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Help section
          Container(
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  'Need Help?',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 8),
                Text(
                  'If you\'re having trouble scanning, make sure the QR code is clearly visible and well-lit. You can also tap the flashlight button above.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
                SizedBox(height: 16),
                TextButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: Icon(Icons.arrow_back),
                  label: Text('Skip for now'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCornerMarker(bool isLeft, bool isTop) {
    return Container(
      width: 30,
      height: 30,
      decoration: BoxDecoration(
        border: Border(
          left: isLeft ? BorderSide(color: Color(0xFFFF9800), width: 4) : BorderSide.none,
          right: !isLeft ? BorderSide(color: Color(0xFFFF9800), width: 4) : BorderSide.none,
          top: isTop ? BorderSide(color: Color(0xFFFF9800), width: 4) : BorderSide.none,
          bottom: !isTop ? BorderSide(color: Color(0xFFFF9800), width: 4) : BorderSide.none,
        ),
      ),
    );
  }
}

/// Widget to generate a SEAIT Campus QR Code
/// Used for creating the physical QR code at the main gate
class CampusQRCodeGenerator extends StatelessWidget {
  final String data;
  final double size;

  const CampusQRCodeGenerator({
    super.key,
    this.data = '{"type":"campus_entry","location":"seait_main_gate","version":"1.0"}',
    this.size = 200,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // QR Code placeholder - in real implementation, use qr_flutter package
          Container(
            width: size - 60,
            height: size - 60,
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: Colors.black, width: 2),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.qr_code_2, size: 60, color: Colors.black),
                  SizedBox(height: 8),
                  Text(
                    'SEAIT\nCAMPUS',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Scan to enter',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
