#!/usr/bin/env python3
"""
Django Models for Pakistan Flood Early Warning System (Pak-FEWS)
Gauge classification and management models
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
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
    OTHER = 'OTHER', 'Other Source'

class AlertLevel(models.TextChoices):
    """Flood alert levels"""
    NORMAL = 'normal', 'Normal'
    WARNING = 'warning', 'Warning'
    DANGER = 'danger', 'Danger'
    EXTREME_DANGER = 'extreme_danger', 'Extreme Danger'

class RiverGauge(models.Model):
    """Main model for river gauge information"""
    
    # Core identification
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
    
    # Gauge metadata
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
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_verified = models.DateTimeField(
        default=timezone.now,
        help_text="Last time classification was verified"
    )
    
    class Meta:
        ordering = ['-confidence_score', 'site_name']
        indexes = [
            models.Index(fields=['classification']),
            models.Index(fields=['source']),
            models.Index(fields=['quality_verified']),
            models.Index(fields=['active']),
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
    def is_likely_physical(self):
        """Check if gauge is likely physical"""
        return self.classification in [
            GaugeClassification.VERIFIED_PHYSICAL,
            GaugeClassification.LIKELY_PHYSICAL
        ]
    
    @property
    def display_name(self):
        """Get display name for gauge"""
        if self.site_name:
            return self.site_name
        elif self.river:
            return f"{self.river} - {self.gauge_id}"
        else:
            return self.gauge_id

class GaugeThreshold(models.Model):
    """Flood thresholds for individual gauges"""
    
    gauge = models.OneToOneField(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='thresholds'
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
    
    # Units and metadata
    unit = models.CharField(
        max_length=50,
        default="CUBIC_METERS_PER_SECOND",
        help_text="Unit of measurement for threshold values"
    )
    
    # Return periods
    two_year_return = models.FloatField(
        null=True, 
        blank=True,
        help_text="2-year return period value"
    )
    five_year_return = models.FloatField(
        null=True, 
        blank=True,
        help_text="5-year return period value"
    )
    twenty_year_return = models.FloatField(
        null=True, 
        blank=True,
        help_text="20-year return period value"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Thresholds for {self.gauge.display_name}"

class FloodAlert(models.Model):
    """Current flood status and alerts for gauges"""
    
    gauge = models.ForeignKey(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    # Alert information
    alert_level = models.CharField(
        max_length=20,
        choices=AlertLevel.choices,
        default=AlertLevel.NORMAL
    )
    severity = models.CharField(
        max_length=20,
        blank=True,
        help_text="Severity level from Google Flood Hub"
    )
    
    # Current readings
    current_value = models.FloatField(
        null=True, 
        blank=True,
        help_text="Current gauge reading"
    )
    forecast_value = models.FloatField(
        null=True, 
        blank=True,
        help_text="Forecasted peak value"
    )
    
    # Timing
    forecast_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Time of forecasted peak"
    )
    issued_at = models.DateTimeField(
        default=timezone.now,
        help_text="When alert was issued"
    )
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When alert expires"
    )
    
    # Alert metadata
    active = models.BooleanField(
        default=True,
        help_text="Alert is currently active"
    )
    automated = models.BooleanField(
        default=True,
        help_text="Alert was generated automatically"
    )
    
    # Raw API data
    raw_api_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw data from Google Flood Hub API"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['gauge', 'active']),
            models.Index(fields=['alert_level']),
            models.Index(fields=['issued_at']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_level_display()} - {self.gauge.display_name}"

class UserFeedback(models.Model):
    """User feedback on gauge accuracy and alerts"""
    
    gauge = models.ForeignKey(
        RiverGauge,
        on_delete=models.CASCADE,
        related_name='feedback'
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
            ('accuracy', 'Gauge Accuracy'),
            ('alert', 'Alert Feedback'),
            ('classification', 'Classification Feedback'),
            ('location', 'Location Correction'),
            ('other', 'Other')
        ]
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 stars"
    )
    comments = models.TextField(
        blank=True,
        help_text="Additional comments from user"
    )
    
    # Contact info (for anonymous feedback)
    contact_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional contact information"
    )
    
    # Verification
    verified = models.BooleanField(
        default=False,
        help_text="Feedback has been verified by admin"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} for {self.gauge.display_name}"

class AnalysisReport(models.Model):
    """Periodic analysis reports on gauge performance"""
    
    report_date = models.DateField(
        default=timezone.now,
        help_text="Date of the analysis report"
    )
    
    # Summary statistics
    total_gauges = models.IntegerField(default=0)
    physical_gauges = models.IntegerField(default=0)
    virtual_gauges = models.IntegerField(default=0)
    uncertain_gauges = models.IntegerField(default=0)
    
    # Performance metrics
    average_confidence = models.FloatField(
        default=0.0,
        help_text="Average confidence score across all gauges"
    )
    external_matches = models.IntegerField(
        default=0,
        help_text="Number of gauges with external validation matches"
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
    
    # Report data
    detailed_data = models.JSONField(
        default=dict,
        help_text="Detailed analysis data"
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-report_date']
        unique_together = ['report_date']
    
    def __str__(self):
        return f"Analysis Report - {self.report_date}"

# Management command helpers
class GaugeManager:
    """Helper class for gauge management operations"""
    
    @staticmethod
    def update_gauge_from_api_data(api_data: dict) -> RiverGauge:
        """Update or create gauge from API data"""
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
                'quality_verified': api_data.get('qualityVerified', False),
                'has_model': api_data.get('hasModel', False),
                'last_verified': timezone.now()
            }
        )
        
        return gauge
    
    @staticmethod
    def calculate_classification_stats():
        """Calculate classification statistics"""
        return {
            'total': RiverGauge.objects.count(),
            'by_classification': {
                choice[0]: RiverGauge.objects.filter(classification=choice[0]).count()
                for choice in GaugeClassification.choices
            },
            'by_source': {
                choice[0]: RiverGauge.objects.filter(source=choice[0]).count()
                for choice in GaugeSource.choices
            },
            'quality_verified': RiverGauge.objects.filter(quality_verified=True).count(),
            'with_external_match': RiverGauge.objects.filter(external_match_found=True).count()
        }