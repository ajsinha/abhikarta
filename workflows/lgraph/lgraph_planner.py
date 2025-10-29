"""
LangGraph-based Planner
Advanced autonomous workflow planning using LangGraph with supervisor pattern

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal, TypedDict
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from db.database import get_db
from llm.llm_facade import LLMFacade
from agents.agent_registry import AgentRegistry
from tools.tool_registry import ToolRegistry
from workflows.dag.dag_registry import DAGRegistry


class PlanType(str, Enum):
    """Type of plan to execute"""
    USE_EXISTING_DAG = "use_existing_dag"
    CREATE_STATEGRAPH = "create_stategraph"
    SIMPLE_EXECUTION = "simple_execution"


class ExecutionMode(str, Enum):
    """Execution mode for tasks"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class WorkflowState(TypedDict):
    """State for the LangGraph workflow"""
    # Input
    user_request: str
    user_id: str
    session_id: str
    
    # Planning
    plan_type: Optional[PlanType]
    selected_dag_id: Optional[str]
    task_breakdown: List[Dict[str, Any]]
    execution_plan: Dict[str, Any]
    requires_hitl: bool
    hitl_checkpoints: List[str]
    
    # Execution
    current_step: int
    completed_steps: List[str]
    step_results: Dict[str, Any]
    parallel_branches: Dict[str, List[Dict[str, Any]]]
    loop_state: Dict[str, Any]
    
    # Status
    status: str
    error: Optional[str]
    plan_id: str
    workflow_id: Optional[str]
    
    # Context
    available_agents: List[Dict[str, Any]]
    available_tools: List[Dict[str, Any]]
    available_dags: List[Dict[str, Any]]
    messages: List[BaseMessage]
    
    # Approval
    pending_approval: bool
    approval_granted: bool


class LangGraphPlanner:
    """
    Advanced autonomous planner using LangGraph with supervisor pattern.
    
    Features:
    - Autonomous planning with supervisor agent
    - Dynamic StateGraph construction
    - Support for parallel execution, loops, and conditionals
    - Integration with existing DAGs
    - Human-in-the-loop support
    - Fine-grained state management
    """
    
    def __init__(self, llm_provider: str = 'anthropic'):
        self.llm = LLMFacade(provider=llm_provider)
        self.db = get_db()
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        self.dag_registry = DAGRegistry()
        
        # Build the supervisor graph
        self.supervisor_graph = self._build_supervisor_graph()
    
    def _build_supervisor_graph(self) -> StateGraph:
        """Build the supervisor workflow graph"""
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("evaluate_resources", self._evaluate_resources)
        workflow.add_node("decide_strategy", self._decide_strategy)
        workflow.add_node("construct_plan", self._construct_plan)
        workflow.add_node("request_approval", self._request_approval)
        workflow.add_node("execute_plan", self._execute_plan)
        workflow.add_node("handle_hitl", self._handle_hitl)
        workflow.add_node("finalize", self._finalize)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        # Add edges
        workflow.add_edge("analyze_request", "evaluate_resources")
        workflow.add_edge("evaluate_resources", "decide_strategy")
        workflow.add_edge("decide_strategy", "construct_plan")
        workflow.add_edge("construct_plan", "request_approval")
        
        # Conditional edge after approval
        workflow.add_conditional_edges(
            "request_approval",
            self._check_approval,
            {
                "approved": "execute_plan",
                "rejected": END,
                "waiting": END
            }
        )
        
        # Conditional edge after execution
        workflow.add_conditional_edges(
            "execute_plan",
            self._check_hitl_needed,
            {
                "hitl_needed": "handle_hitl",
                "continue": "execute_plan",
                "complete": "finalize"
            }
        )
        
        workflow.add_edge("handle_hitl", END)
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _analyze_request(self, state: WorkflowState) -> WorkflowState:
        """Analyze user request to understand intent and requirements"""
        
        user_request = state["user_request"]
        
        # Create analysis prompt
        prompt = f"""Analyze this user request and extract key information:
Request: "{user_request}"

Provide a JSON response with:
1. "intent": What the user wants to accomplish
2. "complexity": "simple", "moderate", or "complex"
3. "requires_hitl": boolean - whether human approval might be needed
4. "key_requirements": list of main requirements
5. "suggested_approach": brief description of how to approach this

Respond ONLY with valid JSON."""

        response = self.llm.generate(prompt)
        
        try:
            analysis = json.loads(response)
        except:
            # Fallback analysis
            analysis = {
                "intent": user_request,
                "complexity": "moderate",
                "requires_hitl": False,
                "key_requirements": [user_request],
                "suggested_approach": "Sequential execution"
            }
        
        # Update state
        state["requires_hitl"] = analysis.get("requires_hitl", False)
        state["messages"].append(AIMessage(content=f"Analysis: {json.dumps(analysis, indent=2)}"))
        
        # Store analysis in state for later use
        state["execution_plan"] = {"analysis": analysis}
        
        return state
    
    def _evaluate_resources(self, state: WorkflowState) -> WorkflowState:
        """Evaluate available agents, tools, and DAGs"""
        
        # Get available resources
        agents = self.agent_registry.list_agents()
        tools = self.tool_registry.list_tools()
        dags = self.dag_registry.list_dags()
        
        state["available_agents"] = agents
        state["available_tools"] = tools
        state["available_dags"] = dags
        
        # Create summary
        summary = {
            "agent_count": len(agents),
            "tool_count": len(tools),
            "dag_count": len(dags),
            "agents": [a.get("agent_id") for a in agents],
            "tools": [t.get("tool_name") for t in tools],
            "dags": [d.get("dag_id") for d in dags]
        }
        
        state["messages"].append(AIMessage(
            content=f"Available resources: {json.dumps(summary, indent=2)}"
        ))
        
        return state
    
    def _decide_strategy(self, state: WorkflowState) -> WorkflowState:
        """Decide on execution strategy: use existing DAG or create new StateGraph"""
        
        user_request = state["user_request"]
        available_dags = state["available_dags"]
        analysis = state["execution_plan"].get("analysis", {})
        
        # Create decision prompt
        dag_descriptions = "\n".join([
            f"- {dag['dag_id']}: {dag.get('description', 'No description')} ({dag.get('node_count', 0)} nodes)"
            for dag in available_dags
        ])
        
        prompt = f"""Based on this user request, decide the best execution strategy:

User Request: "{user_request}"
Request Complexity: {analysis.get('complexity', 'moderate')}
Key Requirements: {', '.join(analysis.get('key_requirements', []))}

Available DAGs:
{dag_descriptions if dag_descriptions else "No pre-defined DAGs available"}

Available Agents: {', '.join([a['agent_id'] for a in state['available_agents']])}
Available Tools: {', '.join([t['tool_name'] for t in state['available_tools']])}

Decide the best strategy and respond with JSON:
{{
  "strategy": "use_existing_dag" or "create_stategraph" or "simple_execution",
  "reasoning": "Why this strategy is best",
  "selected_dag_id": "dag_id" (if using existing DAG, otherwise null),
  "execution_mode": "sequential" or "parallel" or "conditional" or "loop",
  "estimated_steps": number
}}

Respond ONLY with valid JSON."""

        response = self.llm.generate(prompt)
        
        try:
            decision = json.loads(response)
        except:
            # Fallback decision
            decision = {
                "strategy": "create_stategraph",
                "reasoning": "Creating custom StateGraph for flexible execution",
                "selected_dag_id": None,
                "execution_mode": "sequential",
                "estimated_steps": 3
            }
        
        # Update state
        state["plan_type"] = PlanType(decision["strategy"])
        state["selected_dag_id"] = decision.get("selected_dag_id")
        state["execution_plan"]["strategy"] = decision
        
        state["messages"].append(AIMessage(
            content=f"Strategy Decision: {json.dumps(decision, indent=2)}"
        ))
        
        return state
    
    def _construct_plan(self, state: WorkflowState) -> WorkflowState:
        """Construct detailed execution plan"""
        
        plan_type = state["plan_type"]
        user_request = state["user_request"]
        
        if plan_type == PlanType.USE_EXISTING_DAG:
            return self._construct_dag_plan(state)
        else:
            return self._construct_stategraph_plan(state)
    
    def _construct_dag_plan(self, state: WorkflowState) -> WorkflowState:
        """Construct plan from existing DAG"""
        
        dag_id = state["selected_dag_id"]
        dag_config = self.dag_registry.get_dag_config(dag_id)
        
        if not dag_config:
            state["error"] = f"DAG {dag_id} not found"
            state["plan_type"] = PlanType.CREATE_STATEGRAPH
            return self._construct_stategraph_plan(state)
        
        # Convert DAG to execution plan
        execution_plan = {
            "type": "dag",
            "dag_id": dag_id,
            "dag_config": dag_config,
            "steps": []
        }
        
        # Build step list from DAG nodes
        for node in dag_config.get("nodes", []):
            step = {
                "step_id": node["node_id"],
                "type": node["node_type"],
                "agent_id": node.get("agent_id"),
                "config": node.get("config", {}),
                "dependencies": node.get("dependencies", [])
            }
            execution_plan["steps"].append(step)
        
        state["execution_plan"]["details"] = execution_plan
        state["task_breakdown"] = execution_plan["steps"]
        
        state["messages"].append(AIMessage(
            content=f"Using existing DAG: {dag_id} with {len(execution_plan['steps'])} steps"
        ))
        
        return state
    
    def _construct_stategraph_plan(self, state: WorkflowState) -> WorkflowState:
        """Construct dynamic StateGraph plan"""
        
        user_request = state["user_request"]
        strategy = state["execution_plan"].get("strategy", {})
        execution_mode = strategy.get("execution_mode", "sequential")
        
        available_agents = [a["agent_id"] for a in state["available_agents"]]
        available_tools = [t["tool_name"] for t in state["available_tools"]]
        
        # Create detailed planning prompt
        prompt = f"""Create a detailed execution plan for this request:

Request: "{user_request}"
Execution Mode: {execution_mode}

Available Agents: {', '.join(available_agents)}
Available Tools: {', '.join(available_tools)}

Create a JSON execution plan with these requirements:
1. Break down into concrete, executable steps
2. Specify which agent or tool to use for each step
3. For parallel mode: identify steps that can run in parallel
4. For loop mode: specify loop conditions and iterations
5. For conditional mode: specify conditions and branches
6. Include any human-in-the-loop checkpoints if needed

Response format:
{{
  "type": "stategraph",
  "execution_mode": "{execution_mode}",
  "steps": [
    {{
      "step_id": "step_1",
      "name": "Step name",
      "type": "agent" or "tool",
      "agent_id": "agent_id" or "tool_name": "tool_name",
      "input": {{}},
      "dependencies": [],
      "parallel_group": null or "group_name",
      "conditional": null or {{"condition": "...", "branches": [...]}}
    }}
  ],
  "parallel_groups": {{}},
  "hitl_checkpoints": [],
  "loop_config": null or {{"max_iterations": 5, "condition": "..."}}
}}

Respond ONLY with valid JSON."""

        response = self.llm.generate(prompt)
        
        try:
            execution_plan = json.loads(response)
        except:
            # Fallback plan
            execution_plan = {
                "type": "stategraph",
                "execution_mode": execution_mode,
                "steps": [
                    {
                        "step_id": "step_1",
                        "name": "Execute request",
                        "type": "agent",
                        "agent_id": available_agents[0] if available_agents else "echo_agent",
                        "input": {"request": user_request},
                        "dependencies": []
                    }
                ],
                "parallel_groups": {},
                "hitl_checkpoints": [],
                "loop_config": None
            }
        
        # Update state
        state["execution_plan"]["details"] = execution_plan
        state["task_breakdown"] = execution_plan["steps"]
        state["hitl_checkpoints"] = execution_plan.get("hitl_checkpoints", [])
        
        if execution_mode == "parallel":
            state["parallel_branches"] = execution_plan.get("parallel_groups", {})
        
        if execution_mode == "loop":
            state["loop_state"] = execution_plan.get("loop_config", {})
        
        state["messages"].append(AIMessage(
            content=f"Created StateGraph plan with {len(execution_plan['steps'])} steps"
        ))
        
        return state
    
    def _request_approval(self, state: WorkflowState) -> WorkflowState:
        """Request user approval for the plan"""
        
        execution_plan = state["execution_plan"]["details"]
        
        # Generate human-readable plan summary
        summary = self._generate_plan_summary(execution_plan)
        
        # Save plan to database
        plan_id = f"lgraph_plan_{uuid.uuid4().hex[:8]}"
        state["plan_id"] = plan_id
        
        self.db.insert('lgraph_plans', {
            'plan_id': plan_id,
            'user_id': state["user_id"],
            'session_id': state["session_id"],
            'user_request': state["user_request"],
            'plan_type': state["plan_type"].value,
            'execution_plan': json.dumps(execution_plan),
            'plan_summary': summary,
            'status': 'pending_approval',
            'created_at': datetime.now().isoformat()
        })
        
        state["pending_approval"] = True
        state["status"] = "pending_approval"
        
        state["messages"].append(AIMessage(
            content=f"Plan created (ID: {plan_id}). Summary:\n{summary}\n\nPlease approve to execute."
        ))
        
        return state
    
    def _check_approval(self, state: WorkflowState) -> Literal["approved", "rejected", "waiting"]:
        """Check if plan is approved"""
        
        if state.get("approval_granted"):
            return "approved"
        elif state.get("error"):
            return "rejected"
        else:
            return "waiting"
    
    def _execute_plan(self, state: WorkflowState) -> WorkflowState:
        """Execute the approved plan"""
        
        execution_plan = state["execution_plan"]["details"]
        plan_type = state["plan_type"]
        
        # Create workflow execution record
        if not state.get("workflow_id"):
            workflow_id = str(uuid.uuid4())
            state["workflow_id"] = workflow_id
            
            self.db.insert('lgraph_workflows', {
                'workflow_id': workflow_id,
                'plan_id': state["plan_id"],
                'user_id': state["user_id"],
                'session_id': state["session_id"],
                'status': 'running',
                'started_at': datetime.now().isoformat()
            })
        
        # Execute based on plan type
        if plan_type == PlanType.USE_EXISTING_DAG:
            state = self._execute_dag_plan(state)
        else:
            state = self._execute_stategraph_plan(state)
        
        return state
    
    def _execute_dag_plan(self, state: WorkflowState) -> WorkflowState:
        """Execute plan using existing DAG orchestrator"""
        
        from workflows.dag.orchestrator import WorkflowOrchestrator
        
        dag_id = state["selected_dag_id"]
        graph = self.dag_registry.create_graph_from_dag(dag_id)
        
        if not graph:
            state["error"] = f"Failed to create graph from DAG {dag_id}"
            state["status"] = "failed"
            return state
        
        # Use existing orchestrator
        orchestrator = WorkflowOrchestrator()
        workflow_id = orchestrator.start_workflow(
            dag_id=dag_id,
            session_id=state["session_id"],
            user_id=state["user_id"],
            graph=graph
        )
        
        state["workflow_id"] = workflow_id
        state["status"] = "running_dag"
        
        state["messages"].append(AIMessage(
            content=f"Started DAG execution (workflow: {workflow_id})"
        ))
        
        return state
    
    def _execute_stategraph_plan(self, state: WorkflowState) -> WorkflowState:
        """Execute dynamically constructed StateGraph plan"""
        
        execution_plan = state["execution_plan"]["details"]
        execution_mode = execution_plan.get("execution_mode", "sequential")
        steps = execution_plan.get("steps", [])
        
        current_step = state.get("current_step", 0)
        completed_steps = state.get("completed_steps", [])
        step_results = state.get("step_results", {})
        
        if execution_mode == "parallel":
            state = self._execute_parallel_steps(state, steps)
        elif execution_mode == "loop":
            state = self._execute_loop_steps(state, steps)
        elif execution_mode == "conditional":
            state = self._execute_conditional_steps(state, steps)
        else:  # sequential
            state = self._execute_sequential_steps(state, steps)
        
        return state
    
    def _execute_sequential_steps(self, state: WorkflowState, steps: List[Dict]) -> WorkflowState:
        """Execute steps sequentially"""
        
        current_step = state.get("current_step", 0)
        completed_steps = state.get("completed_steps", [])
        step_results = state.get("step_results", {})
        
        # Execute next ready step
        for i, step in enumerate(steps):
            step_id = step["step_id"]
            
            if step_id in completed_steps:
                continue
            
            # Check dependencies
            dependencies = step.get("dependencies", [])
            if all(dep in completed_steps for dep in dependencies):
                # Execute this step
                result = self._execute_step(step, step_results)
                
                step_results[step_id] = result
                completed_steps.append(step_id)
                
                # Log execution
                self._log_step_execution(state["workflow_id"], step_id, result)
                
                state["current_step"] = i + 1
                state["completed_steps"] = completed_steps
                state["step_results"] = step_results
                
                # Check if more steps remain
                if len(completed_steps) < len(steps):
                    state["status"] = "running"
                else:
                    state["status"] = "completed"
                
                break
        else:
            # No more steps to execute
            state["status"] = "completed"
        
        return state
    
    def _execute_parallel_steps(self, state: WorkflowState, steps: List[Dict]) -> WorkflowState:
        """Execute steps in parallel groups"""
        
        parallel_groups = state.get("parallel_branches", {})
        completed_steps = state.get("completed_steps", [])
        step_results = state.get("step_results", {})
        
        # Group steps by parallel group
        for step in steps:
            step_id = step["step_id"]
            
            if step_id in completed_steps:
                continue
            
            # Check if dependencies are met
            dependencies = step.get("dependencies", [])
            if all(dep in completed_steps for dep in dependencies):
                # Execute step
                result = self._execute_step(step, step_results)
                
                step_results[step_id] = result
                completed_steps.append(step_id)
                
                self._log_step_execution(state["workflow_id"], step_id, result)
        
        state["completed_steps"] = completed_steps
        state["step_results"] = step_results
        
        # Check completion
        if len(completed_steps) >= len(steps):
            state["status"] = "completed"
        else:
            state["status"] = "running"
        
        return state
    
    def _execute_loop_steps(self, state: WorkflowState, steps: List[Dict]) -> WorkflowState:
        """Execute steps with looping"""
        
        loop_state = state.get("loop_state", {})
        max_iterations = loop_state.get("max_iterations", 5)
        current_iteration = loop_state.get("current_iteration", 0)
        
        if current_iteration >= max_iterations:
            state["status"] = "completed"
            return state
        
        # Execute all steps in loop
        state = self._execute_sequential_steps(state, steps)
        
        # Increment iteration
        loop_state["current_iteration"] = current_iteration + 1
        state["loop_state"] = loop_state
        
        # Check loop condition (simplified - would evaluate actual condition in production)
        if state.get("status") == "completed":
            # Reset for next iteration
            state["completed_steps"] = []
            state["current_step"] = 0
            state["status"] = "running"
        
        return state
    
    def _execute_conditional_steps(self, state: WorkflowState, steps: List[Dict]) -> WorkflowState:
        """Execute steps with conditional branching"""
        
        # Similar to sequential but evaluates conditions at branch points
        state = self._execute_sequential_steps(state, steps)
        
        # In production, would evaluate conditions and route accordingly
        return state
    
    def _execute_step(self, step: Dict, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step"""
        
        step_type = step.get("type")
        
        try:
            if step_type == "agent":
                agent_id = step.get("agent_id")
                input_data = step.get("input", {})
                
                # Merge previous results if needed
                if step.get("use_previous_result"):
                    deps = step.get("dependencies", [])
                    for dep in deps:
                        if dep in previous_results:
                            input_data["previous_result"] = previous_results[dep]
                
                result = self.agent_registry.execute_agent(agent_id, input_data)
                
            elif step_type == "tool":
                tool_name = step.get("tool_name")
                input_data = step.get("input", {})
                
                result = self.tool_registry.execute_tool(tool_name, **input_data)
                
            else:
                result = {
                    "success": False,
                    "error": f"Unknown step type: {step_type}"
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_hitl_needed(self, state: WorkflowState) -> Literal["hitl_needed", "continue", "complete"]:
        """Check if human-in-the-loop is needed"""
        
        hitl_checkpoints = state.get("hitl_checkpoints", [])
        completed_steps = state.get("completed_steps", [])
        
        # Check if we're at a HITL checkpoint
        for checkpoint in hitl_checkpoints:
            if checkpoint in completed_steps and f"{checkpoint}_hitl_approved" not in completed_steps:
                return "hitl_needed"
        
        # Check if execution is complete
        execution_plan = state["execution_plan"]["details"]
        steps = execution_plan.get("steps", [])
        
        if state.get("status") == "completed":
            return "complete"
        elif len(completed_steps) < len(steps):
            return "continue"
        else:
            return "complete"
    
    def _handle_hitl(self, state: WorkflowState) -> WorkflowState:
        """Handle human-in-the-loop checkpoint"""
        
        # Create HITL request
        hitl_id = str(uuid.uuid4())
        
        self.db.insert('lgraph_hitl_requests', {
            'hitl_id': hitl_id,
            'workflow_id': state["workflow_id"],
            'plan_id': state["plan_id"],
            'checkpoint': state["completed_steps"][-1],
            'message': f"Review results at checkpoint {state['completed_steps'][-1]}",
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        })
        
        state["status"] = "waiting_hitl"
        state["messages"].append(AIMessage(
            content=f"Human review required (HITL ID: {hitl_id})"
        ))
        
        return state
    
    def _finalize(self, state: WorkflowState) -> WorkflowState:
        """Finalize workflow execution"""
        
        workflow_id = state.get("workflow_id")
        
        if workflow_id:
            self.db.update(
                'lgraph_workflows',
                {
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'results': json.dumps(state["step_results"])
                },
                'workflow_id = ?',
                (workflow_id,)
            )
        
        state["status"] = "completed"
        state["messages"].append(AIMessage(
            content="Workflow completed successfully!"
        ))
        
        return state
    
    def _generate_plan_summary(self, execution_plan: Dict) -> str:
        """Generate human-readable plan summary"""
        
        plan_type = execution_plan.get("type")
        steps = execution_plan.get("steps", [])
        
        summary = f"Plan Type: {plan_type}\n"
        summary += f"Total Steps: {len(steps)}\n"
        summary += f"Execution Mode: {execution_plan.get('execution_mode', 'sequential')}\n\n"
        summary += "Steps:\n"
        
        for i, step in enumerate(steps, 1):
            step_name = step.get("name", step.get("step_id"))
            step_type = step.get("type")
            resource = step.get("agent_id") or step.get("tool_name")
            
            summary += f"{i}. {step_name} ({step_type}: {resource})\n"
            
            if step.get("dependencies"):
                summary += f"   Dependencies: {', '.join(step['dependencies'])}\n"
        
        if execution_plan.get("hitl_checkpoints"):
            summary += f"\nHITL Checkpoints: {', '.join(execution_plan['hitl_checkpoints'])}\n"
        
        return summary
    
    def _log_step_execution(self, workflow_id: str, step_id: str, result: Dict) -> None:
        """Log step execution"""
        
        self.db.insert('lgraph_step_logs', {
            'workflow_id': workflow_id,
            'step_id': step_id,
            'result': json.dumps(result),
            'success': result.get('success', False),
            'executed_at': datetime.now().isoformat()
        })
    
    # Public API methods
    
    def create_plan(self, user_id: str, session_id: str, user_request: str) -> Dict[str, Any]:
        """
        Create a plan from user request
        
        Args:
            user_id: User ID
            session_id: Session ID
            user_request: Natural language request
            
        Returns:
            Dictionary with plan details and status
        """
        
        # Initialize state
        initial_state: WorkflowState = {
            "user_request": user_request,
            "user_id": user_id,
            "session_id": session_id,
            "plan_type": None,
            "selected_dag_id": None,
            "task_breakdown": [],
            "execution_plan": {},
            "requires_hitl": False,
            "hitl_checkpoints": [],
            "current_step": 0,
            "completed_steps": [],
            "step_results": {},
            "parallel_branches": {},
            "loop_state": {},
            "status": "planning",
            "error": None,
            "plan_id": "",
            "workflow_id": None,
            "available_agents": [],
            "available_tools": [],
            "available_dags": [],
            "messages": [HumanMessage(content=user_request)],
            "pending_approval": False,
            "approval_granted": False
        }
        
        # Run supervisor graph until approval needed
        result = self.supervisor_graph.invoke(initial_state)
        
        return {
            "plan_id": result["plan_id"],
            "plan_type": result["plan_type"].value if result["plan_type"] else None,
            "status": result["status"],
            "execution_plan": result["execution_plan"],
            "task_breakdown": result["task_breakdown"],
            "requires_hitl": result["requires_hitl"],
            "messages": [msg.content for msg in result["messages"]],
            "pending_approval": result["pending_approval"]
        }
    
    def approve_plan(self, plan_id: str, user_id: str) -> Dict[str, Any]:
        """Approve a plan for execution"""
        
        # Update plan status
        self.db.update(
            'lgraph_plans',
            {
                'status': 'approved',
                'approved_at': datetime.now().isoformat(),
                'approved_by': user_id
            },
            'plan_id = ?',
            (plan_id,)
        )
        
        # Get plan details
        plan = self.db.fetchone(
            "SELECT * FROM lgraph_plans WHERE plan_id = ?",
            (plan_id,)
        )
        
        if not plan:
            return {"success": False, "error": "Plan not found"}
        
        # Reconstruct state for execution
        execution_state: WorkflowState = {
            "user_request": plan["user_request"],
            "user_id": plan["user_id"],
            "session_id": plan["session_id"],
            "plan_type": PlanType(plan["plan_type"]),
            "selected_dag_id": None,
            "task_breakdown": [],
            "execution_plan": json.loads(plan["execution_plan"]),
            "requires_hitl": False,
            "hitl_checkpoints": [],
            "current_step": 0,
            "completed_steps": [],
            "step_results": {},
            "parallel_branches": {},
            "loop_state": {},
            "status": "approved",
            "error": None,
            "plan_id": plan_id,
            "workflow_id": None,
            "available_agents": [],
            "available_tools": [],
            "available_dags": [],
            "messages": [],
            "pending_approval": False,
            "approval_granted": True
        }
        
        # Start execution
        result = self._execute_plan(execution_state)
        
        return {
            "success": True,
            "workflow_id": result.get("workflow_id"),
            "status": result["status"],
            "message": "Plan execution started"
        }
    
    def reject_plan(self, plan_id: str, user_id: str, reason: str = "") -> bool:
        """Reject a plan"""
        
        self.db.update(
            'lgraph_plans',
            {
                'status': 'rejected',
                'rejected_at': datetime.now().isoformat(),
                'rejected_by': user_id,
                'rejection_reason': reason
            },
            'plan_id = ?',
            (plan_id,)
        )
        
        return True
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan details"""
        
        plan = self.db.fetchone(
            "SELECT * FROM lgraph_plans WHERE plan_id = ?",
            (plan_id,)
        )
        
        if plan:
            return {
                "plan_id": plan["plan_id"],
                "user_id": plan["user_id"],
                "user_request": plan["user_request"],
                "plan_type": plan["plan_type"],
                "execution_plan": json.loads(plan["execution_plan"]),
                "plan_summary": plan["plan_summary"],
                "status": plan["status"],
                "created_at": plan["created_at"]
            }
        
        return None
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status"""
        
        workflow = self.db.fetchone(
            "SELECT * FROM lgraph_workflows WHERE workflow_id = ?",
            (workflow_id,)
        )
        
        if not workflow:
            return None
        
        # Get step logs
        steps = self.db.fetchall(
            "SELECT * FROM lgraph_step_logs WHERE workflow_id = ? ORDER BY executed_at",
            (workflow_id,)
        )
        
        return {
            "workflow_id": workflow["workflow_id"],
            "plan_id": workflow["plan_id"],
            "status": workflow["status"],
            "started_at": workflow["started_at"],
            "completed_at": workflow.get("completed_at"),
            "steps": steps,
            "results": json.loads(workflow.get("results", "{}")) if workflow.get("results") else {}
        }
    
    def approve_hitl(self, hitl_id: str, user_id: str, response: str = "approved") -> bool:
        """Approve HITL checkpoint"""
        
        self.db.update(
            'lgraph_hitl_requests',
            {
                'status': 'approved',
                'responded_at': datetime.now().isoformat(),
                'responded_by': user_id,
                'response': response
            },
            'hitl_id = ?',
            (hitl_id,)
        )
        
        # Resume workflow execution
        # In production, would trigger continuation of the workflow
        
        return True
    
    def reject_hitl(self, hitl_id: str, user_id: str, reason: str = "") -> bool:
        """Reject HITL checkpoint"""
        
        self.db.update(
            'lgraph_hitl_requests',
            {
                'status': 'rejected',
                'responded_at': datetime.now().isoformat(),
                'responded_by': user_id,
                'response': reason
            },
            'hitl_id = ?',
            (hitl_id,)
        )
        
        # Mark workflow as failed
        request = self.db.fetchone(
            "SELECT * FROM lgraph_hitl_requests WHERE hitl_id = ?",
            (hitl_id,)
        )
        
        if request:
            self.db.update(
                'lgraph_workflows',
                {
                    'status': 'failed',
                    'completed_at': datetime.now().isoformat(),
                    'error': f'HITL rejected: {reason}'
                },
                'workflow_id = ?',
                (request["workflow_id"],)
            )
        
        return True


def initialize_lgraph_tables():
    """Initialize database tables for LangGraph planner"""
    
    db = get_db()
    
    # LangGraph plans table
    db.execute("""
        CREATE TABLE IF NOT EXISTS lgraph_plans (
            plan_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_request TEXT,
            plan_type TEXT,
            execution_plan TEXT,
            plan_summary TEXT,
            status TEXT DEFAULT 'pending_approval',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            approved_by TEXT,
            rejected_at TEXT,
            rejected_by TEXT,
            rejection_reason TEXT
        )
    """)
    
    # LangGraph workflows table
    db.execute("""
        CREATE TABLE IF NOT EXISTS lgraph_workflows (
            workflow_id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            results TEXT,
            error TEXT,
            FOREIGN KEY (plan_id) REFERENCES lgraph_plans(plan_id)
        )
    """)
    
    # LangGraph step logs table
    db.execute("""
        CREATE TABLE IF NOT EXISTS lgraph_step_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            result TEXT,
            success BOOLEAN,
            executed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES lgraph_workflows(workflow_id)
        )
    """)
    
    # LangGraph HITL requests table
    db.execute("""
        CREATE TABLE IF NOT EXISTS lgraph_hitl_requests (
            hitl_id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            checkpoint TEXT,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            responded_at TEXT,
            responded_by TEXT,
            response TEXT,
            FOREIGN KEY (workflow_id) REFERENCES lgraph_workflows(workflow_id)
        )
    """)
    
    print("LangGraph planner tables initialized successfully")
