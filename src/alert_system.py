"""
Sistema de Alertas para Monitoramento do Modelo

Envia notificações quando métricas ultrapassam thresholds definidos.
Suporta múltiplos canais: logs, Slack, email.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


# Diretórios
ROOT_DIR = Path(__file__).parent.parent
MONITORING_DIR = ROOT_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)

# Configurações
ALERT_CONFIG = MONITORING_DIR / "alert_config.json"
ALERT_HISTORY = MONITORING_DIR / "alert_history.json"


@dataclass
class AlertThresholds:
    """Thresholds para disparo de alertas."""
    mae_threshold: float = 2.0           # MAE máximo aceitável
    mape_threshold: float = 5.0          # MAPE máximo (%)
    drift_mean_pct: float = 10.0         # Mudança de média (%)
    drift_std_pct: float = 20.0          # Mudança de desvio (%)
    error_rate_threshold: float = 0.05   # Taxa de erro máxima (5%)


class AlertSystem:
    """
    Sistema de alertas para monitoramento do modelo.
    
    Funcionalidades:
    - Define thresholds para métricas
    - Detecta violações de thresholds
    - Envia alertas via múltiplos canais
    - Mantém histórico de alertas
    """
    
    def __init__(self, thresholds: AlertThresholds = None):
        """
        Inicializa o sistema de alertas.
        
        Args:
            thresholds: Thresholds personalizados (usa defaults se None)
        """
        self.thresholds = thresholds or AlertThresholds()
        self.config = self._load_config()
        self.history = self._load_history()
    
    def _load_config(self) -> Dict:
        """
        Carrega configurações de alertas.
        
        Returns:
            Dicionário com configurações
        """
        if ALERT_CONFIG.exists():
            with open(ALERT_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Configuração padrão
        default_config = {
            "slack_webhook_url": None,  # Configurar manualmente
            "email_config": {
                "smtp_server": None,
                "smtp_port": 587,
                "sender_email": None,
                "receiver_emails": [],
                "password": None
            },
            "enable_slack": False,
            "enable_email": False,
            "enable_logs": True
        }
        
        with open(ALERT_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _load_history(self) -> Dict:
        """
        Carrega histórico de alertas.
        
        Returns:
            Dicionário com histórico
        """
        if ALERT_HISTORY.exists():
            with open(ALERT_HISTORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"alerts": []}
    
    def _save_history(self):
        """Salva histórico de alertas."""
        with open(ALERT_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def check_performance_metrics(self, metrics: Dict) -> List[str]:
        """
        Verifica se métricas de performance violam thresholds.
        
        Args:
            metrics: Dicionário com métricas (mae, mape, etc.)
        
        Returns:
            Lista de violações detectadas
        """
        violations = []
        
        # Verifica MAE
        if "mae" in metrics:
            if metrics["mae"] > self.thresholds.mae_threshold:
                violations.append(
                    f"MAE alto: {metrics['mae']:.4f} > {self.thresholds.mae_threshold}"
                )
        
        # Verifica MAPE
        if "mape" in metrics:
            if metrics["mape"] > self.thresholds.mape_threshold:
                violations.append(
                    f"MAPE alto: {metrics['mape']:.2f}% > {self.thresholds.mape_threshold}%"
                )
        
        return violations
    
    def check_drift_metrics(self, drift_report: Dict) -> List[str]:
        """
        Verifica se drift report indica problemas.
        
        Args:
            drift_report: Relatório de drift
        
        Returns:
            Lista de violações detectadas
        """
        violations = []
        
        if drift_report.get("drift_detected"):
            alerts = drift_report.get("alerts", [])
            violations.extend([f"Drift: {alert}" for alert in alerts])
        
        return violations
    
    def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "WARNING",
        metadata: Dict = None
    ):
        """
        Envia alerta através dos canais configurados.
        
        Args:
            alert_type: Tipo do alerta (performance, drift, error)
            message: Mensagem do alerta
            severity: Severidade (INFO, WARNING, CRITICAL)
            metadata: Dados adicionais
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "metadata": metadata or {}
        }
        
        # Adiciona ao histórico
        self.history["alerts"].append(alert)
        self._save_history()
        
        # Envia via diferentes canais
        if self.config.get("enable_logs", True):
            self._send_log_alert(alert)
        
        if self.config.get("enable_slack") and self.config.get("slack_webhook_url"):
            self._send_slack_alert(alert)
        
        if self.config.get("enable_email") and self.config["email_config"].get("sender_email"):
            self._send_email_alert(alert)
    
    def _send_log_alert(self, alert: Dict):
        """
        Registra alerta nos logs.
        
        Args:
            alert: Dicionário com informações do alerta
        """
        severity_symbol = {
            "INFO": "ℹ️ ",
            "WARNING": "⚠️ ",
            "CRITICAL": "🚨"
        }.get(alert["severity"], "📢")
        
        print(f"\n{'='*60}")
        print(f"{severity_symbol} ALERTA: {alert['type'].upper()}")
        print(f"{'='*60}")
        print(f"Severidade: {alert['severity']}")
        print(f"Timestamp:  {alert['timestamp']}")
        print(f"Mensagem:   {alert['message']}")
        if alert["metadata"]:
            print(f"Detalhes:   {json.dumps(alert['metadata'], indent=2)}")
        print(f"{'='*60}\n")
    
    def _send_slack_alert(self, alert: Dict):
        """
        Envia alerta para Slack via webhook.
        
        Args:
            alert: Dicionário com informações do alerta
        """
        webhook_url = self.config.get("slack_webhook_url")
        if not webhook_url:
            return
        
        # Emoji baseado em severidade
        emoji = {
            "INFO": ":information_source:",
            "WARNING": ":warning:",
            "CRITICAL": ":rotating_light:"
        }.get(alert["severity"], ":bell:")
        
        # Monta payload do Slack
        payload = {
            "text": f"{emoji} *{alert['type'].upper()} Alert*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} {alert['type'].upper()} Alert"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{alert['severity']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:*\n{alert['timestamp']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:*\n{alert['message']}"
                    }
                }
            ]
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Alerta enviado para Slack")
            else:
                print(f"❌ Erro ao enviar para Slack: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Erro ao enviar para Slack: {e}")
    
    def _send_email_alert(self, alert: Dict):
        """
        Envia alerta por email (implementação básica).
        
        Args:
            alert: Dicionário com informações do alerta
        """
        # Nota: Implementação completa requer biblioteca smtplib
        # Aqui apenas um placeholder
        print(f"📧 Email alert (não implementado): {alert['message']}")
        
        # Para implementar:
        # import smtplib
        # from email.mime.text import MIMEText
        # Configurar SMTP e enviar
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """
        Retorna alertas recentes.
        
        Args:
            hours: Horas para filtrar
        
        Returns:
            Lista de alertas
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            alert for alert in self.history["alerts"]
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
        
        return recent
    
    def get_alert_summary(self) -> Dict:
        """
        Retorna resumo de alertas.
        
        Returns:
            Resumo estatístico
        """
        total = len(self.history["alerts"])
        
        if total == 0:
            return {"total_alerts": 0}
        
        # Conta por tipo
        by_type = {}
        by_severity = {}
        
        for alert in self.history["alerts"]:
            alert_type = alert["type"]
            severity = alert["severity"]
            
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_alerts": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "last_alert": self.history["alerts"][-1] if total > 0 else None
        }


def configure_slack_webhook(webhook_url: str):
    """
    Configura webhook do Slack para alertas.
    
    Args:
        webhook_url: URL do webhook do Slack
    """
    if ALERT_CONFIG.exists():
        with open(ALERT_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    config["slack_webhook_url"] = webhook_url
    config["enable_slack"] = True
    
    with open(ALERT_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Slack webhook configurado!")


def main():
    """Função principal para testes."""
    print("\n🔔 Sistema de Alertas B3SA3")
    print("="*60)
    
    alert_system = AlertSystem()
    
    # Exemplo de alerta
    alert_system.send_alert(
        alert_type="test",
        message="Sistema de alertas funcionando!",
        severity="INFO",
        metadata={"test_mode": True}
    )
    
    # Mostra resumo
    summary = alert_system.get_alert_summary()
    print(f"\n📊 Resumo de Alertas:")
    print(f"   Total: {summary['total_alerts']}")
    print(f"   Por tipo: {summary.get('by_type', {})}")
    print(f"   Por severidade: {summary.get('by_severity', {})}")


if __name__ == "__main__":
    main()
