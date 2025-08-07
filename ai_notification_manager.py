#!/usr/bin/env python3
"""
Enhanced Notification Manager with AI Integration
Handles alerts and notifications based on AI system analysis.
"""

import logging
import time
import threading
import json
from typing import Dict, Any, List, Optional
from collections import deque

from ui.notifications import NotificationManager
from analyzers.ai_system_analyzer import AISystemAnalyzer

class AINotificationManager(NotificationManager):
    """Enhanced notification manager with AI-powered analysis integration."""
    
    def __init__(self, ai_analyzer: AISystemAnalyzer = None):
        super().__init__()
        self.ai_analyzer = ai_analyzer
        self.logger = logging.getLogger(f"{__name__}.AINotificationManager")
        
        # AI-specific notification settings
        self.ai_notifications_enabled = True
        self.analysis_notifications = True
        self.predictive_notifications = True
        self.learning_notifications = False
        
        # Notification priority levels for AI issues
        self.ai_severity_mapping = {
            'critical': 'critical',
            'warning': 'warning', 
            'info': 'info'
        }
        
        # Performance impact notifications
        self.performance_impact_messages = {
            'high': {
                'title': '🔴 High Performance Impact Detected',
                'message': 'Critical issues are significantly affecting system performance',
                'severity': 'critical'
            },
            'medium': {
                'title': '🟠 Medium Performance Impact Detected',
                'message': 'Several issues may be affecting gaming performance',
                'severity': 'warning'
            },
            'low': {
                'title': '🟢 Minor Performance Issues Detected',
                'message': 'Some optimizations available to improve performance',
                'severity': 'info'
            }
        }
        
        # Issue category icons and colors
        self.category_styling = {
            'cpu': {'icon': '🔥', 'color': '#ff4444'},
            'memory': {'icon': '💾', 'color': '#ff8800'},
            'gpu': {'icon': '🎮', 'color': '#00ff88'},
            'network': {'icon': '🌐', 'color': '#4488ff'},
            'storage': {'icon': '💿', 'color': '#ff44ff'},
            'system': {'icon': '⚙️', 'color': '#8844ff'},
            'gaming': {'icon': '🎯', 'color': '#ff0088'}
        }
        
        self.logger.info("AI Notification Manager initialized")
    
    def notify_ai_analysis_results(self, analysis_results: Dict[str, Any]):
        """Send notifications based on AI analysis results."""
        try:
            if not self.ai_notifications_enabled:
                return
            
            analysis_summary = analysis_results.get('analysis_summary', {})
            detected_issues = analysis_results.get('issues', {})
            recommendations = analysis_results.get('recommendations', {})
            
            # Notify about performance impact level
            impact_level = analysis_summary.get('performance_impact_level', 'low')
            if impact_level in self.performance_impact_messages:
                impact_info = self.performance_impact_messages[impact_level]
                self._send_notification(
                    impact_info['title'],
                    impact_info['message'],
                    impact_info['severity']
                )
            
            # Notify about critical and warning issues
            self._notify_about_detected_issues(detected_issues)
            
            # Notify about high-priority recommendations
            self._notify_about_recommendations(recommendations)
            
            # Notify about system health score
            health_score = analysis_summary.get('overall_health_score', 100)
            if health_score < 70:
                severity = 'critical' if health_score < 50 else 'warning'
                title = f"📊 System Health Score: {health_score}/100"
                message = self._create_health_score_message(health_score, analysis_summary)
                self._send_notification(title, message, severity)
            
            # Log analysis completion
            self._log_analysis_notification(analysis_summary)
            
        except Exception as e:
            self.logger.error(f"Error sending AI analysis notifications: {e}")
    
    def _notify_about_detected_issues(self, detected_issues: Dict[str, Any]):
        """Send notifications for detected system issues."""
        try:
            # Group issues by severity and category
            critical_issues = []
            warning_issues = []
            gaming_issues = []
            
            for issue_id, issue_data in detected_issues.items():
                severity = issue_data.get('severity', 'info')
                affects_gaming = issue_data.get('affects_gaming', False)
                
                if severity == 'critical':
                    critical_issues.append(issue_data)
                elif severity == 'warning':
                    warning_issues.append(issue_data)
                
                if affects_gaming:
                    gaming_issues.append(issue_data)
            
            # Send notifications for critical issues
            for issue in critical_issues[:3]:  # Limit to 3 most important
                self._send_issue_notification(issue, 'critical')
            
            # Send grouped notification for warning issues
            if warning_issues:
                self._send_grouped_issues_notification(warning_issues, 'warning')
            
            # Send gaming-specific notification if needed
            if len(gaming_issues) > 2:
                self._send_gaming_issues_notification(gaming_issues)
                
        except Exception as e:
            self.logger.error(f"Error notifying about detected issues: {e}")
    
    def _notify_about_recommendations(self, recommendations: Dict[str, Any]):
        """Send notifications for optimization recommendations."""
        try:
            if not self.analysis_notifications:
                return
            
            # Filter high-priority auto-applicable recommendations
            high_priority_recs = []
            auto_applicable_recs = []
            
            for rec_id, rec_data in recommendations.items():
                priority = rec_data.get('priority', 0)
                auto_applicable = rec_data.get('auto_applicable', False)
                
                if priority >= 8:
                    high_priority_recs.append(rec_data)
                
                if auto_applicable:
                    auto_applicable_recs.append(rec_data)
            
            # Notify about high-priority recommendations
            if high_priority_recs:
                count = len(high_priority_recs)
                title = f"⚡ {count} High-Priority Optimization{'s' if count > 1 else ''} Available"
                
                message_lines = []
                for rec in high_priority_recs[:3]:  # Show top 3
                    message_lines.append(f"• {rec['title']}")
                    
                if len(high_priority_recs) > 3:
                    message_lines.append(f"• And {len(high_priority_recs) - 3} more optimizations...")
                
                message = "\n".join(message_lines)
                self._send_notification(title, message, 'info')
            
            # Notify about auto-applicable optimizations
            if len(auto_applicable_recs) >= 5:
                title = f"🔧 {len(auto_applicable_recs)} Automatic Optimizations Available"
                message = "Multiple optimizations can be applied automatically to improve performance"
                self._send_notification(title, message, 'info')
                
        except Exception as e:
            self.logger.error(f"Error notifying about recommendations: {e}")
    
    def _send_issue_notification(self, issue_data: Dict[str, Any], severity: str):
        """Send notification for a single issue."""
        try:
            category = issue_data.get('category', 'system')
            styling = self.category_styling.get(category, {'icon': '⚠️', 'color': '#ffaa00'})
            
            title = f"{styling['icon']} {issue_data.get('title', 'System Issue Detected')}"
            
            description = issue_data.get('description', '')
            impact = issue_data.get('impact', '')
            auto_fixable = issue_data.get('auto_fixable', False)
            
            message_parts = [description]
            if impact:
                message_parts.append(f"\nImpact: {impact}")
            
            if auto_fixable:
                message_parts.append("\n✅ Can be fixed automatically")
            
            message = "".join(message_parts)
            
            self._send_notification(title, message, severity)
            
        except Exception as e:
            self.logger.error(f"Error sending issue notification: {e}")
    
    def _send_grouped_issues_notification(self, issues: List[Dict[str, Any]], severity: str):
        """Send a grouped notification for multiple issues."""
        try:
            if not issues:
                return
            
            count = len(issues)
            title = f"⚠️ {count} Performance Issue{'s' if count > 1 else ''} Detected"
            
            message_lines = []
            category_counts = {}
            
            # Count issues by category
            for issue in issues:
                category = issue.get('category', 'system')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Create summary message
            for category, count in category_counts.items():
                styling = self.category_styling.get(category, {'icon': '⚠️'})
                message_lines.append(f"{styling['icon']} {category.title()}: {count} issue{'s' if count > 1 else ''}")
            
            # Add auto-fixable count
            auto_fixable_count = sum(1 for issue in issues if issue.get('auto_fixable', False))
            if auto_fixable_count > 0:
                message_lines.append(f"\n✅ {auto_fixable_count} can be fixed automatically")
            
            message = "\n".join(message_lines)
            self._send_notification(title, message, severity)
            
        except Exception as e:
            self.logger.error(f"Error sending grouped issues notification: {e}")
    
    def _send_gaming_issues_notification(self, gaming_issues: List[Dict[str, Any]]):
        """Send specific notification for gaming-related issues."""
        try:
            count = len(gaming_issues)
            title = f"🎮 {count} Gaming Performance Issue{'s' if count > 1 else ''}"
            
            critical_count = sum(1 for issue in gaming_issues if issue.get('severity') == 'critical')
            warning_count = sum(1 for issue in gaming_issues if issue.get('severity') == 'warning')
            
            message_parts = []
            if critical_count > 0:
                message_parts.append(f"🔴 {critical_count} critical gaming issue{'s' if critical_count > 1 else ''}")
            if warning_count > 0:
                message_parts.append(f"🟠 {warning_count} warning{'s' if warning_count > 1 else ''}")
            
            message_parts.append("\nThese issues may affect your gaming performance and should be addressed.")
            
            # Add specific gaming impacts
            gaming_impacts = set()
            for issue in gaming_issues[:3]:  # Top 3 issues
                impact = issue.get('impact', '')
                if 'frame' in impact.lower() or 'fps' in impact.lower():
                    gaming_impacts.add('Frame rate issues')
                elif 'latency' in impact.lower() or 'lag' in impact.lower():
                    gaming_impacts.add('Input latency')
                elif 'stutter' in impact.lower():
                    gaming_impacts.add('Frame stuttering')
            
            if gaming_impacts:
                message_parts.append(f"\nPotential impacts: {', '.join(gaming_impacts)}")
            
            message = "\n".join(message_parts)
            severity = 'critical' if critical_count > 0 else 'warning'
            
            self._send_notification(title, message, severity)
            
        except Exception as e:
            self.logger.error(f"Error sending gaming issues notification: {e}")
    
    def _create_health_score_message(self, health_score: int, analysis_summary: Dict[str, Any]) -> str:
        """Create a detailed health score message."""
        try:
            message_parts = []
            
            if health_score >= 80:
                message_parts.append("✅ Your system is in good condition")
            elif health_score >= 60:
                message_parts.append("⚠️ Your system has some performance issues")
            else:
                message_parts.append("🔴 Your system has significant performance problems")
            
            # Add issue breakdown
            critical_issues = analysis_summary.get('critical_issues', 0)
            warning_issues = analysis_summary.get('warning_issues', 0)
            gaming_affecting = analysis_summary.get('gaming_affecting_issues', 0)
            
            if critical_issues > 0:
                message_parts.append(f"\n🔴 {critical_issues} critical issue{'s' if critical_issues != 1 else ''}")
            if warning_issues > 0:
                message_parts.append(f"\n🟠 {warning_issues} warning{'s' if warning_issues != 1 else ''}")
            if gaming_affecting > 0:
                message_parts.append(f"\n🎮 {gaming_affecting} affecting gaming performance")
            
            # Add recommendations info
            total_recommendations = analysis_summary.get('total_recommendations', 0)
            auto_applicable = analysis_summary.get('auto_applicable_recommendations', 0)
            
            if total_recommendations > 0:
                message_parts.append(f"\n⚡ {total_recommendations} optimization{'s' if total_recommendations != 1 else ''} available")
                if auto_applicable > 0:
                    message_parts.append(f" ({auto_applicable} automatic)")
            
            return "".join(message_parts)
            
        except Exception as e:
            self.logger.error(f"Error creating health score message: {e}")
            return f"System health score: {health_score}/100"
    
    def _log_analysis_notification(self, analysis_summary: Dict[str, Any]):
        """Log analysis completion notification."""
        try:
            total_issues = analysis_summary.get('total_issues', 0)
            total_recommendations = analysis_summary.get('total_recommendations', 0)
            health_score = analysis_summary.get('overall_health_score', 100)
            
            log_message = (f"AI Analysis completed - Health Score: {health_score}/100, "
                          f"Issues: {total_issues}, Recommendations: {total_recommendations}")
            
            if total_issues == 0:
                self.logger.info(f"✅ {log_message}")
            elif analysis_summary.get('critical_issues', 0) > 0:
                self.logger.warning(f"🔴 {log_message}")
            else:
                self.logger.info(f"🟠 {log_message}")
                
        except Exception as e:
            self.logger.error(f"Error logging analysis notification: {e}")
    
    def notify_predictive_issue(self, prediction_type: str, confidence: float, details: str):
        """Send notification for AI-predicted issues."""
        try:
            if not self.predictive_notifications or confidence < 0.6:
                return
            
            prediction_messages = {
                'cpu_bottleneck': ('🔮 CPU Bottleneck Predicted', 'AI predicts potential CPU performance issues'),
                'memory_pressure': ('🔮 Memory Pressure Predicted', 'AI predicts potential memory shortage'),
                'thermal_throttling': ('🔮 Thermal Throttling Risk', 'AI predicts potential overheating issues'),
                'network_degradation': ('🔮 Network Issues Predicted', 'AI predicts potential network problems')
            }
            
            if prediction_type in prediction_messages:
                title, base_message = prediction_messages[prediction_type]
                
                confidence_text = f"{confidence*100:.0f}% confidence"
                message = f"{base_message} ({confidence_text})"
                
                if details:
                    message += f"\n\nDetails: {details}"
                
                message += "\n\nConsider taking preventive action to avoid performance issues."
                
                severity = 'warning' if confidence > 0.8 else 'info'
                self._send_notification(title, message, severity)
                
        except Exception as e:
            self.logger.error(f"Error sending predictive notification: {e}")
    
    def notify_learning_insight(self, insight_type: str, data: Dict[str, Any]):
        """Send notification for AI learning insights."""
        try:
            if not self.learning_notifications:
                return
            
            insight_messages = {
                'usage_pattern': 'AI has learned your system usage patterns',
                'optimization_success': 'AI has identified successful optimization patterns',
                'issue_correlation': 'AI has found correlations between system issues',
                'performance_baseline': 'AI has established new performance baselines'
            }
            
            if insight_type in insight_messages:
                title = f"🧠 AI Learning Insight"
                message = insight_messages[insight_type]
                
                if 'details' in data:
                    message += f"\n\n{data['details']}"
                
                self._send_notification(title, message, 'info')
                
        except Exception as e:
            self.logger.error(f"Error sending learning insight: {e}")
    
    def notify_anticheat_detection(self, detected_anticheats: List[str]):
        """Send notification about detected anti-cheat systems."""
        try:
            if not detected_anticheats:
                return
            
            anticheat_names = {
                'vac': 'Valve Anti-Cheat (Steam/CS2)',
                'vanguard': 'Riot Vanguard (Valorant)',
                'battleye': 'BattlEye',
                'easyanticheat': 'Easy Anti-Cheat'
            }
            
            detected_names = [anticheat_names.get(ac, ac.title()) for ac in detected_anticheats]
            
            if len(detected_names) == 1:
                title = f"🛡️ Anti-Cheat Detected: {detected_names[0]}"
                message = "Optimization system is now running in safe mode for anti-cheat compatibility"
            else:
                title = f"🛡️ {len(detected_names)} Anti-Cheat Systems Detected"
                message = f"Detected: {', '.join(detected_names)}\n\nOptimization system is now running in safe mode"
            
            message += "\n\nOnly safe, anti-cheat compatible optimizations will be applied."
            
            self._send_notification(title, message, 'info')
            
        except Exception as e:
            self.logger.error(f"Error sending anti-cheat detection notification: {e}")
    
    def notify_optimization_completed(self, optimization_results: Dict[str, bool]):
        """Send notification when optimizations are completed."""
        try:
            successful = sum(1 for result in optimization_results.values() if result)
            total = len(optimization_results)
            failed = total - successful
            
            if total == 0:
                return
            
            if successful == total:
                title = f"✅ All {total} Optimization{'s' if total != 1 else ''} Applied Successfully"
                message = "All optimizations were applied successfully. Your system performance should be improved."
                severity = 'info'
            elif successful > 0:
                title = f"⚠️ {successful}/{total} Optimizations Applied"
                message = f"{successful} optimizations applied successfully, {failed} failed."
                severity = 'warning'
            else:
                title = f"❌ Optimization Failed"
                message = f"All {total} optimizations failed to apply. Check system permissions and try again."
                severity = 'warning'
            
            # Add details about what was optimized
            if successful > 0:
                successful_optimizations = [name for name, result in optimization_results.items() if result]
                if len(successful_optimizations) <= 3:
                    message += f"\n\nApplied: {', '.join(successful_optimizations)}"
                else:
                    message += f"\n\nApplied {len(successful_optimizations)} optimizations including: {', '.join(successful_optimizations[:2])}, and others"
            
            self._send_notification(title, message, severity)
            
        except Exception as e:
            self.logger.error(f"Error sending optimization completion notification: {e}")
    
    def notify_system_monitoring_status(self, status: str, details: Dict[str, Any] = None):
        """Send notification about system monitoring status."""
        try:
            status_messages = {
                'monitoring_started': ('🚀 AI System Monitoring Active', 'Continuous performance analysis started'),
                'monitoring_stopped': ('🛑 AI System Monitoring Stopped', 'Performance analysis has been stopped'),
                'analysis_completed': ('📊 System Analysis Completed', 'Comprehensive system analysis finished'),
                'learning_updated': ('🧠 AI Learning Data Updated', 'System has learned from recent performance data'),
                'baseline_established': ('📈 Performance Baseline Established', 'AI has created new performance benchmarks')
            }
            
            if status in status_messages:
                title, base_message = status_messages[status]
                message = base_message
                
                if details:
                    if 'duration' in details:
                        message += f"\nDuration: {details['duration']:.1f} seconds"
                    if 'issues_found' in details:
                        message += f"\nIssues found: {details['issues_found']}"
                    if 'optimizations_available' in details:
                        message += f"\nOptimizations available: {details['optimizations_available']}"
                
                self._send_notification(title, message, 'info')
                
        except Exception as e:
            self.logger.error(f"Error sending monitoring status notification: {e}")
    
    def configure_ai_notifications(self, config: Dict[str, Any]):
        """Configure AI-specific notification settings."""
        try:
            if 'ai_notifications_enabled' in config:
                self.ai_notifications_enabled = config['ai_notifications_enabled']
            
            if 'analysis_notifications' in config:
                self.analysis_notifications = config['analysis_notifications']
            
            if 'predictive_notifications' in config:
                self.predictive_notifications = config['predictive_notifications']
            
            if 'learning_notifications' in config:
                self.learning_notifications = config['learning_notifications']
            
            # Also configure base notification settings
            self.configure_notifications(config)
            
            self.logger.info(f"AI notification configuration updated: {config}")
            
        except Exception as e:
            self.logger.error(f"Error configuring AI notifications: {e}")
    
    def get_ai_notification_stats(self) -> Dict[str, Any]:
        """Get AI-specific notification statistics."""
        try:
            base_stats = self.get_notification_stats()
            
            # Count AI-related notifications
            ai_notifications = 0
            analysis_notifications = 0
            predictive_notifications = 0
            
            for notification in self.notification_history:
                title = notification.get('title', '')
                if any(indicator in title for indicator in ['AI', '🔮', '🧠', '📊', '🛡️']):
                    ai_notifications += 1
                
                if 'Analysis' in title or '📊' in title:
                    analysis_notifications += 1
                
                if '🔮' in title:
                    predictive_notifications += 1
            
            ai_stats = {
                'ai_notifications': ai_notifications,
                'analysis_notifications': analysis_notifications,
                'predictive_notifications': predictive_notifications,
                'ai_settings': {
                    'ai_notifications_enabled': self.ai_notifications_enabled,
                    'analysis_notifications': self.analysis_notifications,
                    'predictive_notifications': self.predictive_notifications,
                    'learning_notifications': self.learning_notifications
                }
            }
            
            # Merge with base stats
            base_stats.update(ai_stats)
            return base_stats
            
        except Exception as e:
            self.logger.error(f"Error getting AI notification stats: {e}")
            return self.get_notification_stats()
    
    def test_ai_notifications(self):
        """Test AI-specific notifications."""
        try:
            test_analysis_result = {
                'analysis_summary': {
                    'total_issues': 3,
                    'critical_issues': 1,
                    'warning_issues': 2,
                    'gaming_affecting_issues': 2,
                    'overall_health_score': 75,
                    'performance_impact_level': 'medium',
                    'total_recommendations': 5,
                    'auto_applicable_recommendations': 3
                },
                'issues': {
                    'test_cpu_issue': {
                        'category': 'cpu',
                        'severity': 'critical',
                        'title': 'Test High CPU Usage',
                        'description': 'This is a test critical CPU issue',
                        'impact': 'May cause frame drops',
                        'auto_fixable': True,
                        'affects_gaming': True
                    }
                },
                'recommendations': {
                    'test_optimization': {
                        'priority': 9,
                        'title': 'Test High Priority Optimization',
                        'auto_applicable': True
                    }
                }
            }
            
            self.logger.info("Testing AI notifications...")
            
            # Test analysis results notification
            self.notify_ai_analysis_results(test_analysis_result)
            time.sleep(2)
            
            # Test predictive notification
            self.notify_predictive_issue('cpu_bottleneck', 0.85, 'Test predictive issue')
            time.sleep(2)
            
            # Test anti-cheat detection
            self.notify_anticheat_detection(['vac', 'vanguard'])
            time.sleep(2)
            
            # Test optimization completion
            self.notify_optimization_completed({'test_opt1': True, 'test_opt2': False})
            
            self.logger.info("AI notification tests completed")
            
        except Exception as e:
            self.logger.error(f"AI notification test failed: {e}")