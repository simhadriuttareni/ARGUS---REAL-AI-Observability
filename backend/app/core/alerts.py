"""
ARGUS Alert Engine
Evaluates rules and triggers notifications
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import uuid

from ..models.alert import Alert, AlertRule, AlertStatus, AlertSeverity, AlertRuleType
from .monitoring import UptimeCheck


@dataclass
class AlertContext:
    rule: AlertRule
    check: UptimeCheck
    trigger_reason: str


class AlertEngine:
    """Evaluates alert rules and handles notifications"""
    
    def __init__(self):
        self.active_incidents: Dict[str, Alert] = {}
        self.notification_handlers = []
    
    async def evaluate(self, checks: List[UptimeCheck]):
        """Evaluate all checks against rules"""
        rules = await self.get_active_rules()
        
        for rule in rules:
            context = await self.check_rule(rule, checks)
            if context:
                await self.trigger_alert(context)
    
    async def check_rule(self, rule: AlertRule, checks: List[UptimeCheck]) -> Optional[AlertContext]:
        """Check if a single rule is triggered"""
        
        if rule.type == AlertRuleType.MODEL_DOWN.value:
            for check in checks:
                if check.model_name == rule.model and check.status == "down":
                    return AlertContext(
                        rule=rule,
                        check=check,
                        trigger_reason=f"Model {check.model_name} is down"
                    )
        
        elif rule.type == AlertRuleType.LATENCY_SPIKE.value:
            for check in checks:
                if check.latency_ms > rule.threshold:
                    return AlertContext(
                        rule=rule,
                        check=check,
                        trigger_reason=f"Latency {check.latency_ms:.0f}ms exceeds threshold {rule.threshold:.0f}ms"
                    )
        
        elif rule.type == AlertRuleType.COST_SPIKE.value:
            # Check if cost exceeds budget
            # Would calculate from trace data
            pass
        
        return None
    
    async def trigger_alert(self, context: AlertContext):
        """Trigger an alert and send notifications"""
        
        alert = Alert(
            id=str(uuid.uuid4()),
            rule_id=context.rule.id,
            rule_name=context.rule.name,
            model=context.check.model_name,
            provider=context.check.provider,
            severity=context.rule.severity,
            status=AlertStatus.ACTIVE.value,
            reason=context.trigger_reason,
            created_at=datetime.now(),
            extra={
                "latency_ms": context.check.latency_ms,
                "ttft_ms": context.check.ttft_ms,
                "tps": context.check.tps,
                "error": context.check.error
            }
        )
        
        self.active_incidents[alert.id] = alert
        
        # Send notifications
        await self.send_notifications(alert)
        
        print(f"🚨 ALERT: {alert.reason}")
    
    async def get_active_rules(self) -> List[AlertRule]:
        """Get all active alert rules"""
        # This would come from database in production
        return [
            AlertRule(
                id="rule-1",
                name="Model Down Alert",
                type=AlertRuleType.MODEL_DOWN.value,
                model="gpt-4o-mini",
                threshold=0,
                severity=AlertSeverity.CRITICAL.value,
                enabled=True
            ),
            AlertRule(
                id="rule-2",
                name="Latency Spike Alert",
                type=AlertRuleType.LATENCY_SPIKE.value,
                threshold=5000,  # 5 seconds
                severity=AlertSeverity.WARNING.value,
                enabled=True
            ),
        ]
    
    async def check_trace(self, trace):
        """Check a trace against alert rules"""
        # This would evaluate cost rules, etc.
        pass
    
    async def send_notifications(self, alert: Alert):
        """Send notifications via configured channels"""
        # Slack, Email, Webhook implementations
        print(f"📧 Notification: {alert.rule_name} - {alert.reason}")


# Singleton instance
alert_engine = AlertEngine()