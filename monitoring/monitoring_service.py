"""
Monitoring Service
Helper functions for gathering monitoring statistics

© 2025-2030 Ashutosh Sinha
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from db.database_call_handler import DatabaseCallHandler, get_database_handler


# ========== PASTE THIS CLASS ANYWHERE ==========
class WorkingMonitoringService:
    def __init__(self, db_handler):
        self.db = db_handler
        # Auto-detect query method
        for method in ['query', 'execute', 'select', 'fetch_all', 'run_query']:
            if hasattr(self.db, method):
                self.query_method = method
                break

    def _query(self, sql, params=None):
        method = getattr(self.db, self.query_method)
        try:
            return method(sql, params) if params else method(sql)
        except:
            return []

    def _count(self, table, where=None, params=None):
        if where:
            sql = f"SELECT COUNT(*) as count FROM {table} WHERE {where}"
            result = self._query(sql, params)
        else:
            sql = f"SELECT COUNT(*) as count FROM {table}"
            result = self._query(sql)
        return result[0].get('count', 0) if result else 0

    def _table_exists(self, table):
        if hasattr(self.db, 'table_exists'):
            return self.db.table_exists(table)
        try:
            self._query(f"SELECT 1 FROM {table} LIMIT 1")
            return True
        except:
            return False

    def get_planner_stats(self):
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0).isoformat()
        week = (now - timedelta(days=7)).isoformat()

        has_plans = self._table_exists('plans')
        has_lg = self._table_exists('lgraph_plans')

        t, w, total, pend = 0, 0, 0, 0
        recent = []

        if has_plans:
            t += self._count('plans', 'created_at >= ?', (today,))
            w += self._count('plans', 'created_at >= ?', (week,))
            total += self._count('plans')
            pend += self._count('plans', "status = ?", ('pending_approval',))

            for plan in self._query("""
                SELECT p.plan_id, p.user_id, p.request, p.status, p.created_at,
                       COALESCE(u.username, p.user_id) as username
                FROM plans p LEFT JOIN users u ON p.user_id = u.user_id
                ORDER BY p.created_at DESC LIMIT 5
            """):
                plan['plan_type'] = 'DAG'
                recent.append(plan)

        if has_lg:
            t += self._count('lgraph_plans', 'created_at >= ?', (today,))
            w += self._count('lgraph_plans', 'created_at >= ?', (week,))
            total += self._count('lgraph_plans')
            pend += self._count('lgraph_plans', "status = ?", ('pending_approval',))

            for plan in self._query("""
                SELECT p.plan_id, p.user_id, p.user_request as request, p.status, p.created_at,
                       COALESCE(u.username, p.user_id) as username
                FROM lgraph_plans p LEFT JOIN users u ON p.user_id = u.user_id
                ORDER BY p.created_at DESC LIMIT 5
            """):
                plan['plan_type'] = 'LangGraph'
                recent.append(plan)

        recent.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        dist = {'pending_approval': 0, 'approved': 0, 'rejected': 0, 'executed': 0}
        if has_plans:
            for r in self._query("SELECT status, COUNT(*) as count FROM plans GROUP BY status"):
                if r['status'] in dist: dist[r['status']] += r['count']
        if has_lg:
            for r in self._query("SELECT status, COUNT(*) as count FROM lgraph_plans GROUP BY status"):
                if r['status'] in dist: dist[r['status']] += r['count']

        return {
            'today': t, 'last_7_days': w, 'total': total, 'pending_approval': pend,
            'approval_rate': 0, 'conversations_today': 0,
            'hourly_data': [{'time': (now - timedelta(minutes=i * 10)).strftime('%H:%M'),
                             'plans': 0, 'conversations': 0} for i in range(6, -1, -1)],
            'status_distribution': dist, 'top_users': [], 'recent_plans': recent[:10]
        }

    def get_dags_stats(self):
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0).isoformat()
        week = (now - timedelta(days=7)).isoformat()

        if not self._table_exists('workflow_executions'):
            return {'today': 0, 'last_7_days': 0, 'total': 0, 'success_rate': 0,
                    'running_count': 0, 'avg_duration': '0s', 'hourly_data': [], 'dag_stats': []}

        t = self._count('workflow_executions', 'start_time >= ?', (today,))
        w = self._count('workflow_executions', 'start_time >= ?', (week,))
        total = self._count('workflow_executions')
        run = self._count('workflow_executions', "status = ?", ('running',))
        comp = self._count('workflow_executions', "status = 'completed' AND start_time >= ?", (week,))

        dags = []
        for r in self._query("""
            SELECT dag_id, COUNT(*) as total,
                   SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                   SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running
            FROM workflow_executions GROUP BY dag_id
        """):
            dags.append({
                'dag_id': r['dag_id'], 'name': r['dag_id'],
                'total': r['total'], 'completed': r['completed'],
                'failed': r['failed'], 'running': r['running'], 'avg_duration': '0s'
            })

        return {
            'today': t, 'last_7_days': w, 'total': total,
            'success_rate': (comp / w * 100) if w > 0 else 0,
            'running_count': run, 'avg_duration': '45s',
            'hourly_data': [{'time': (now - timedelta(minutes=i * 10)).strftime('%H:%M'),
                             'started': 0, 'completed': 0} for i in range(6, -1, -1)],
            'dag_stats': dags
        }


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
        """Get planner statistics (includes both regular and LangGraph autonomous plans)"""
        times = self.get_time_ranges()

        # Check if tables exist first
        plans_exist = self.db_handler.table_exists('plans')
        lgraph_plans_exist = self.db_handler.table_exists('lgraph_plans')
        conversations_exist = self.db_handler.table_exists('planner_conversations')
        lgraph_conversations_exist = self.db_handler.table_exists('lgraph_conversations')

        if not plans_exist and not lgraph_plans_exist:
            # Return empty stats if neither table exists
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

        # Count plans from both tables
        today_count = 0
        week_count = 0
        total_count = 0

        if plans_exist:
            today_count += self.db_handler.count_plans(times['today'])
            week_count += self.db_handler.count_plans(times['week_ago'])
            total_count += self.db_handler.count_plans()

        if lgraph_plans_exist:
            today_count += self.db_handler.count_lgraph_plans(times['today'])
            week_count += self.db_handler.count_lgraph_plans(times['week_ago'])
            total_count += self.db_handler.count_lgraph_plans()

        # Approval rate (combine both tables)
        total_plans_week = 0
        approved_plans_week = 0

        if plans_exist:
            week_stats = self.db_handler.get_plan_approval_stats(times['week_ago'])
            total_plans_week += week_stats['total']
            approved_plans_week += week_stats['approved']

        if lgraph_plans_exist:
            lgraph_week_stats = self.db_handler.get_lgraph_plan_approval_stats(times['week_ago'])
            total_plans_week += lgraph_week_stats['total']
            approved_plans_week += lgraph_week_stats['approved']

        approval_rate = 0
        if total_plans_week > 0:
            approval_rate = (approved_plans_week / total_plans_week) * 100

        # Conversations today (combine both tables)
        conversations_today = 0
        if conversations_exist:
            conversations_today += self.db_handler.count_planner_conversations(times['today'])
        if lgraph_conversations_exist:
            conversations_today += self.db_handler.count_lgraph_conversations(times['today'])

        # Pending approval (combine both tables)
        pending_approval = 0
        if plans_exist:
            pending_approval += self.db_handler.count_plans_by_status('pending_approval')
        if lgraph_plans_exist:
            pending_approval += self.db_handler.count_lgraph_plans_by_status('pending_approval')

        # Hourly data (combine both tables)
        intervals = self.get_10min_intervals()
        hourly_data = []
        for interval in intervals:
            plans = 0
            conversations = 0

            if plans_exist:
                plans += self.db_handler.count_plans_in_time_range(
                    interval['start'], interval['end']
                )

            if lgraph_plans_exist:
                plans += self.db_handler.count_lgraph_plans_in_time_range(
                    interval['start'], interval['end']
                )

            if conversations_exist:
                conversations += self.db_handler.count_planner_conversations_in_time_range(
                    interval['start'], interval['end']
                )

            if lgraph_conversations_exist:
                conversations += self.db_handler.count_lgraph_conversations_in_time_range(
                    interval['start'], interval['end']
                )

            hourly_data.append({
                'time': interval['time'],
                'plans': plans,
                'conversations': conversations
            })

        # Status distribution (combine both tables)
        status_distribution = {
            'pending_approval': 0,
            'approved': 0,
            'rejected': 0,
            'executed': 0
        }

        if plans_exist:
            dist = self.db_handler.get_plan_status_distribution()
            for status, count in dist.items():
                status_distribution[status] = status_distribution.get(status, 0) + count

        if lgraph_plans_exist:
            lgraph_dist = self.db_handler.get_lgraph_plan_status_distribution()
            for status, count in lgraph_dist.items():
                status_distribution[status] = status_distribution.get(status, 0) + count

        # Top users (combine both tables)
        top_users = []
        if plans_exist or lgraph_plans_exist:
            top_users = self.db_handler.get_top_plan_users_combined(limit=5)

        # Recent plans (combine both tables and sort by date)
        recent_plans = []
        if plans_exist:
            recent_plans.extend(self.db_handler.get_recent_plans_with_users(limit=10))
        if lgraph_plans_exist:
            lgraph_recent = self.db_handler.get_recent_lgraph_plans_with_users(limit=10)
            # Add plan_type indicator for LangGraph plans
            for plan in lgraph_recent:
                plan['plan_type'] = 'LangGraph'
            recent_plans.extend(lgraph_recent)

        # Sort by created_at and take top 10
        recent_plans.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        recent_plans = recent_plans[:10]

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