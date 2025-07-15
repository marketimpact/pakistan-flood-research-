#!/usr/bin/env python3
"""
Integrated Pakistan Gauge Analysis System
Combines classification, external validation, and reporting
"""

import pandas as pd
import json
import logging
from datetime import datetime
from typing import Dict, List
import argparse

from gauge_analyzer import PakistanGaugeAnalyzer, GaugeClassification
from external_validators import ExternalValidationService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedGaugeAnalyzer:
    """Integrated analysis system combining all components"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.gauge_analyzer = PakistanGaugeAnalyzer(api_key)
        self.validator = ExternalValidationService()
        self.results = {}
        
    def run_complete_analysis(self) -> Dict:
        """Run complete analysis pipeline"""
        logger.info("Starting complete gauge analysis pipeline...")
        
        # Step 1: Analyze all Pakistani gauges
        logger.info("Step 1: Analyzing Pakistani gauges...")
        gauge_df = self.gauge_analyzer.analyze_all_gauges()
        
        # Step 2: Add external validation
        logger.info("Step 2: Adding external validation...")
        validated_df = self._add_external_validation(gauge_df)
        
        # Step 3: Generate comprehensive reports
        logger.info("Step 3: Generating reports...")
        reports = self._generate_comprehensive_reports(validated_df)
        
        # Step 4: Save all results
        logger.info("Step 4: Saving results...")
        file_paths = self._save_all_results(validated_df, reports)
        
        self.results = {
            'dataframe': validated_df,
            'reports': reports,
            'file_paths': file_paths
        }
        
        return self.results
    
    def _add_external_validation(self, gauge_df: pd.DataFrame) -> pd.DataFrame:
        """Add external validation data to gauge dataframe"""
        validation_results = []
        
        for _, gauge in gauge_df.iterrows():
            gauge_data = {
                'location': {
                    'latitude': gauge['latitude'],
                    'longitude': gauge['longitude']
                }
            }
            
            validation = self.validator.validate_gauge_against_external(gauge_data)
            validation_results.append(validation)
        
        # Add validation columns
        gauge_df['validation_status'] = [v['validation_status'] for v in validation_results]
        gauge_df['confidence_boost'] = [v['confidence_boost'] for v in validation_results]
        gauge_df['external_matches'] = [len(v['matches']) for v in validation_results]
        gauge_df['validation_evidence'] = ['; '.join(v['evidence']) for v in validation_results]
        
        # Update confidence scores with validation boost
        gauge_df['final_confidence_score'] = gauge_df['confidenceScore'] + gauge_df['confidence_boost']
        gauge_df['final_confidence_score'] = gauge_df['final_confidence_score'].clip(0, 100)
        
        # Update classifications based on new confidence scores
        def update_classification(row):
            score = row['final_confidence_score']
            if score >= 80:
                return GaugeClassification.VERIFIED_PHYSICAL
            elif score >= 60:
                return GaugeClassification.LIKELY_PHYSICAL
            elif score >= 30:
                return GaugeClassification.UNCERTAIN
            else:
                return GaugeClassification.LIKELY_VIRTUAL
        
        gauge_df['final_classification'] = gauge_df.apply(update_classification, axis=1)
        
        return gauge_df
    
    def _generate_comprehensive_reports(self, validated_df: pd.DataFrame) -> Dict:
        """Generate comprehensive analysis reports"""
        reports = {}
        
        # Basic statistics
        reports['basic_stats'] = {
            'total_gauges': len(validated_df),
            'analysis_date': datetime.now().isoformat(),
            'api_key_used': self.api_key is not None
        }
        
        # Classification analysis
        reports['classification_analysis'] = {
            'original_classification': validated_df['classification'].value_counts().to_dict(),
            'final_classification': validated_df['final_classification'].value_counts().to_dict(),
            'confidence_distribution': {
                'original_mean': float(validated_df['confidenceScore'].mean()),
                'final_mean': float(validated_df['final_confidence_score'].mean()),
                'original_std': float(validated_df['confidenceScore'].std()),
                'final_std': float(validated_df['final_confidence_score'].std())
            }
        }
        
        # Source analysis
        reports['source_analysis'] = {
            'by_source': validated_df['source'].value_counts().to_dict(),
            'quality_verified_by_source': validated_df.groupby('source')['qualityVerified'].sum().to_dict(),
            'has_model_by_source': validated_df.groupby('source')['hasModel'].sum().to_dict()
        }
        
        # External validation analysis
        reports['validation_analysis'] = {
            'validation_status_counts': validated_df['validation_status'].value_counts().to_dict(),
            'external_matches_distribution': validated_df['external_matches'].value_counts().to_dict(),
            'validation_impact': {
                'gauges_with_boost': int((validated_df['confidence_boost'] > 0).sum()),
                'average_boost': float(validated_df['confidence_boost'].mean()),
                'max_boost': float(validated_df['confidence_boost'].max())
            }
        }
        
        # Geographic analysis
        reports['geographic_analysis'] = {
            'latitude_range': [float(validated_df['latitude'].min()), float(validated_df['latitude'].max())],
            'longitude_range': [float(validated_df['longitude'].min()), float(validated_df['longitude'].max())],
            'geographic_distribution': self._analyze_geographic_distribution(validated_df)
        }
        
        # Quality analysis
        reports['quality_analysis'] = {
            'quality_verified_count': int(validated_df['qualityVerified'].sum()),
            'quality_verified_percentage': float(validated_df['qualityVerified'].mean() * 100),
            'has_model_count': int(validated_df['hasModel'].sum()),
            'has_model_percentage': float(validated_df['hasModel'].mean() * 100),
            'high_confidence_gauges': int((validated_df['final_confidence_score'] >= 70).sum())
        }
        
        # Recommended actions
        reports['recommendations'] = self._generate_recommendations(validated_df)
        
        # External stations summary
        external_stations_df = self.validator.get_all_external_stations()
        reports['external_stations_summary'] = {
            'total_external_stations': len(external_stations_df),
            'by_source': external_stations_df['source'].value_counts().to_dict(),
            'by_river': external_stations_df['river'].value_counts().to_dict()
        }
        
        return reports
    
    def _analyze_geographic_distribution(self, df: pd.DataFrame) -> Dict:
        """Analyze geographic distribution of gauges"""
        # Define Pakistan regions (approximate)
        regions = {
            'Northern': {'lat_min': 34, 'lat_max': 38, 'lon_min': 71, 'lon_max': 78},
            'Central': {'lat_min': 28, 'lat_max': 34, 'lon_min': 67, 'lon_max': 76},
            'Southern': {'lat_min': 23, 'lat_max': 28, 'lon_min': 60, 'lon_max': 72}
        }
        
        distribution = {}
        for region, bounds in regions.items():
            mask = (
                (df['latitude'] >= bounds['lat_min']) & 
                (df['latitude'] < bounds['lat_max']) &
                (df['longitude'] >= bounds['lon_min']) & 
                (df['longitude'] < bounds['lon_max'])
            )
            region_df = df[mask]
            distribution[region] = {
                'total_gauges': len(region_df),
                'physical_gauges': int((region_df['final_classification'].isin([
                    GaugeClassification.VERIFIED_PHYSICAL, 
                    GaugeClassification.LIKELY_PHYSICAL
                ])).sum()),
                'quality_verified': int(region_df['qualityVerified'].sum())
            }
        
        return distribution
    
    def _generate_recommendations(self, df: pd.DataFrame) -> Dict:
        """Generate recommendations based on analysis"""
        recommendations = {}
        
        # High priority gauges for Pak-FEWS
        high_priority = df[
            (df['final_confidence_score'] >= 70) & 
            (df['qualityVerified'] == True)
        ]
        
        recommendations['high_priority_gauges'] = {
            'count': len(high_priority),
            'criteria': 'Confidence score >= 70 AND quality verified',
            'gauge_ids': high_priority['gaugeId'].tolist()[:10]  # Top 10
        }
        
        # Uncertain gauges needing verification
        uncertain = df[df['final_classification'] == GaugeClassification.UNCERTAIN]
        recommendations['verification_needed'] = {
            'count': len(uncertain),
            'action': 'Contact Google for clarification or verify locally',
            'gauge_ids': uncertain['gaugeId'].tolist()[:5]  # Top 5
        }
        
        # Coverage gaps
        low_coverage_regions = []
        geographic_dist = self._analyze_geographic_distribution(df)
        for region, stats in geographic_dist.items():
            if stats['total_gauges'] < 10:  # Arbitrary threshold
                low_coverage_regions.append(region)
        
        recommendations['coverage_gaps'] = {
            'regions': low_coverage_regions,
            'action': 'Consider additional monitoring or partner with local agencies'
        }
        
        # System implementation recommendations
        recommendations['system_implementation'] = {
            'start_with_physical': f"Begin with {len(high_priority)} high-confidence physical gauges",
            'include_quality_hybas': f"Include {len(df[(df['source'] == 'HYBAS') & (df['qualityVerified'] == True)])} quality-verified HYBAS gauges",
            'flag_uncertain': f"Flag {len(uncertain)} uncertain gauges with appropriate warnings",
            'user_feedback': "Implement user feedback system to improve classifications over time"
        }
        
        return recommendations
    
    def _save_all_results(self, df: pd.DataFrame, reports: Dict) -> Dict:
        """Save all analysis results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_paths = {}
        
        # Save main gauge inventory
        csv_filename = f'gauge_inventory_complete_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)
        file_paths['gauge_inventory'] = csv_filename
        
        # Save comprehensive analysis report
        json_filename = f'comprehensive_analysis_{timestamp}.json'
        with open(json_filename, 'w') as f:
            json.dump(reports, f, indent=2, default=str)
        file_paths['analysis_report'] = json_filename
        
        # Save high-priority gauges
        high_priority = df[
            (df['final_confidence_score'] >= 70) & 
            (df['qualityVerified'] == True)
        ]
        high_priority_filename = f'high_priority_gauges_{timestamp}.csv'
        high_priority.to_csv(high_priority_filename, index=False)
        file_paths['high_priority_gauges'] = high_priority_filename
        
        # Save external stations reference
        external_df = self.validator.get_all_external_stations()
        external_filename = f'external_stations_reference_{timestamp}.csv'
        external_df.to_csv(external_filename, index=False)
        file_paths['external_stations'] = external_filename
        
        # Save research findings markdown
        findings_filename = f'research_findings_{timestamp}.md'
        self._generate_research_findings_md(df, reports, findings_filename)
        file_paths['research_findings'] = findings_filename
        
        return file_paths
    
    def _generate_research_findings_md(self, df: pd.DataFrame, reports: Dict, filename: str):
        """Generate comprehensive research findings markdown report"""
        content = f"""# Pakistan Flood Hub Gauge Analysis - Research Findings

## Executive Summary

Analysis completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} covering {reports['basic_stats']['total_gauges']} gauges within Pakistan's boundaries.

## Key Findings

### 1. Gauge Inventory Overview
- **Total Gauges Identified**: {reports['basic_stats']['total_gauges']}
- **Quality Verified**: {reports['quality_analysis']['quality_verified_count']} ({reports['quality_analysis']['quality_verified_percentage']:.1f}%)
- **With Flood Models**: {reports['quality_analysis']['has_model_count']} ({reports['quality_analysis']['has_model_percentage']:.1f}%)

### 2. Classification Results
- **Verified/Likely Physical**: {reports['classification_analysis']['final_classification'].get('verified_physical', 0) + reports['classification_analysis']['final_classification'].get('likely_physical', 0)}
- **Uncertain**: {reports['classification_analysis']['final_classification'].get('uncertain', 0)}
- **Likely Virtual**: {reports['classification_analysis']['final_classification'].get('likely_virtual', 0)}

### 3. Data Sources
"""
        
        for source, count in reports['source_analysis']['by_source'].items():
            content += f"- **{source}**: {count} gauges\n"
        
        content += f"""
### 4. External Validation Results
- **Gauges with External Matches**: {reports['validation_analysis']['validation_impact']['gauges_with_boost']}
- **Average Confidence Boost**: {reports['validation_analysis']['validation_impact']['average_boost']:.1f} points
- **Total External Stations Referenced**: {reports['external_stations_summary']['total_external_stations']}

### 5. Geographic Distribution
"""
        
        for region, stats in reports['geographic_analysis']['geographic_distribution'].items():
            content += f"- **{region} Pakistan**: {stats['total_gauges']} total, {stats['physical_gauges']} likely physical\n"
        
        content += f"""
## Detailed Analysis

### Quality Assessment
The analysis reveals that {reports['quality_analysis']['quality_verified_percentage']:.1f}% of gauges have `qualityVerified: true`, indicating Google's confidence in the data quality. This represents {reports['quality_analysis']['quality_verified_count']} gauges that meet Google's quality standards.

### Source Analysis
The gauge network includes data from multiple sources:
"""
        
        for source, count in reports['source_analysis']['by_source'].items():
            quality_count = reports['source_analysis']['quality_verified_by_source'].get(source, 0)
            model_count = reports['source_analysis']['has_model_by_source'].get(source, 0)
            content += f"- **{source}**: {count} gauges ({quality_count} quality verified, {model_count} with models)\n"
        
        content += f"""
### External Validation Impact
Cross-referencing with Pakistani government databases revealed:
- {reports['validation_analysis']['validation_impact']['gauges_with_boost']} gauges matched with external stations
- Average confidence boost of {reports['validation_analysis']['validation_impact']['average_boost']:.1f} points
- Maximum boost of {reports['validation_analysis']['validation_impact']['max_boost']:.1f} points

## Recommendations for Pak-FEWS Implementation

### Phase 1: High-Priority Gauges
Start with {reports['recommendations']['high_priority_gauges']['count']} gauges that meet criteria:
- Confidence score ≥ 70
- Quality verified by Google
- Examples: {', '.join(reports['recommendations']['high_priority_gauges']['gauge_ids'][:3]) if reports['recommendations']['high_priority_gauges']['gauge_ids'] else 'None available'}

### Phase 2: Verified HYBAS Gauges
Include {len(df[(df['source'] == 'HYBAS') & (df['qualityVerified'] == True)])} HYBAS gauges with quality verification.

### Phase 3: Uncertain Gauges
{reports['recommendations']['verification_needed']['count']} gauges need additional verification through:
- Direct contact with Google Flood Hub team
- Local verification with WAPDA/PMD
- Community feedback collection

### System Design Implications
1. **Trust Levels**: Implement confidence-based alert reliability indicators
2. **User Feedback**: Build feedback system to improve classifications
3. **Coverage Gaps**: Focus on regions with low gauge density
4. **Update Mechanism**: Regular re-analysis as new data becomes available

## Technical Details

### Confidence Scoring Algorithm
The classification system uses a weighted scoring approach:
- Named site/river: +30/+20 points
- Physical network source (GRDC/WAPDA/PMD): +40 points
- Quality verification: +10 points
- Non-HYBAS ID format: +20 points
- External station match: +10-40 points (distance-based)

### External Data Sources
- **WAPDA**: {reports['external_stations_summary']['by_source'].get('WAPDA', 0)} stations
- **PMD**: {reports['external_stations_summary']['by_source'].get('PMD', 0)} stations
- **FFD**: {reports['external_stations_summary']['by_source'].get('FFD', 0)} stations
- **NDMA**: {reports['external_stations_summary']['by_source'].get('NDMA', 0)} stations

## Conclusion

This analysis provides a systematic approach to identifying physical vs. virtual gauges in Pakistan's flood monitoring network. The results support a phased implementation approach for Pak-FEWS, starting with high-confidence physical gauges and expanding to include validated virtual gauges.

**Next Steps:**
1. Review high-priority gauge list for immediate implementation
2. Contact Google for clarification on uncertain gauges
3. Begin system development with confidence-based alert architecture
4. Establish user feedback mechanism for continuous improvement

---
*Report generated by Pakistan Flood Hub Gauge Analyzer*
*Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(filename, 'w') as f:
            f.write(content)
    
    def print_summary(self):
        """Print analysis summary to console"""
        if not self.results:
            print("No analysis results available. Run run_complete_analysis() first.")
            return
        
        reports = self.results['reports']
        df = self.results['dataframe']
        
        print("\n" + "="*60)
        print("PAKISTAN FLOOD HUB GAUGE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nTotal Gauges Analyzed: {reports['basic_stats']['total_gauges']}")
        
        print("\nFinal Classification:")
        for classification, count in reports['classification_analysis']['final_classification'].items():
            print(f"  {classification.replace('_', ' ').title()}: {count}")
        
        print("\nData Sources:")
        for source, count in reports['source_analysis']['by_source'].items():
            print(f"  {source}: {count}")
        
        print(f"\nQuality Metrics:")
        print(f"  Quality Verified: {reports['quality_analysis']['quality_verified_count']} ({reports['quality_analysis']['quality_verified_percentage']:.1f}%)")
        print(f"  With Models: {reports['quality_analysis']['has_model_count']} ({reports['quality_analysis']['has_model_percentage']:.1f}%)")
        print(f"  High Confidence: {reports['quality_analysis']['high_confidence_gauges']}")
        
        print(f"\nExternal Validation:")
        print(f"  Gauges with Matches: {reports['validation_analysis']['validation_impact']['gauges_with_boost']}")
        print(f"  Average Confidence Boost: {reports['validation_analysis']['validation_impact']['average_boost']:.1f} points")
        
        print(f"\nRecommendations:")
        print(f"  Start with {reports['recommendations']['high_priority_gauges']['count']} high-priority gauges")
        print(f"  Verify {reports['recommendations']['verification_needed']['count']} uncertain gauges")
        
        print(f"\nFiles Generated:")
        for file_type, filepath in self.results['file_paths'].items():
            print(f"  {file_type}: {filepath}")
        
        print("\n" + "="*60)

def main():
    """Main execution function with command line arguments"""
    parser = argparse.ArgumentParser(description='Pakistan Flood Hub Gauge Analysis')
    parser.add_argument('--api-key', help='Google Flood Hub API key')
    parser.add_argument('--output-dir', help='Output directory for results', default='.')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run analysis
    analyzer = IntegratedGaugeAnalyzer(api_key=args.api_key)
    results = analyzer.run_complete_analysis()
    analyzer.print_summary()

if __name__ == "__main__":
    main()