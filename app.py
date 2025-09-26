
# app.py - Main Flask Application
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import numpy as np
import cv2
from PIL import Image
import io
import json
from datetime import datetime, timedelta
import logging
from hyperspectral_processor import HyperspectralProcessor
from ai_models import CropHealthAnalyzer, PestDetector, SoilAnalyzer
from database_models import db, Field, HyperspectralImage, HealthAnalysis, PestDetection, SoilAnalysis
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/cropscope_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize extensions
CORS(app)
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize processors
hyperspectral_processor = HyperspectralProcessor()
crop_health_analyzer = CropHealthAnalyzer()
pest_detector = PestDetector()
soil_analyzer = SoilAnalyzer()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'raw', 'hdr', 'img', 'bil', 'bip', 'bsq', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/fields', methods=['GET'])
def get_fields():
    """Get all fields with their latest analysis results"""
    try:
        fields = Field.query.all()
        fields_data = []

        for field in fields:
            latest_image = HyperspectralImage.query.filter_by(field_id=field.id).order_by(
                HyperspectralImage.created_at.desc()
            ).first()

            latest_health = HealthAnalysis.query.filter_by(field_id=field.id).order_by(
                HealthAnalysis.created_at.desc()
            ).first()

            pest_alerts = PestDetection.query.filter_by(field_id=field.id).filter(
                PestDetection.severity.in_(['High', 'Medium'])
            ).count()

            field_data = {
                'id': field.id,
                'name': field.name,
                'location': field.location,
                'area': field.area,
                'crop_type': field.crop_type,
                'last_scan': latest_image.created_at.isoformat() if latest_image else None,
                'health_score': latest_health.overall_score if latest_health else 0,
                'status': field.status,
                'alerts': pest_alerts
            }
            fields_data.append(field_data)

        return jsonify({
            'success': True,
            'fields': fields_data,
            'total_fields': len(fields_data)
        })
    except Exception as e:
        logger.error(f"Error getting fields: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fields/<int:field_id>/upload', methods=['POST'])
def upload_hyperspectral_image(field_id):
    """Upload and process hyperspectral image for a field"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400

        # Verify field exists
        field = Field.query.get(field_id)
        if not field:
            return jsonify({'success': False, 'error': 'Field not found'}), 404

        # Save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)

        # Create database record
        hyperspectral_image = HyperspectralImage(
            field_id=field_id,
            filename=unique_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            processing_status='pending'
        )
        db.session.add(hyperspectral_image)
        db.session.commit()

        # Process the hyperspectral image
        process_hyperspectral_image_async(hyperspectral_image.id, file_path, field_id)

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'image_id': hyperspectral_image.id,
            'status': 'processing'
        })

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def process_hyperspectral_image_async(image_id, file_path, field_id):
    """Process hyperspectral image and extract insights"""
    try:
        # Update processing status
        hyperspectral_image = HyperspectralImage.query.get(image_id)
        hyperspectral_image.processing_status = 'processing'
        db.session.commit()

        # Process hyperspectral data
        logger.info(f"Processing hyperspectral image: {file_path}")

        # Load and preprocess hyperspectral data
        processed_data = hyperspectral_processor.load_and_preprocess(file_path)

        # Extract spectral indices
        spectral_indices = hyperspectral_processor.calculate_spectral_indices(processed_data)

        # Analyze crop health
        health_results = crop_health_analyzer.analyze(processed_data, spectral_indices)

        # Detect pests and diseases
        pest_results = pest_detector.detect(processed_data)

        # Analyze soil conditions
        soil_results = soil_analyzer.analyze(processed_data)

        # Save health analysis results
        health_analysis = HealthAnalysis(
            field_id=field_id,
            image_id=image_id,
            chlorophyll_content=health_results['chlorophyll_content'],
            water_stress=health_results['water_stress'],
            nutrient_deficiency=health_results['nutrient_deficiency'],
            disease_risk=health_results['disease_risk'],
            overall_score=health_results['overall_score'],
            spectral_indices=json.dumps(spectral_indices),
            recommendations=json.dumps(health_results['recommendations'])
        )
        db.session.add(health_analysis)

        # Save pest detection results
        for pest in pest_results:
            pest_detection = PestDetection(
                field_id=field_id,
                image_id=image_id,
                pest_type=pest['type'],
                confidence=pest['confidence'],
                severity=pest['severity'],
                location_x=pest.get('location_x', 0),
                location_y=pest.get('location_y', 0),
                recommendation=pest['recommendation']
            )
            db.session.add(pest_detection)

        # Save soil analysis results
        soil_analysis = SoilAnalysis(
            field_id=field_id,
            image_id=image_id,
            ph_level=soil_results['ph_level'],
            organic_matter=soil_results['organic_matter'],
            moisture_content=soil_results['moisture_content'],
            nitrogen_level=soil_results['nitrogen_level'],
            phosphorus_level=soil_results['phosphorus_level'],
            potassium_level=soil_results['potassium_level'],
            recommendations=json.dumps(soil_results['recommendations'])
        )
        db.session.add(soil_analysis)

        # Update processing status
        hyperspectral_image.processing_status = 'completed'
        hyperspectral_image.processed_at = datetime.utcnow()

        # Update field status based on analysis results
        if health_results['overall_score'] >= 80:
            field_status = 'Excellent'
        elif health_results['overall_score'] >= 60:
            field_status = 'Healthy' if len([p for p in pest_results if p['severity'] == 'High']) == 0 else 'Attention Needed'
        else:
            field_status = 'Poor'

        field = Field.query.get(field_id)
        field.status = field_status

        db.session.commit()
        logger.info(f"Successfully processed hyperspectral image: {image_id}")

    except Exception as e:
        logger.error(f"Error processing hyperspectral image {image_id}: {str(e)}")

        # Update status to failed
        hyperspectral_image = HyperspectralImage.query.get(image_id)
        hyperspectral_image.processing_status = 'failed'
        hyperspectral_image.error_message = str(e)
        db.session.commit()

@app.route('/api/fields/<int:field_id>/health', methods=['GET'])
def get_field_health(field_id):
    """Get health analysis for a specific field"""
    try:
        field = Field.query.get(field_id)
        if not field:
            return jsonify({'success': False, 'error': 'Field not found'}), 404

        latest_analysis = HealthAnalysis.query.filter_by(field_id=field_id).order_by(
            HealthAnalysis.created_at.desc()
        ).first()

        if not latest_analysis:
            return jsonify({'success': False, 'error': 'No health analysis available'}), 404

        spectral_indices = json.loads(latest_analysis.spectral_indices) if latest_analysis.spectral_indices else {}
        recommendations = json.loads(latest_analysis.recommendations) if latest_analysis.recommendations else []

        return jsonify({
            'success': True,
            'health_analysis': {
                'id': latest_analysis.id,
                'field_name': field.name,
                'analysis_date': latest_analysis.created_at.isoformat(),
                'chlorophyll_content': latest_analysis.chlorophyll_content,
                'water_stress': latest_analysis.water_stress,
                'nutrient_deficiency': latest_analysis.nutrient_deficiency,
                'disease_risk': latest_analysis.disease_risk,
                'overall_score': latest_analysis.overall_score,
                'spectral_indices': spectral_indices,
                'recommendations': recommendations
            }
        })

    except Exception as e:
        logger.error(f"Error getting field health: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fields/<int:field_id>/pests', methods=['GET'])
def get_field_pests(field_id):
    """Get pest detection results for a specific field"""
    try:
        field = Field.query.get(field_id)
        if not field:
            return jsonify({'success': False, 'error': 'Field not found'}), 404

        pest_detections = PestDetection.query.filter_by(field_id=field_id).order_by(
            PestDetection.created_at.desc()
        ).limit(10).all()

        pests_data = []
        for detection in pest_detections:
            pest_data = {
                'id': detection.id,
                'pest_type': detection.pest_type,
                'confidence': detection.confidence,
                'severity': detection.severity,
                'detected_date': detection.created_at.isoformat(),
                'location_x': detection.location_x,
                'location_y': detection.location_y,
                'recommendation': detection.recommendation
            }
            pests_data.append(pest_data)

        return jsonify({
            'success': True,
            'field_name': field.name,
            'pest_detections': pests_data,
            'total_detections': len(pests_data)
        })

    except Exception as e:
        logger.error(f"Error getting field pests: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fields/<int:field_id>/soil', methods=['GET'])
def get_field_soil(field_id):
    """Get soil analysis for a specific field"""
    try:
        field = Field.query.get(field_id)
        if not field:
            return jsonify({'success': False, 'error': 'Field not found'}), 404

        latest_soil_analysis = SoilAnalysis.query.filter_by(field_id=field_id).order_by(
            SoilAnalysis.created_at.desc()
        ).first()

        if not latest_soil_analysis:
            return jsonify({'success': False, 'error': 'No soil analysis available'}), 404

        recommendations = json.loads(latest_soil_analysis.recommendations) if latest_soil_analysis.recommendations else []

        return jsonify({
            'success': True,
            'soil_analysis': {
                'id': latest_soil_analysis.id,
                'field_name': field.name,
                'analysis_date': latest_soil_analysis.created_at.isoformat(),
                'ph_level': latest_soil_analysis.ph_level,
                'organic_matter': latest_soil_analysis.organic_matter,
                'moisture_content': latest_soil_analysis.moisture_content,
                'nitrogen_level': latest_soil_analysis.nitrogen_level,
                'phosphorus_level': latest_soil_analysis.phosphorus_level,
                'potassium_level': latest_soil_analysis.potassium_level,
                'recommendations': recommendations
            }
        })

    except Exception as e:
        logger.error(f"Error getting field soil: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_fields = Field.query.count()

        # Calculate average health score
        health_analyses = HealthAnalysis.query.all()
        avg_health_score = sum([h.overall_score for h in health_analyses]) / len(health_analyses) if health_analyses else 0

        # Count active alerts (high and medium severity pests)
        active_alerts = PestDetection.query.filter(
            PestDetection.severity.in_(['High', 'Medium'])
        ).count()

        # Count recent scans (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = HyperspectralImage.query.filter(
            HyperspectralImage.created_at >= week_ago
        ).count()

        # Get health trend data (last 30 days)
        month_ago = datetime.utcnow() - timedelta(days=30)
        trend_analyses = HealthAnalysis.query.filter(
            HealthAnalysis.created_at >= month_ago
        ).order_by(HealthAnalysis.created_at.asc()).all()

        trend_data = []
        for analysis in trend_analyses:
            trend_data.append({
                'date': analysis.created_at.strftime('%Y-%m-%d'),
                'score': analysis.overall_score
            })

        return jsonify({
            'success': True,
            'stats': {
                'total_fields': total_fields,
                'avg_health_score': round(avg_health_score, 1),
                'active_alerts': active_alerts,
                'recent_scans': recent_scans,
                'health_trend': trend_data
            }
        })

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/export', methods=['POST'])
def export_report():
    """Export analysis report for specified fields and date range"""
    try:
        data = request.json
        field_ids = data.get('field_ids', [])
        start_date = datetime.fromisoformat(data.get('start_date'))
        end_date = datetime.fromisoformat(data.get('end_date'))
        report_type = data.get('report_type', 'summary')

        # Generate report based on type
        if report_type == 'summary':
            report_data = generate_summary_report(field_ids, start_date, end_date)
        elif report_type == 'detailed':
            report_data = generate_detailed_report(field_ids, start_date, end_date)
        else:
            return jsonify({'success': False, 'error': 'Invalid report type'}), 400

        return jsonify({
            'success': True,
            'report': report_data
        })

    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_summary_report(field_ids, start_date, end_date):
    """Generate summary report for specified fields and date range"""
    report_data = {
        'title': 'Crop Health Summary Report',
        'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'fields': []
    }

    for field_id in field_ids:
        field = Field.query.get(field_id)
        if not field:
            continue

        # Get analyses within date range
        analyses = HealthAnalysis.query.filter(
            HealthAnalysis.field_id == field_id,
            HealthAnalysis.created_at >= start_date,
            HealthAnalysis.created_at <= end_date
        ).all()

        if analyses:
            avg_health = sum([a.overall_score for a in analyses]) / len(analyses)

            field_data = {
                'name': field.name,
                'crop_type': field.crop_type,
                'area': field.area,
                'total_scans': len(analyses),
                'avg_health_score': round(avg_health, 1),
                'status': field.status
            }
            report_data['fields'].append(field_data)

    return report_data

def generate_detailed_report(field_ids, start_date, end_date):
    """Generate detailed report for specified fields and date range"""
    report_data = {
        'title': 'Detailed Crop Analysis Report',
        'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'fields': []
    }

    for field_id in field_ids:
        field = Field.query.get(field_id)
        if not field:
            continue

        # Get all analyses within date range
        health_analyses = HealthAnalysis.query.filter(
            HealthAnalysis.field_id == field_id,
            HealthAnalysis.created_at >= start_date,
            HealthAnalysis.created_at <= end_date
        ).all()

        pest_detections = PestDetection.query.filter(
            PestDetection.field_id == field_id,
            PestDetection.created_at >= start_date,
            PestDetection.created_at <= end_date
        ).all()

        soil_analyses = SoilAnalysis.query.filter(
            SoilAnalysis.field_id == field_id,
            SoilAnalysis.created_at >= start_date,
            SoilAnalysis.created_at <= end_date
        ).all()

        field_data = {
            'name': field.name,
            'crop_type': field.crop_type,
            'area': field.area,
            'health_analyses': [
                {
                    'date': h.created_at.isoformat(),
                    'overall_score': h.overall_score,
                    'chlorophyll_content': h.chlorophyll_content,
                    'water_stress': h.water_stress,
                    'nutrient_deficiency': h.nutrient_deficiency,
                    'disease_risk': h.disease_risk
                } for h in health_analyses
            ],
            'pest_detections': [
                {
                    'date': p.created_at.isoformat(),
                    'pest_type': p.pest_type,
                    'severity': p.severity,
                    'confidence': p.confidence
                } for p in pest_detections
            ],
            'soil_analyses': [
                {
                    'date': s.created_at.isoformat(),
                    'ph_level': s.ph_level,
                    'organic_matter': s.organic_matter,
                    'moisture_content': s.moisture_content
                } for s in soil_analyses
            ]
        }
        report_data['fields'].append(field_data)

    return report_data

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
