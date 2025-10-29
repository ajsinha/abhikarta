"""
Monitoring Service
Helper functions for gathering monitoring statistics

© 2025-2030 Ashutosh Sinha
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from core.database import get_db


class MonitoringService:
    """Service for gathering monitoring statistics"""

    def __init__(self):
        self.db = get_db()

    def get_time_ranges(self):
        """Get time range strings for queries"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        hour_ago = now - timedelta(hours=1)

        return {
            'today': today_start.isoformat(),
            'week_ago': week_ago.isoformat(),
            'hour_ago': hour_ago.isoformat(),
            'now': now.isoformat()
        }

    def get_10min_intervals(self):
        """Get list of 10-minute intervals for last hour"""
        now = datetime.now()
        intervals = []

        for i in range(6, -1, -1):  # 6 intervals ago to now
            time = now - timedelta(minutes=i * 10)
            time_str = time.strftime('%H:%M')
            intervals.append({
                'time': time_str,
                'start': (time - timedelta(minutes=10)).isoformat(),
                'end': time.isoformat()
            })

        return intervals

    # ========== USER MONITORING ==========

    def get_user_stats(self) -> Dict[str, Any]:
        """Get user activity statistics"""
        times = self.get_time_ranges()

        # Count users/sessions by time period
        today_count = self.db.fetchone(
            "SELECT COUNT(DISTINCT user_id) as count FROM sessions WHERE created_at >= ?",
            (times['today'],)
        )['count'] or 0

        week_count = self.db.fetchone(
            "SELECT COUNT(DISTINCT user_id) as count FROM sessions WHERE created_at >= ?",
            (times['week_ago'],)
        )['count'] or 0

        total_users = self.db.fetchone(
            "SELECT COUNT(*) as count FROM users"
        )['count'] or 0

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db.fetchone(
                "SELECT COUNT(*) as count FROM sessions WHERE created_at >= ? AND created_at < ?",
                (interval['start'], interval['end'])
            )['count'] or 0
            hourly_data.append({'time': interval['time'], 'count': count})

        # Active sessions
        active_sessions = self.db.fetchall("""
            SELECT s.*, u.username 
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.status = 'active'
            ORDER BY s.updated_at DESC
            LIMIT 10
        """)

        # User statistics
        user_stats = self.db.fetchall("""
            SELECT 
                u.username,
                u.role,
                u.last_login,
                (SELECT COUNT(*) FROM sessions WHERE user_id = u.user_id) as session_count,
                (SELECT COUNT(*) FROM workflows WHERE created_by = u.user_id) as workflow_count
            FROM users u
            ORDER BY workflow_count DESC
            LIMIT 10
        """)

        return {
            'today': today_count,
            'last_7_days': week_count,
            'total': total_users,
            'hourly_data': hourly_data,
            'active_sessions': active_sessions,
            'user_stats': user_stats
        }

    # ========== TOOLS MONITORING ==========

    def get_tools_stats(self) -> Dict[str, Any]:
        """Get tools execution statistics"""
        times = self.get_time_ranges()

        # Count tool executions
        today_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'tool' AND started_at >= ?
        """, (times['today'],))['count'] or 0

        week_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'tool' AND started_at >= ?
        """, (times['week_ago'],))['count'] or 0

        total_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'tool'
        """)['count'] or 0

        # Success rate (last 7 days)
        week_stats = self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success
            FROM workflow_nodes
            WHERE node_type = 'tool' AND started_at >= ?
        """, (times['week_ago'],))

        success_rate = 0
        if week_stats and week_stats['total'] > 0:
            success_rate = (week_stats['success'] / week_stats['total']) * 100

        # Average execution time (mock for now - would need duration calculation)
        avg_time = "2.3s"

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db.fetchone("""
                SELECT COUNT(*) as count FROM workflow_nodes 
                WHERE node_type = 'tool' AND started_at >= ? AND started_at < ?
            """, (interval['start'], interval['end']))['count'] or 0
            hourly_data.append({'time': interval['time'], 'count': count})

        # Per-tool statistics
        tool_stats = []
        try:
            from tools.tool_registry import ToolRegistry
            tool_registry = ToolRegistry()
            for tool in tool_registry.list_tools():
                tool_stats.append({
                    'tool_name': tool['tool_name'],
                    'enabled': tool.get('enabled', True),
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'avg_duration': '0s'
                })
        except:
            pass

        return {
            'today': today_count,
            'last_7_days': week_count,
            'total': total_count,
            'success_rate': success_rate,
            'avg_time': avg_time,
            'hourly_data': hourly_data,
            'tool_stats': tool_stats
        }

    # ========== AGENTS MONITORING ==========

    def get_agents_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        times = self.get_time_ranges()

        # Count agent executions
        today_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'agent' AND started_at >= ?
        """, (times['today'],))['count'] or 0

        week_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'agent' AND started_at >= ?
        """, (times['week_ago'],))['count'] or 0

        total_count = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'agent'
        """)['count'] or 0

        # Success rate (last 7 days)
        week_stats = self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success
            FROM workflow_nodes
            WHERE node_type = 'agent' AND started_at >= ?
        """, (times['week_ago'],))

        success_rate = 0
        if week_stats and week_stats['total'] > 0:
            success_rate = (week_stats['success'] / week_stats['total']) * 100

        avg_time = "1.8s"

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db.fetchone("""
                SELECT COUNT(*) as count FROM workflow_nodes 
                WHERE node_type = 'agent' AND started_at >= ? AND started_at < ?
            """, (interval['start'], interval['end']))['count'] or 0
            hourly_data.append({'time': interval['time'], 'count': count})

        # Per-agent statistics
        agent_stats = []
        try:
            from agents.agent_registry import AgentRegistry
            agent_registry = AgentRegistry()
            for agent in agent_registry.list_agents():
                # Count executions for this agent
                exec_stats = self.db.fetchone("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                    FROM workflow_nodes
                    WHERE node_type = 'agent' AND agent_id = ?
                """, (agent['agent_id'],))

                agent_stats.append({
                    'agent_id': agent['agent_id'],
                    'enabled': agent.get('enabled', True),
                    'total': exec_stats['total'] or 0,
                    'success': exec_stats['success'] or 0,
                    'failed': exec_stats['failed'] or 0,
                    'avg_duration': '0s'
                })
        except:
            pass

        return {
            'today': today_count,
            'last_7_days': week_count,
            'total': total_count,
            'success_rate': success_rate,
            'avg_time': avg_time,
            'hourly_data': hourly_data,
            'agent_stats': agent_stats
        }

    # ========== DAGS MONITORING ==========

    def get_dags_stats(self) -> Dict[str, Any]:
        """Get workflow/DAG execution statistics"""
        times = self.get_time_ranges()

        # Count workflows
        today_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM workflows WHERE created_at >= ?",
            (times['today'],)
        )['count'] or 0

        week_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM workflows WHERE created_at >= ?",
            (times['week_ago'],)
        )['count'] or 0

        total_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM workflows"
        )['count'] or 0

        # Success rate
        week_stats = self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM workflows
            WHERE created_at >= ?
        """, (times['week_ago'],))

        success_rate = 0
        if week_stats and week_stats['total'] > 0:
            success_rate = (week_stats['completed'] / week_stats['total']) * 100

        # Running count
        running_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM workflows WHERE status = 'running'"
        )['count'] or 0

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            started = self.db.fetchone(
                "SELECT COUNT(*) as count FROM workflows WHERE started_at >= ? AND started_at < ?",
                (interval['start'], interval['end'])
            )['count'] or 0

            completed = self.db.fetchone(
                "SELECT COUNT(*) as count FROM workflows WHERE completed_at >= ? AND completed_at < ?",
                (interval['start'], interval['end'])
            )['count'] or 0

            hourly_data.append({
                'time': interval['time'],
                'started': started,
                'completed': completed
            })

        # Per-DAG statistics
        dag_stats = self.db.fetchall("""
            SELECT 
                dag_id,
                name,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running
            FROM workflows
            GROUP BY dag_id, name
            ORDER BY total DESC
        """)

        for dag in dag_stats:
            dag['avg_duration'] = '0s'  # Would calculate from started_at/completed_at

        return {
            'today': today_count,
            'last_7_days': week_count,
            'total': total_count,
            'success_rate': success_rate,
            'running_count': running_count,
            'avg_duration': '45s',
            'hourly_data': hourly_data,
            'dag_stats': dag_stats
        }

    # ========== PLANNER MONITORING ==========

    def get_planner_stats(self) -> Dict[str, Any]:
        """Get planner statistics"""
        times = self.get_time_ranges()

        # Check if tables exist first
        plans_exist = self._table_exists('plans')
        conversations_exist = self._table_exists('planner_conversations')

        if not plans_exist:
            # Return empty stats if table doesn't exist
            return {
                'today': 0,
                'last_7_days': 0,
                'total': 0,
                'approval_rate': 0,
                'conversations_today': 0,
                'pending_approval': 0,
                'hourly_data': [{'time': interval['time'], 'plans': 0, 'conversations': 0}
                                for interval in self.get_10min_intervals()],
                'status_distribution': {
                    'pending_approval': 0,
                    'approved': 0,
                    'rejected': 0,
                    'executed': 0
                },
                'top_users': [],
                'recent_plans': []
            }

        # Count plans
        today_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM plans WHERE created_at >= ?",
            (times['today'],)
        )['count'] or 0

        week_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM plans WHERE created_at >= ?",
            (times['week_ago'],)
        )['count'] or 0

        total_count = self.db.fetchone(
            "SELECT COUNT(*) as count FROM plans"
        )['count'] or 0

        # Approval rate
        week_stats = self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
            FROM plans
            WHERE created_at >= ?
        """, (times['week_ago'],))

        approval_rate = 0
        if week_stats and week_stats['total'] > 0:
            approval_rate = (week_stats['approved'] / week_stats['total']) * 100

        # Conversations today
        conversations_today = 0
        if conversations_exist:
            conversations_today = self.db.fetchone(
                "SELECT COUNT(*) as count FROM planner_conversations WHERE created_at >= ?",
                (times['today'],)
            )['count'] or 0

        # Pending approval
        pending_approval = self.db.fetchone(
            "SELECT COUNT(*) as count FROM plans WHERE status = 'pending_approval'"
        )['count'] or 0

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            plans = self.db.fetchone(
                "SELECT COUNT(*) as count FROM plans WHERE created_at >= ? AND created_at < ?",
                (interval['start'], interval['end'])
            )['count'] or 0

            conversations = 0
            if conversations_exist:
                conversations = self.db.fetchone(
                    "SELECT COUNT(*) as count FROM planner_conversations WHERE created_at >= ? AND created_at < ?",
                    (interval['start'], interval['end'])
                )['count'] or 0

            hourly_data.append({
                'time': interval['time'],
                'plans': plans,
                'conversations': conversations
            })

        # Status distribution
        status_distribution = {
            'pending_approval':
                self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'pending_approval'")['count'] or 0,
            'approved': self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'approved'")['count'] or 0,
            'rejected': self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'rejected'")['count'] or 0,
            'executed': self.db.fetchone("SELECT COUNT(*) as count FROM plans WHERE status = 'executed'")['count'] or 0
        }

        # Top users
        top_users = self.db.fetchall("""
            SELECT 
                u.username,
                (SELECT COUNT(*) FROM plans WHERE user_id = u.user_id) as plan_count,
                0 as conversation_count
            FROM users u
            WHERE (SELECT COUNT(*) FROM plans WHERE user_id = u.user_id) > 0
            ORDER BY plan_count DESC
            LIMIT 5
        """)

        # Recent plans
        recent_plans = self.db.fetchall("""
            SELECT p.*, u.username
            FROM plans p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.created_at DESC
            LIMIT 10
        """)

        return {
            'today': today_count,
            'last_7_days': week_count,
            'total': total_count,
            'approval_rate': approval_rate,
            'conversations_today': conversations_today,
            'pending_approval': pending_approval,
            'hourly_data': hourly_data,
            'status_distribution': status_distribution,
            'top_users': top_users,
            'recent_plans': recent_plans
        }

    # ========== DASHBOARD STATS ==========

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard overview statistics"""
        times = self.get_time_ranges()

        # Active users (last 24 hours)
        active_users = self.db.fetchone(
            "SELECT COUNT(DISTINCT user_id) as count FROM sessions WHERE updated_at >= ?",
            ((datetime.now() - timedelta(hours=24)).isoformat(),)
        )['count'] or 0

        # Workflows today
        workflows_today = self.db.fetchone(
            "SELECT COUNT(*) as count FROM workflows WHERE created_at >= ?",
            (times['today'],)
        )['count'] or 0

        # Agent executions today
        agent_executions_today = self.db.fetchone("""
            SELECT COUNT(*) as count FROM workflow_nodes 
            WHERE node_type = 'agent' AND started_at >= ?
        """, (times['today'],))['count'] or 0

        # Pending HITL
        pending_hitl = self.db.fetchone(
            "SELECT COUNT(*) as count FROM hitl_requests WHERE status = 'pending'"
        )['count'] or 0

        # Recent activity
        recent_activity = self.db.fetchall("""
            SELECT 
                'workflow' as type,
                'primary' as type_color,
                'Workflow started: ' || COALESCE(name, 'Unnamed') as event,
                created_by as user,
                created_at as time
            FROM workflows
            ORDER BY created_at DESC
            LIMIT 10
        """)

        return {
            'active_users': active_users,
            'workflows_today': workflows_today,
            'agent_executions_today': agent_executions_today,
            'pending_hitl': pending_hitl,
            'recent_activity': recent_activity
        }

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            result = self.db.fetchone(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return result is not None
        except:
            return False