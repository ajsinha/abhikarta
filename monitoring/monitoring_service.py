"""
Monitoring Service
Helper functions for gathering monitoring statistics

© 2025-2030 Ashutosh Sinha
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from db.database_call_handler import DatabaseCallHandler, get_database_handler


class MonitoringService:
    """Service for gathering monitoring statistics"""

    def __init__(self, db_handler: DatabaseCallHandler = None):
        self.db_handler = db_handler or get_database_handler()

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
        today_count = self.db_handler.count_distinct_users_in_sessions(times['today'])
        week_count = self.db_handler.count_distinct_users_in_sessions(times['week_ago'])
        total_users = self.db_handler.count_total_users()

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db_handler.count_sessions_in_time_range(
                interval['start'], interval['end']
            )
            hourly_data.append({'time': interval['time'], 'count': count})

        # Active sessions
        active_sessions = self.db_handler.get_active_sessions_with_users(limit=10)

        # User statistics
        user_stats = self.db_handler.get_user_statistics(limit=10)

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
        today_count = self.db_handler.count_tool_nodes(times['today'])
        week_count = self.db_handler.count_tool_nodes(times['week_ago'])
        total_count = self.db_handler.count_tool_nodes()

        # Success rate (last 7 days)
        week_stats = self.db_handler.get_tool_success_stats(times['week_ago'])
        success_rate = 0
        if week_stats['total'] > 0:
            success_rate = (week_stats['success'] / week_stats['total']) * 100

        # Average execution time (mock for now - would need duration calculation)
        avg_time = "2.3s"

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db_handler.count_tool_nodes_in_time_range(
                interval['start'], interval['end']
            )
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
        today_count = self.db_handler.count_agent_nodes(times['today'])
        week_count = self.db_handler.count_agent_nodes(times['week_ago'])
        total_count = self.db_handler.count_agent_nodes()

        # Success rate (last 7 days)
        week_stats = self.db_handler.get_agent_success_stats(times['week_ago'])
        success_rate = 0
        if week_stats['total'] > 0:
            success_rate = (week_stats['success'] / week_stats['total']) * 100

        avg_time = "1.8s"

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            count = self.db_handler.count_agent_nodes_in_time_range(
                interval['start'], interval['end']
            )
            hourly_data.append({'time': interval['time'], 'count': count})

        # Per-agent statistics
        agent_stats = []
        try:
            from agents.agent_registry import AgentRegistry
            agent_registry = AgentRegistry()
            for agent in agent_registry.list_agents():
                # Count executions for this agent
                exec_stats = self.db_handler.get_agent_execution_stats(agent['agent_id'])

                agent_stats.append({
                    'agent_id': agent['agent_id'],
                    'enabled': agent.get('enabled', True),
                    'total': exec_stats['total'],
                    'success': exec_stats['success'],
                    'failed': exec_stats['failed'],
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
        today_count = self.db_handler.count_workflows_by_time(times['today'])
        week_count = self.db_handler.count_workflows_by_time(times['week_ago'])
        total_count = self.db_handler.get_workflow_count()

        # Success rate
        week_stats = self.db_handler.get_workflow_success_stats(times['week_ago'])
        success_rate = 0
        if week_stats['total'] > 0:
            success_rate = (week_stats['completed'] / week_stats['total']) * 100

        # Running count
        running_count = self.db_handler.get_workflow_count('running')

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            started = self.db_handler.count_workflows_started_in_time_range(
                interval['start'], interval['end']
            )
            completed = self.db_handler.count_workflows_completed_in_time_range(
                interval['start'], interval['end']
            )

            hourly_data.append({
                'time': interval['time'],
                'started': started,
                'completed': completed
            })

        # Per-DAG statistics
        dag_stats = self.db_handler.get_dag_statistics()

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
        plans_exist = self.db_handler.table_exists('plans')
        conversations_exist = self.db_handler.table_exists('planner_conversations')

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
        today_count = self.db_handler.count_plans(times['today'])
        week_count = self.db_handler.count_plans(times['week_ago'])
        total_count = self.db_handler.count_plans()

        # Approval rate
        week_stats = self.db_handler.get_plan_approval_stats(times['week_ago'])
        approval_rate = 0
        if week_stats['total'] > 0:
            approval_rate = (week_stats['approved'] / week_stats['total']) * 100

        # Conversations today
        conversations_today = 0
        if conversations_exist:
            conversations_today = self.db_handler.count_planner_conversations(times['today'])

        # Pending approval
        pending_approval = self.db_handler.count_plans_by_status('pending_approval')

        # Hourly data
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            plans = self.db_handler.count_plans_in_time_range(
                interval['start'], interval['end']
            )

            conversations = 0
            if conversations_exist:
                conversations = self.db_handler.count_planner_conversations_in_time_range(
                    interval['start'], interval['end']
                )

            hourly_data.append({
                'time': interval['time'],
                'plans': plans,
                'conversations': conversations
            })

        # Status distribution
        status_distribution = self.db_handler.get_plan_status_distribution()

        # Top users
        top_users = self.db_handler.get_top_plan_users(limit=5)

        # Recent plans
        recent_plans = self.db_handler.get_recent_plans_with_users(limit=10)

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
        time_24h_ago = (datetime.now() - timedelta(hours=24)).isoformat()
        active_users = self.db_handler.count_active_users_in_last_24h(time_24h_ago)

        # Workflows today
        workflows_today = self.db_handler.count_workflows_by_time(times['today'])

        # Agent executions today
        agent_executions_today = self.db_handler.count_agent_nodes(times['today'])

        # Pending HITL
        pending_hitl = self.db_handler.count_pending_hitl_requests()

        # Recent activity
        recent_activity = self.db_handler.get_recent_activity(limit=10)

        return {
            'active_users': active_users,
            'workflows_today': workflows_today,
            'agent_executions_today': agent_executions_today,
            'pending_hitl': pending_hitl,
            'recent_activity': recent_activity
        }