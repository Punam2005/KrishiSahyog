
# database_models.py - SQLAlchemy Database Models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Field(db.Model):
    """Model for agricultural fields"""
    __tablename__ = 'fields'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))  # GPS coordinates or address
    area = db.Column(db.String(50))  # e.g., "25.3 hectares"
    crop_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Unknown')  # Excellent, Healthy, Attention Needed, Poor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hyperspectral_images = db.relationship('HyperspectralImage', backref='field', lazy=True)
    health_analyses = db.relationship('HealthAnalysis', backref='field', lazy=True)
    pest_detections = db.relationship('PestDetection', backref='field', lazy=True)
    soil_analyses = db.relationship('SoilAnalysis', backref='field', lazy=True)

    def __repr__(self):
        return f'<Field {self.name}>'

class HyperspectralImage(db.Model):
    """Model for hyperspectral images"""
    __tablename__ = 'hyperspectral_images'

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger)
    processing_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    metadata = db.Column(db.JSON)  # Store image metadata (bands, resolution, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    # Relationships
    health_analyses = db.relationship('HealthAnalysis', backref='hyperspectral_image', lazy=True)
    pest_detections = db.relationship('PestDetection', backref='hyperspectral_image', lazy=True)
    soil_analyses = db.relationship('SoilAnalysis', backref='hyperspectral_image', lazy=True)

    def __repr__(self):
        return f'<HyperspectralImage {self.filename}>'

class HealthAnalysis(db.Model):
    """Model for crop health analysis results"""
    __tablename__ = 'health_analyses'

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('hyperspectral_images.id'), nullable=False)

    # Health metrics (0-100 scale)
    chlorophyll_content = db.Column(db.Float)
    water_stress = db.Column(db.Float)
    nutrient_deficiency = db.Column(db.Float)
    disease_risk = db.Column(db.Float)
    overall_score = db.Column(db.Float)

    # Spectral indices as JSON
    spectral_indices = db.Column(db.JSON)  # NDVI, EVI, SAVI, etc.

    # Analysis details
    analysis_method = db.Column(db.String(100), default='hyperspectral_ml')
    confidence_score = db.Column(db.Float)
    recommendations = db.Column(db.JSON)  # Array of recommendation strings

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HealthAnalysis Field:{self.field_id} Score:{self.overall_score}>'

class PestDetection(db.Model):
    """Model for pest and disease detection results"""
    __tablename__ = 'pest_detections'

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('hyperspectral_images.id'), nullable=False)

    # Detection details
    pest_type = db.Column(db.String(100), nullable=False)  # e.g., "Aphids", "Corn Borer", "Leaf Rust"
    confidence = db.Column(db.Float)  # 0-1 confidence score
    severity = db.Column(db.String(20))  # Low, Medium, High, Critical

    # Location within image (normalized coordinates 0-1)
    location_x = db.Column(db.Float)
    location_y = db.Column(db.Float)

    # Detection metadata
    detection_method = db.Column(db.String(100), default='hyperspectral_cnn')
    bounding_box = db.Column(db.JSON)  # For storing detection area

    # Treatment information
    recommendation = db.Column(db.Text)
    treatment_urgency = db.Column(db.String(20))  # Immediate, Within 24h, Within Week, Monitor

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PestDetection {self.pest_type} Severity:{self.severity}>'

class SoilAnalysis(db.Model):
    """Model for soil condition analysis results"""
    __tablename__ = 'soil_analyses'

    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('hyperspectral_images.id'), nullable=False)

    # Soil properties
    ph_level = db.Column(db.Float)
    organic_matter = db.Column(db.Float)  # Percentage
    moisture_content = db.Column(db.Float)  # Percentage

    # Nutrient levels (0-100 scale)
    nitrogen_level = db.Column(db.Float)
    phosphorus_level = db.Column(db.Float)
    potassium_level = db.Column(db.Float)

    # Additional soil properties
    soil_temperature = db.Column(db.Float)
    salinity_level = db.Column(db.Float)
    compaction_index = db.Column(db.Float)

    # Analysis metadata
    analysis_method = db.Column(db.String(100), default='hyperspectral_regression')
    confidence_score = db.Column(db.Float)

    # Recommendations
    recommendations = db.Column(db.JSON)  # Array of soil management recommendations

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SoilAnalysis Field:{self.field_id} pH:{self.ph_level}>'

class ProcessingJob(db.Model):
    """Model for tracking long-running processing jobs"""
    __tablename__ = 'processing_jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = db.Column(db.String(50), nullable=False)  # hyperspectral_analysis, bulk_processing
    status = db.Column(db.String(20), default='queued')  # queued, running, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100

    # Job parameters
    parameters = db.Column(db.JSON)

    # Results and error handling
    result = db.Column(db.JSON)
    error_message = db.Column(db.Text)

    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<ProcessingJob {self.job_type} Status:{self.status}>'

class User(db.Model):
    """Model for system users (optional - for authentication)"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='researcher')  # admin, researcher, viewer

    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    organization = db.Column(db.String(100))

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

# Database initialization functions
def init_database():
    """Initialize database with sample data"""
    db.create_all()

    # Create sample fields if none exist
    if Field.query.count() == 0:
        sample_fields = [
            Field(
                name="North Field A",
                location="40.7128, -74.0060",
                area="25.3 hectares",
                crop_type="Corn",
                status="Healthy"
            ),
            Field(
                name="South Field B", 
                location="40.7589, -73.9851",
                area="18.7 hectares",
                crop_type="Wheat",
                status="Attention Needed"
            ),
            Field(
                name="East Field C",
                location="40.6892, -74.0445", 
                area="31.2 hectares",
                crop_type="Soybeans",
                status="Excellent"
            )
        ]

        for field in sample_fields:
            db.session.add(field)

        db.session.commit()
        print("Sample fields created successfully!")

def create_indexes():
    """Create database indexes for better performance"""
    # These would be created as SQL commands or using Alembic migrations
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_hyperspectral_images_field_id ON hyperspectral_images(field_id);",
        "CREATE INDEX IF NOT EXISTS idx_hyperspectral_images_created_at ON hyperspectral_images(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_health_analyses_field_id ON health_analyses(field_id);",
        "CREATE INDEX IF NOT EXISTS idx_health_analyses_created_at ON health_analyses(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_pest_detections_field_id ON pest_detections(field_id);",
        "CREATE INDEX IF NOT EXISTS idx_pest_detections_severity ON pest_detections(severity);",
        "CREATE INDEX IF NOT EXISTS idx_soil_analyses_field_id ON soil_analyses(field_id);",
        "CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);"
    ]

    for index_sql in indexes:
        try:
            db.engine.execute(index_sql)
        except Exception as e:
            print(f"Error creating index: {e}")
