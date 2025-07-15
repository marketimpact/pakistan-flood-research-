#!/usr/bin/env python3
"""
Enhanced Django Models for Pakistan Flood Early Warning System (Pak-FEWS)
Comprehensive models supporting all Google Flood Hub APIs
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
import json

class GaugeClassification(models.TextChoices):
    """Classification types for river gauges"""
    VERIFIED_PHYSICAL = 'verified_physical', 'Verified Physical'
    LIKELY_PHYSICAL = 'likely_physical', 'Likely Physical'
    UNCERTAIN = 'uncertain', 'Uncertain'
    LIKELY_VIRTUAL = 'likely_virtual', 'Likely Virtual'

class GaugeSource(models.TextChoices):
    """Data sources for gauges"""
    GRDC = 'GRDC', 'Global Runoff Data Centre'
    WAPDA = 'WAPDA', 'Water and Power Development Authority'
    PMD = 'PMD', 'Pakistan Meteorological Department'
    FFD = 'FFD', 'Federal Flood Division'
    HYBAS = 'HYBAS', 'HydroBASINS'
    NDMA = 'NDMA', 'National Disaster Management Authority'
    CWC = 'CWC', 'Central Water Commission'
    OTHER = 'OTHER', 'Other Source'

class GaugeValueUnit(models.TextChoices):
    """Gauge value units"""
    GAUGE_VALUE_UNIT_UNSPECIFIED = 'GAUGE_VALUE_UNIT_UNSPECIFIED', 'Unspecified'
    METERS = 'METERS', 'Meters'
    CUBIC_METERS_PER_SECOND = 'CUBIC_METERS_PER_SECOND', 'Cubic Meters per Second'

class FloodSeverity(models.TextChoices):
    """Flood severity levels"""
    SEVERITY_UNSPECIFIED = 'SEVERITY_UNSPECIFIED', 'Unspecified'
    EXTREME = 'EXTREME', 'Extreme'
    SEVERE = 'SEVERE', 'Severe'
    ABOVE_NORMAL = 'ABOVE_NORMAL', 'Above Normal'
    NO_FLOODING = 'NO_FLOODING', 'No Flooding'
    UNKNOWN = 'UNKNOWN', 'Unknown'

class ForecastTrend(models.TextChoices):
    """Forecast trend indicators"""
    FORECAST_TREND_UNSPECIFIED = 'FORECAST_TREND_UNSPECIFIED', 'Unspecified'
    RISE = 'RISE', 'Rising'
    FALL = 'FALL', 'Falling'
    NO_CHANGE = 'NO_CHANGE', 'No Change'

class MapInferenceType(models.TextChoices):
    """Map inference types"""
    MAP_INFERENCE_TYPE_UNSPECIFIED = 'MAP_INFERENCE_TYPE_UNSPECIFIED', 'Unspecified'
    MODEL = 'MODEL', 'Model-based'
    IMAGE_CLASSIFICATION = 'IMAGE_CLASSIFICATION', 'Image Classification'

class InundationMapType(models.TextChoices):
    """Inundation map types"""
    INUNDATION_MAP_TYPE_UNSPECIFIED = 'INUNDATION_MAP_TYPE_UNSPECIFIED', 'Unspecified'
    PROBABILITY = 'PROBABILITY', 'Probability Map'
    DEPTH = 'DEPTH', 'Depth Map'

class ReliabilityTier(models.TextChoices):
    """Reliability tiers for alert system"""
    TIER_1_HIGHEST = 'tier_1_highest', 'Tier 1 (Highest Reliability)'
    TIER_2_HIGH = 'tier_2_high', 'Tier 2 (High Reliability)'
    TIER_3_MEDIUM = 'tier_3_medium', 'Tier 3 (Medium Reliability)'
    TIER_4_LOW = 'tier_4_low', 'Tier 4 (Low Reliability)'

class RiverGauge(models.Model):
    """Enhanced model for river gauge information"""
    
    # Core identification (from gauges API)
    gauge_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique identifier from Google Flood Hub API"
    )
    
    # Location
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(23.0), MaxValueValidator(38.0)],
        help_text="Latitude coordinate (Pakistan bounds: 23-38°N)"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7,
        validators=[MinValueValidator(60.0), MaxValueValidator(78.0)],
        help_text="Longitude coordinate (Pakistan bounds: 60-78°E)"
    )
    
    # Gauge metadata (from gauges API)
    source = models.CharField(
        max_length=20,
        choices=GaugeSource.choices,
        default=GaugeSource.OTHER
    )
    site_name = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Name of the gauge site (if available)"
    )
    river = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Name of the river (if available)"
    )
    country_code = models.CharField(
        max_length=2,
        default='PK',
        help_text="ISO 3166 Alpha-2 country code"
    )
    
    # Google Flood Hub metadata
    quality_verified = models.BooleanField(
        default=False,
        help_text="Quality verified by Google Flood Hub"
    )
    has_model = models.BooleanField(
        default=False,
        help_text="Has flood prediction model available"
    )
    
    # Classification system
    classification = models.CharField(
        max_length=20,
        choices=GaugeClassification.choices,
        default=GaugeClassification.UNCERTAIN
    )
    confidence_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence score for classification (0-100)"
    )
    evidence = models.TextField(
        blank=True,
        help_text="Evidence used for classification decision"
    )
    
    # External validation
    external_match_found = models.BooleanField(
        default=False,
        help_text="Found matching station in external Pakistani databases"
    )
    external_match_distance = models.FloatField(
        null=True, 
        blank=True,
        help_text="Distance to nearest external station (km)"
    )
    external_match_source = models.CharField(
        max_length=20,
        blank=True,
        help_text="Source of external match (WAPDA, PMD, etc.)"
    )
    external_match_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed external validation data"
    )
    
    # Reliability assessment
    reliability_tier = models.CharField(
        max_length=20,
        choices=ReliabilityTier.choices,
        default=ReliabilityTier.TIER_4_LOW,
        help_text="Reliability tier for alert system"
    )
    alert_priority = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Alert priority score (0-100)"
    )
    is_reliable = models.BooleanField(
        default=False,
        help_text="Suitable for reliable flood alerting"
    )
    
    # System management
    active = models.BooleanField(
        default=True,
        help_text="Include this gauge in active monitoring"
    )
    priority = models.CharField(
        max_length=10,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        default='medium'
    )
    
    # User feedback system
    user_feedback_count = models.IntegerField(
        default=0,
        help_text="Number of user feedback reports received"
    )
    accuracy_rating = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="User accuracy rating (0-5 stars)"
    )
    
    # API sync tracking
    last_api_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time data was synced with Google API"
    )
    api_sync_errors = models.TextField(
        blank=True,
        help_text="Any errors encountered during API sync"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_verified = models.DateTimeField(
        default=timezone.now,
        help_text="Last time classification was verified"
    )
    
    class Meta:
        ordering = ['-alert_priority', '-confidence_score', 'site_name']
        indexes = [
            models.Index(fields=['classification']),
            models.Index(fields=['source']),
            models.Index(fields=['quality_verified']),
            models.Index(fields=['active']),
            models.Index(fields=['reliability_tier']),
            models.Index(fields=['alert_priority']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        name = self.site_name or f"Gauge {self.gauge_id}"
        return f"{name} ({self.get_classification_display()})"
    
    @property
    def coordinates(self):
        """Get coordinates as tuple"""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def display_name(self):
        """Get display name for gauge"""
        if self.site_name:
            return self.site_name
        elif self.river:
            return f"{self.river} - {self.gauge_id}"
        else:
            return self.gauge_id

class GaugeModel(models.Model):
    """Gauge model metadata (from gaugeModels API)"""
    
    gauge = models.OneToOneField(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='model'
    )
    
    # Model identification
    gauge_model_id = models.CharField(
        max_length=100,
        help_text="Model ID from Google Flood Hub"
    )
    
    # Value unit
    gauge_value_unit = models.CharField(
        max_length=50,
        choices=GaugeValueUnit.choices,
        default=GaugeValueUnit.GAUGE_VALUE_UNIT_UNSPECIFIED
    )
    
    # Model quality
    model_quality_verified = models.BooleanField(
        default=False,
        help_text="Whether this model is quality verified"
    )
    
    # Threshold values
    warning_level = models.FloatField(
        null=True, 
        blank=True,
        help_text="Warning level threshold value"
    )
    danger_level = models.FloatField(
        null=True, 
        blank=True,
        help_text="Danger level threshold value"
    )
    extreme_danger_level = models.FloatField(
        null=True, 
        blank=True,
        help_text="Extreme danger level threshold value"
    )
    
    # Model metadata
    model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Model version identifier"
    )
    model_updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the model was last updated"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Model for {self.gauge.display_name}"

class FloodStatus(models.Model):
    """Current flood status (from floodStatus API)"""
    
    gauge = models.ForeignKey(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='flood_statuses'
    )
    
    # Status identification
    status_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier for this flood status"
    )
    
    # Timing information
    issued_time = models.DateTimeField(
        help_text="When this status was issued"
    )
    forecast_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start of forecast time range"
    )
    forecast_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End of forecast time range"
    )
    
    # Flood assessment
    severity = models.CharField(
        max_length=30,
        choices=FloodSeverity.choices,
        default=FloodSeverity.SEVERITY_UNSPECIFIED
    )
    forecast_trend = models.CharField(
        max_length=30,
        choices=ForecastTrend.choices,
        default=ForecastTrend.FORECAST_TREND_UNSPECIFIED
    )
    map_inference_type = models.CharField(
        max_length=30,
        choices=MapInferenceType.choices,
        default=MapInferenceType.MAP_INFERENCE_TYPE_UNSPECIFIED
    )
    
    # Forecast changes
    forecast_change_lower = models.FloatField(
        null=True,
        blank=True,
        help_text="Lower bound of forecasted change (meters)"
    )
    forecast_change_upper = models.FloatField(
        null=True,
        blank=True,
        help_text="Upper bound of forecasted change (meters)"
    )
    reference_time_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start of reference time range"
    )
    reference_time_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End of reference time range"
    )
    
    # Inundation maps
    has_inundation_maps = models.BooleanField(
        default=False,
        help_text="Whether inundation maps are available"
    )
    inundation_map_type = models.CharField(
        max_length=30,
        choices=InundationMapType.choices,
        blank=True,
        help_text="Type of inundation maps"
    )
    inundation_maps_count = models.IntegerField(
        default=0,
        help_text="Number of inundation maps available"
    )
    
    # Polygon IDs for map data
    notification_polygon_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID for notification polygon"
    )
    inundation_polygon_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="IDs for inundation polygons"
    )
    
    # Status flags
    is_active_flood = models.BooleanField(
        default=False,
        help_text="Whether this represents active flooding"
    )
    risk_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        help_text="Numeric risk level (0-4)"
    )
    
    # Raw API data
    raw_api_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw data from Google Flood Hub API"
    )
    
    # Status management
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the current status for the gauge"
    )
    superseded_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Newer status that supersedes this one"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-issued_time', '-created_at']
        indexes = [
            models.Index(fields=['gauge', 'is_current']),
            models.Index(fields=['severity']),
            models.Index(fields=['issued_time']),
            models.Index(fields=['is_active_flood']),
            models.Index(fields=['risk_level']),
        ]
        unique_together = [['gauge', 'issued_time']]
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.gauge.display_name} ({self.issued_time})"
    
    @property
    def forecast_duration_hours(self):
        """Calculate forecast duration in hours"""
        if self.forecast_start and self.forecast_end:
            return (self.forecast_end - self.forecast_start).total_seconds() / 3600
        return 0

class UserFeedback(models.Model):
    """Enhanced user feedback on gauge accuracy and alerts"""
    
    gauge = models.ForeignKey(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    flood_status = models.ForeignKey(
        FloodStatus,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='feedback',
        help_text="Specific flood status being reviewed"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Feedback content
    feedback_type = models.CharField(
        max_length=20,
        choices=[
            ('gauge_accuracy', 'Gauge Accuracy'),
            ('flood_alert', 'Flood Alert Accuracy'),
            ('classification', 'Classification Feedback'),
            ('location', 'Location Correction'),
            ('threshold', 'Threshold Feedback'),
            ('inundation_map', 'Inundation Map Accuracy'),
            ('false_positive', 'False Positive Report'),
            ('false_negative', 'False Negative Report'),
            ('other', 'Other')
        ]
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 stars"
    )
    accuracy_confirmed = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the alert/prediction was accurate"
    )
    
    # Detailed feedback
    comments = models.TextField(
        blank=True,
        help_text="Additional comments from user"
    )
    observed_conditions = models.TextField(
        blank=True,
        help_text="Actual observed conditions on ground"
    )
    suggested_improvements = models.TextField(
        blank=True,
        help_text="Suggestions for improvement"
    )
    
    # Contact info (for anonymous feedback)
    contact_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional contact information"
    )
    organization = models.CharField(
        max_length=100,
        blank=True,
        help_text="Organization providing feedback"
    )
    
    # Location context
    reporting_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Location from which feedback is provided"
    )
    
    # Verification
    verified = models.BooleanField(
        default=False,
        help_text="Feedback has been verified by admin"
    )
    verification_notes = models.TextField(
        blank=True,
        help_text="Admin notes on verification"
    )
    
    # Response tracking
    response_provided = models.BooleanField(
        default=False,
        help_text="Whether response was provided to user"
    )
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up action is required"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gauge', 'feedback_type']),
            models.Index(fields=['verified']),
            models.Index(fields=['follow_up_required']),
        ]
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} for {self.gauge.display_name}"

class AnalysisReport(models.Model):
    """Enhanced periodic analysis reports"""
    
    report_date = models.DateField(
        default=timezone.now,
        help_text="Date of the analysis report"
    )
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily Report'),
            ('weekly', 'Weekly Report'), 
            ('monthly', 'Monthly Report'),
            ('comprehensive', 'Comprehensive Analysis'),
            ('emergency', 'Emergency Assessment')
        ],
        default='daily'
    )
    
    # Summary statistics
    total_gauges = models.IntegerField(default=0)
    reliable_gauges = models.IntegerField(default=0)
    active_flood_alerts = models.IntegerField(default=0)
    quality_verified_gauges = models.IntegerField(default=0)
    
    # Classification breakdown
    verified_physical = models.IntegerField(default=0)
    likely_physical = models.IntegerField(default=0)
    uncertain_gauges = models.IntegerField(default=0)
    likely_virtual = models.IntegerField(default=0)
    
    # Performance metrics
    average_confidence = models.FloatField(
        default=0.0,
        help_text="Average confidence score across all gauges"
    )
    external_matches = models.IntegerField(
        default=0,
        help_text="Number of gauges with external validation matches"
    )
    api_sync_success_rate = models.FloatField(
        default=0.0,
        help_text="Success rate of API synchronization"
    )
    
    # User engagement
    total_feedback = models.IntegerField(
        default=0,
        help_text="Total user feedback received"
    )
    average_rating = models.FloatField(
        null=True,
        blank=True,
        help_text="Average user rating"
    )
    verified_feedback = models.IntegerField(
        default=0,
        help_text="Amount of verified feedback"
    )
    
    # System reliability
    tier_1_gauges = models.IntegerField(
        default=0,
        help_text="Tier 1 (highest reliability) gauges"
    )
    tier_2_gauges = models.IntegerField(
        default=0,
        help_text="Tier 2 (high reliability) gauges"
    )
    
    # Geographic coverage
    northern_coverage = models.IntegerField(
        default=0,
        help_text="Gauges in northern Pakistan"
    )
    central_coverage = models.IntegerField(
        default=0,
        help_text="Gauges in central Pakistan"
    )
    southern_coverage = models.IntegerField(
        default=0,
        help_text="Gauges in southern Pakistan"
    )
    
    # Report data
    detailed_data = models.JSONField(
        default=dict,
        help_text="Detailed analysis data"
    )
    recommendations = models.JSONField(
        default=list,
        help_text="System recommendations"
    )
    
    # Report metadata
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who generated the report"
    )
    generation_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to generate report"
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date', '-generated_at']
        unique_together = [['report_date', 'report_type']]
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['report_date']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.report_date}"

class APIConfig(models.Model):
    """Configuration for Google Flood Hub API integration"""
    
    config_name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Configuration name identifier"
    )
    
    # API settings
    api_key = models.CharField(
        max_length=200,
        blank=True,
        help_text="Google Flood Hub API key"
    )
    base_url = models.URLField(
        default="https://floodhub.googleapis.com",
        help_text="Base URL for Google Flood Hub API"
    )
    
    # Rate limiting
    requests_per_minute = models.IntegerField(
        default=60,
        help_text="API requests per minute limit"
    )
    batch_size = models.IntegerField(
        default=50,
        help_text="Batch size for API requests"
    )
    
    # Sync settings
    sync_interval_hours = models.IntegerField(
        default=6,
        help_text="Hours between automatic syncs"
    )
    auto_sync_enabled = models.BooleanField(
        default=True,
        help_text="Enable automatic API synchronization"
    )
    
    # Retry settings
    max_retries = models.IntegerField(
        default=3,
        help_text="Maximum retry attempts for failed requests"
    )
    retry_delay_seconds = models.IntegerField(
        default=30,
        help_text="Delay between retry attempts"
    )
    
    # Regional settings
    pakistan_bounds_json = models.JSONField(
        default=dict,
        help_text="Pakistan geographical bounds for API queries"
    )
    
    # Status tracking
    last_successful_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful API sync time"
    )
    last_sync_error = models.TextField(
        blank=True,
        help_text="Last API sync error message"
    )
    total_api_calls = models.BigIntegerField(
        default=0,
        help_text="Total API calls made"
    )
    
    # Configuration metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'config_name']
    
    def __str__(self):
        return f"API Config: {self.config_name}"

# Management utility classes
class EnhancedGaugeManager:
    """Enhanced helper class for gauge management operations"""
    
    @staticmethod
    def update_gauge_from_api_data(api_data: dict) -> RiverGauge:
        """Update or create gauge from comprehensive API data"""
        gauge_id = api_data.get('gaugeId')
        location = api_data.get('location', {})
        
        gauge, created = RiverGauge.objects.update_or_create(
            gauge_id=gauge_id,
            defaults={
                'latitude': location.get('latitude', 0),
                'longitude': location.get('longitude', 0),
                'source': api_data.get('source', 'OTHER'),
                'site_name': api_data.get('siteName', ''),
                'river': api_data.get('river', ''),
                'country_code': api_data.get('countryCode', 'PK'),
                'quality_verified': api_data.get('qualityVerified', False),
                'has_model': api_data.get('hasModel', False),
                'last_api_sync': timezone.now()
            }
        )
        
        return gauge
    
    @staticmethod
    def update_reliability_assessment(gauge: RiverGauge) -> RiverGauge:
        """Update reliability tier and alert priority for a gauge"""
        # Calculate alert priority
        priority = min(gauge.confidence_score, 50)
        
        if gauge.quality_verified:
            priority += 20
        
        if gauge.classification == GaugeClassification.VERIFIED_PHYSICAL:
            priority += 15
        elif gauge.classification == GaugeClassification.LIKELY_PHYSICAL:
            priority += 10
        
        if gauge.has_model and hasattr(gauge, 'model') and gauge.model.model_quality_verified:
            priority += 10
        
        # Determine reliability tier
        if (gauge.quality_verified and 
            gauge.classification == GaugeClassification.VERIFIED_PHYSICAL and
            gauge.confidence_score >= 80 and
            gauge.has_model):
            tier = ReliabilityTier.TIER_1_HIGHEST
        elif (gauge.quality_verified and
              gauge.classification == GaugeClassification.LIKELY_PHYSICAL and
              gauge.has_model):
            tier = ReliabilityTier.TIER_2_HIGH
        elif gauge.quality_verified and gauge.has_model:
            tier = ReliabilityTier.TIER_3_MEDIUM
        else:
            tier = ReliabilityTier.TIER_4_LOW
        
        gauge.alert_priority = min(priority, 100)
        gauge.reliability_tier = tier
        gauge.is_reliable = tier in [ReliabilityTier.TIER_1_HIGHEST, ReliabilityTier.TIER_2_HIGH]
        gauge.save()
        
        return gauge
    
    @staticmethod
    def calculate_comprehensive_stats():
        """Calculate comprehensive system statistics"""
        return {
            'total_gauges': RiverGauge.objects.count(),
            'reliable_gauges': RiverGauge.objects.filter(is_reliable=True).count(),
            'by_classification': {
                choice[0]: RiverGauge.objects.filter(classification=choice[0]).count()
                for choice in GaugeClassification.choices
            },
            'by_source': {
                choice[0]: RiverGauge.objects.filter(source=choice[0]).count()
                for choice in GaugeSource.choices
            },
            'by_reliability_tier': {
                choice[0]: RiverGauge.objects.filter(reliability_tier=choice[0]).count()
                for choice in ReliabilityTier.choices
            },
            'quality_verified': RiverGauge.objects.filter(quality_verified=True).count(),
            'with_models': RiverGauge.objects.filter(has_model=True).count(),
            'with_external_match': RiverGauge.objects.filter(external_match_found=True).count(),
            'active_flood_alerts': FloodStatus.objects.filter(
                is_current=True, 
                is_active_flood=True
            ).count(),
            'total_feedback': UserFeedback.objects.count(),
            'verified_feedback': UserFeedback.objects.filter(verified=True).count()
        }